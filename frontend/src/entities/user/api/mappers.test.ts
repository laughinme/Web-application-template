import { describe, expect, it } from "vitest";
import { toProfileUpdate, toUser } from "./mappers";

describe("user mappers", () => {
  it("maps the wire format to the UI model", () => {
    const user = toUser({
      id: "1",
      email: "a@b.c",
      username: null,
      bio: null,
      avatar_key: "avatars/1/x.png",
      avatar_url: "https://cdn/x.png",
      role: "admin",
      is_onboarded: true,
      banned: false,
      created_at: "2026-01-01T00:00:00Z",
      updated_at: "2026-01-02T00:00:00Z",
    });
    expect(user).toMatchObject({ avatarUrl: "https://cdn/x.png", role: "admin", isOnboarded: true });
  });

  it("keeps PATCH semantics: omitted stays omitted, null clears", () => {
    expect(toProfileUpdate({ bio: null })).toEqual({ bio: null });
    expect(toProfileUpdate({})).toEqual({});
  });
});
