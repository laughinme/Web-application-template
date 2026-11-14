// `?next=` comes from the URL, so only local paths are accepted: no `//host`, no `\`, no schemes.
export function safeReturnPath(value: string | null, authPath = "/auth"): string {
  if (!value || !value.startsWith("/") || value.startsWith("//") || /[\\\s]/.test(value)) {
    return "/";
  }
  const url = new URL(value, "http://localhost");
  return url.pathname.replace(/\/+$/, "") === authPath ? "/" : value;
}
