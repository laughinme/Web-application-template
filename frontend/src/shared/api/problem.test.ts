import { AxiosError, AxiosHeaders } from "axios";
import { describe, expect, it } from "vitest";
import { errorCode, problemMessage } from "./problem";

function httpError(status: number, data: unknown): AxiosError {
  const config = { headers: new AxiosHeaders() };
  return new AxiosError("failed", undefined, config, null, { status, statusText: "", headers: {}, config, data });
}

const problem = { status: 401, error_code: "WRONG_CREDENTIALS", detail: "Wrong email or password" };

describe("problemMessage", () => {
  it("uses the screen's wording for a known code", () => {
    expect(problemMessage(httpError(401, problem), { WRONG_CREDENTIALS: "Неверный пароль" })).toBe("Неверный пароль");
  });

  it("falls back to common wording, then to the fallback", () => {
    expect(problemMessage(httpError(429, { status: 429, error_code: "RATE_LIMITED" }), {})).toMatch(/подождите/);
    expect(problemMessage(httpError(409, { status: 409, error_code: "CONFLICT" }), {}, "fallback")).toBe("fallback");
  });

  it("tells a network failure apart from a server answer", () => {
    expect(problemMessage(new AxiosError("Network Error"), {})).toBe("Нет связи с сервером");
  });

  it("reads error_code only from problem bodies", () => {
    expect(errorCode(httpError(401, problem))).toBe("WRONG_CREDENTIALS");
    expect(errorCode(httpError(502, "<html>bad gateway</html>"))).toBeNull();
  });
});
