# Interestingness & selection upgrades (real MP4 pipelines)

This plan is a living document and must be maintained in accordance with `.agents/PLANS.md`.

## Progress

- [x] (2026-01-18) Add real motion/activity timeseries (`feat.video_activity_timeseries@1.0.0`).
- [x] (2026-01-18) Add hook features (`feat.aggregate_candidate_hook_features@1.0.0`).
- [x] (2026-01-18) Add audio event timeseries (`feat.audio_event_timeseries@1.0.0`).
- [x] (2026-01-18) Add richer features (`feat.aggregate_candidate_features_v3@1.0.0`).
- [x] (2026-01-18) Add explicit scoring (`score.interestingness_v2@1.0.0`) + `CandidateScore` entity.
- [x] (2026-01-18) Add peak + hook-first candidate generators (`candidate.from_timeseries_peaks@1.0.0`, `candidate.hook_first_windows@1.0.0`) + merge (`candidate.merge_candidate_sets@1.0.0`).
- [x] (2026-01-18) Add explicit selection (`select.dpp_diverse_v2@1.0.0`) and selection report (`report.selection_debug@1.0.0`).
- [x] (2026-01-18) Wire into real pipelines (`configs/pipelines.yaml`) + update docs (`docs/guide/remix_factory_real_v1.md`).
- [ ] Add face metrics (`feat.face_metrics_opencv_dnn@1.0.0` or `feat.face_metrics_mediapipe@1.0.0`).
- [ ] Add semantic embeddings pipeline variant (`feat.shot_embeddings_clip@...`) + `WITH_SEMANTICS` scoring mode.

## Notes

Understood. The pipeline *works* end-to-end on MP4s now, but “interestingness” is currently mostly:

* **audio_rms_mean** (1s RMS averaged over the candidate window)
* **cut_rate_hz**
* and `motion_mean := cut_rate_hz` (a declared proxy)

That is shallow in a very specific way: it tends to select **loud / cutty**, not **compelling**. It misses:

* iconic but quiet moments,
* reaction shots,
* suspense build-ups,
* “something weird is happening” semantics,
* visual novelty,
* and TikTok‑specific requirements like **a strong first ~1–2 seconds**.

Below is a concrete, plugin‑modular plan to make selection materially better, without sneaking in “fallbacks” (i.e., hidden errors). I’ll include the minor things I called out previously, but the bulk is the scene selection upgrade.

---

# 1) First, restate the real problem in system terms

Today you have:

1. `segment.ffmpeg_scene_detect` → ShotBoundaries
2. `candidate.from_shots_windowed` → CandidateClip windows
3. `feat.ffmpeg_audio_rms_timeseries` + `feat.aggregate_candidate_features`
4. `select.dpp_diverse` (quality + diversity)

What’s missing is **a richer `FeatureVector`** and **a scoring policy** that aligns with “interesting clip” rather than “energetic clip”.

The right structure is:

* **Per‑movie timeseries features** (computed once)
* **Per‑shot semantic features** (computed once)
* **Per‑candidate aggregations** (cheap)
* **ScoringPolicy plugin** (explicitly chooses a scoring mode based on which features exist)
* **Selection plugin** (DPP/topK) consumes explicit scores + similarity vectors

No implicit “if this fails, do that”; any change in behavior is an explicit **decision event** (and ideally an entity) that records why.

---

# 2) Concrete “interestingness” feature set (what to add)

This set is chosen because it’s:

* robust across old films,
* mostly cheap,
* and correlates with human attention.

## 2.1 Real motion/activity (replace the cut-rate proxy)

Add a per-movie timeseries computed from the proxy video:

**Plugin:** `feat.video_activity_timeseries@1.0.0`
**Input:** `MovieArtifacts.proxy_ref`
**Output Artifact:** `activity_timeseries.json` with 1s windows:

```json
{
  "window_s": 1.0,
  "samples": [
    {"t":0, "mad": 3.2, "edge_density": 0.14, "luma_mean": 0.42},
    ...
  ]
}
```

* `mad`: mean absolute frame diff over sampled frames in that second (real motion proxy)
* `edge_density`: fraction of pixels above an edge threshold (helps distinguish “busy” frames vs flat title cards)
* `luma_mean`: helps detect fades / blackouts / blown whites

**Logging requirements**

* Emit a `decision_event` with:

  * sampling fps used
  * resize dimensions used
  * runtime stats (frames processed, seconds covered)

**Why this matters**
This gives you “movement” that isn’t just “many cuts”.

## 2.2 Hook quality (TikTok-specific)

Interestingness is front-loaded on TikTok. Add hook features computed on the *first N seconds* of each candidate.

**Plugin:** `feat.aggregate_candidate_hook_features@1.0.0`
**Input:** `CandidateClip` + `activity_timeseries` + `audio_rms_timeseries`
**Output:** fields like:

