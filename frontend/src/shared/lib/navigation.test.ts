import { describe, expect, it } from "vitest";
import { safeReturnPath } from "./navigation";

describe("safeReturnPath", () => {
  it.each(["/profile", "/profile?tab=details", "/admin/users"])("keeps local path %s", (path) => {
    expect(safeReturnPath(path)).toBe(path);
  });

  it.each([null, "", "//evil.com", "/\\evil.com", "https://evil.com", "/auth", "/auth/", "/ space"])(
    "falls back to / for %s",
    (path) => {
      expect(safeReturnPath(path)).toBe("/");
    },
  );
});
