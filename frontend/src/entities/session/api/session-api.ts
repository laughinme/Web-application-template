import { api, apiPublic, type Schemas, type TokenPairDto } from "@/shared/api";

export type Credentials = Schemas["LoginRequest"];
export type Registration = Schemas["RegisterRequest"];

// The browser is a `web` client: the refresh token stays in an httpOnly cookie.
const web = { headers: { "X-Client": "web" }, withCredentials: true };

export async function login(credentials: Credentials): Promise<TokenPairDto> {
  return (await apiPublic.post<TokenPairDto>("/auth/login", credentials, web)).data;
}

export async function register(registration: Registration): Promise<TokenPairDto> {
  return (await apiPublic.post<TokenPairDto>("/auth/register", registration, web)).data;
}

export async function logout(): Promise<void> {
  await api.post("/auth/logout");
}