* `hook_motion_mean` (first 2s)
* `hook_audio_rms_mean` (first 2s)
* `hook_contrast` / `hook_edge_density`

And a derived `hook_score` (deterministically computed, weights in config).

**No hidden behavior:** if a candidate is shorter than hook window, emit an `ErrorEvent` `CANDIDATE_TOO_SHORT_FOR_HOOK_WINDOW` and mark candidate invalid for selection (explicitly).

## 2.3 Faces / closeups (reaction beats)

You can do this two ways; keep it modular:

### Option A (recommended): OpenCV DNN face detector (no big ML runtime)

**Plugin:** `feat.face_metrics_opencv_dnn@1.0.0`
**Output per-second timeseries**:

* `face_present` boolean
* `face_area_ratio_mean`
* `face_area_ratio_max`
* `face_count_mean`

### Option B: MediaPipe (often better when it works; more deps)

**Plugin:** `feat.face_metrics_mediapipe@1.0.0`
Same output schema, different implementation.

**Critical design point**
Do **not** have one plugin silently “try mediapipe then opencv”. That’s the hidden-error pattern you want to avoid.

Instead:

* Choose one plugin in the pipeline config.
* If it fails (e.g. missing deps), the run fails **unless** the remediation policy explicitly launches a different pipeline variant (that’s a separate run with a separate config hash and explicit remediation record).

## 2.4 Audio events (not just average loudness)

RMS average misses “a single impactful moment.” Add event-y features:

**Plugin:** `feat.audio_event_timeseries@1.0.0`
Compute per 1s window:

* `rms`
* `onset_rate` (spectral flux threshold crossings)
* `peak_rms` (max in subwindows)
* optional `speech_prob` (lightweight VAD)

Even on old movies, this helps surface screams, bursts, crowd moments, etc.

## 2.5 Semantic novelty (optional, but the biggest step up)

This is the difference between “busy” and “interesting”.

**Plugin:** `feat.shot_embeddings_clip@1.0.0`
**Input:** representative frame per shot (you already have shot boundaries)
**Output Artifact:** shot embedding matrix (e.g., float16) + shot_id map.

Then add:

**Plugin:** `feat.aggregate_candidate_embedding@1.0.0`

* candidate embedding = mean of its shot embeddings (or max similarity to prompt set)

And optionally:

**Plugin:** `feat.semantic_novelty_timeseries@1.0.0`

* novelty = distance between consecutive shot embeddings
* candidates that contain spikes in novelty get boosted

**Operational separation**
Provide two explicit pipelines:

* `*_no_gpu_v1` (no semantic embeddings)
* `*_gpu_v1` (CLIP embeddings enabled)

Do not auto-switch.

---

# 3) Replace “score = some shallow mix” with an explicit scoring policy plugin

Today, your selection quality is basically implied inside `select.dpp_diverse` based on whatever features happen to exist.

Make scoring an explicit, versioned, auditable stage.

## 3.1 New entity: ScoreBreakdown

Persist how a candidate’s score was computed.

**Entity:** `CandidateScore` (or `ScoreBreakdown`)

```json
{
  "candidate_id": "...",
  "scorer": {"name":"score.interestingness_v2", "version":"2.0.0"},
  "mode": "NO_SEMANTICS|WITH_SEMANTICS",
  "components": {
    "hook": 0.71,
    "motion": 0.42,
    "audio_events": 0.55,
    "faces": 0.63,
    "novelty": 0.12
  },
  "score": 0.58
}
```

## 3.2 Plugin: `score.interestingness_v2@1.0.0`

**Input:** CandidateClip + FeatureVector(s)
**Output:** CandidateScore list

**Config:**

* weights per component
* mode definitions (e.g. `WITH_SEMANTICS` includes novelty, prompt-sim, etc.)

**Key constraint**
If semantics are missing but the scorer is configured for `WITH_SEMANTICS`, that’s not something to “fall back” from.

Two correct options:

1. **Hard error**: `MISSING_REQUIRED_FEATURE: shot_embeddings_clip`
2. **Explicit mode switch**: only if config explicitly allows it:

   * emit a decision event `SCORING_MODE_SWITCH`
   * persist it
   * include it in the run snapshot
   * and increment a metric like `scoring_mode_switch_total`

That’s not hidden behavior; it is a declared algorithm branch.

---

# 4) Candidate generation should not be just “window shots and pray”

Windowing shots is fine for coverage, but for “interestingness” you should also generate candidates around peaks/events. Do it as a separate generator plugin (modular).

## 4.1 Keep windowed candidates

* `candidate.from_shots_windowed@…` stays.

## 4.2 Add peak-based candidates

**Plugin:** `candidate.from_timeseries_peaks@1.0.0`
**Inputs:** activity_timeseries + audio_event_timeseries (+ optional novelty)
Algorithm (deterministic):

