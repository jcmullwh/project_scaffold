import test from "node:test";
import { equal } from "node:assert/strict";
import { add } from "../src/index";

test("add", () => {
  equal(add(2, 3), 5);
});

