"use client";

import { useQueryClient } from "@tanstack/react-query";
import { createContext, useCallback, useContext, useEffect, useMemo, useRef, useState, type ReactNode } from "react";
import { refreshAccessToken, setAccessToken, setUnauthorizedHandler } from "@/shared/api";

export type SessionStatus = "restoring" | "authenticated" | "anonymous";

export interface Session {
  status: SessionStatus;
  /** Call with the access token from login, register or refresh. */
  start: (accessToken: string) => void;
  /** Forget the token and every cached query: the next user must not see this one's data. */
  end: () => void;
}

const SessionContext = createContext<Session | null>(null);

export function SessionProvider({ children }: { children: ReactNode }) {
  const queryClient = useQueryClient();
  const [status, setStatus] = useState<SessionStatus>("restoring");
  const restoreStarted = useRef(false);

  const start = useCallback((accessToken: string) => {
    setAccessToken(accessToken);
    setStatus("authenticated");
  }, []);

  const end = useCallback(() => {
    setAccessToken(null);
    setStatus("anonymous");
    queryClient.clear();
  }, [queryClient]);

  useEffect(() => {
    setUnauthorizedHandler(end);
    return () => setUnauthorizedHandler(null);
  }, [end]);

  // A reload loses the in-memory access token; the refresh cookie brings it back.
  useEffect(() => {
    if (restoreStarted.current) return;
    restoreStarted.current = true;
    refreshAccessToken()
      .then((token) => (token ? start(token) : setStatus("anonymous")))
      .catch(() => setStatus("anonymous"));
  }, [start]);

  const value = useMemo(() => ({ status, start, end }), [status, start, end]);
  return <SessionContext.Provider value={value}>{children}</SessionContext.Provider>;
}

export function useSession(): Session {
  const session = useContext(SessionContext);
  if (!session) throw new Error("useSession must be used inside <SessionProvider>");
  return session;
}