* compute `event_signal = w1*motion + w2*onset_rate + w3*novelty`
* find local maxima above percentile threshold
* emit windows centered on peaks (e.g. [t-8, t+16], clamped)
* snap to nearest shot boundaries (explicitly logged)

Output CandidateClips with `generation_method = "timeseries_peaks_v1"`

## 4.3 Add “hook-first” candidates

**Plugin:** `candidate.hook_first_windows@1.0.0`
Targets candidates where the first 2s are strong (motion/face/audio). This reduces “slow start” clips.

---

# 5) Selection should consume explicit scores + explicit similarity

Your existing `select.dpp_diverse` is fine, but it should not be responsible for inventing quality scores.

Make the interface explicit:

## 5.1 `select.dpp_diverse_v2@1.0.0`

**Inputs:**

* CandidateScore (quality per candidate)
* CandidateEmbedding (optional; for similarity)
* CandidateClip list (for time constraints)

**Config:**

* `k`
* `lambda` (diversity strength)
* `min_time_separation_s` (hard constraint; prevents near duplicates)
* `similarity_source = EMBEDDING|TIME_ONLY`

If embeddings are missing but config says `EMBEDDING`, that’s a hard error (or explicit mode switch if configured and logged).

---

# 6) Build an automated “selection report” for verification (no human labor, but debuggable)

To verify the “interestingness” improvement without manual scrubbing, generate artifacts that make issues obvious.

**Plugin:** `report.selection_debug@1.0.0`
For each selected candidate:

* write a sidecar JSON containing:

  * candidate start/end, score breakdown
  * top contributing signals
* export 3–5 representative thumbnails (first frame, mid, end)
* optionally generate a simple HTML index linking to the MP4 clips and thumbnails

This is not a dependency on human work; it’s automated evidence that the scoring isn’t nonsense.

---

# 7) Minor but important items to include (quick hit list)

These are the small operational improvements I called out; they’ll save time as soon as you start iterating on scoring:

1. **Tool version capture**

   * `env.capture_tool_versions` plugin that runs `ffmpeg -version` and `ffprobe -version`, stores stdout artifacts, emits refs.

2. **Variant terminal status correctness**

   * Ensure `VariantSpec.status` becomes `FAILED` when a transform fails, not stuck in `RUNNING`.

3. **Transcript usability**

   * Add `task_id` to plugin start/end/error events so you can read transcript.jsonl without DB joins.

4. **Entity mutation detection**

   * If an entity ID is deterministic, overwriting with different data should emit an explicit mutation error (or fail hard).

None of these are “nice to have” once you start iterating on “interestingness”.

---

# 8) Suggested implementation order (so you feel improvement quickly)

If you want maximum “better selection” per unit effort:

## Step 1: Real motion/activity + hook features (no ML deps)

* `feat.video_activity_timeseries`
* `feat.aggregate_candidate_hook_features`
* Update `feat.aggregate_candidate_features` to incorporate these (or introduce v2 aggregator)

This alone will improve selection on:

* action scenes
* fast visual changes
* anything with early movement

## Step 2: Audio events (still no heavy deps)

* `feat.audio_event_timeseries`

This improves:

* screams / bursts / crowd moments
* comedic hits with a sharp sound cue
* key moments in talkies

## Step 3: Face metrics (moderate deps)

* `feat.face_metrics_opencv_dnn`

This improves:

* dialogue and reaction beats (the “human-interest” content)

## Step 4: ScoringPolicy + explicit CandidateScore entity

* `score.interestingness_v2` + `CandidateScore` persistence
* update selection to consume explicit scores

This makes iteration safe and auditable.

## Step 5: Peak-based candidate generator

* `candidate.from_timeseries_peaks`

This increases recall of “moments” even if shot windowing misses them.

## Step 6: Semantic embeddings (GPU pipeline variant)

* `feat.shot_embeddings_clip`
* `feat.aggregate_candidate_embedding`
* “WITH_SEMANTICS” scoring mode + DPP similarity from embeddings

This is the biggest qualitative jump, but it’s also the heaviest operationally.

---

# 9) What “better” should mean (acceptance criteria)

On your two MP4s, after Step 1–3 (no CLIP), the selected candidates should show:

* higher average `hook_score` than random candidates
* lower incidence of “slow starts”
* fewer title cards / fades
* more face-dominant clips (if faces exist in the film)
* and a clear score breakdown that makes sense in the report artifact

If you add CLIP, you should additionally see:

* more semantically varied clips (not all “the loud part of the same scene”)
* more “weird imagery” moments even when not loud or cutty

---

If you want, I can write the **exact plugin I/O schemas** for the new feature/score plugins in the style your repo uses (Pydantic models + `schema_version` + entity updates), but the above is the concrete structure that will make selection meaningfully better while staying faithful to your “no hidden error behavior” philosophy.
