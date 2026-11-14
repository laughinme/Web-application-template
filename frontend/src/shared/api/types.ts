import type { components } from "./schema";

// DTO types come from the backend's OpenAPI (`make openapi`), never written by hand.
export type Schemas = components["schemas"];
export type ErrorCode = Schemas["ErrorCode"];
export type ProblemDto = Schemas["Problem"];
export type TokenPairDto = Schemas["TokenPair"];
