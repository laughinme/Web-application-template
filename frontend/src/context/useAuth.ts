import { useContext } from "react";
import { AuthContext } from "./AuthContextObject";
import type { AuthContextValue } from "../types/auth";

export const useAuth = (): AuthContextValue | null => useContext(AuthContext);
