"use client";

import { useCallback, useEffect, useRef, useState, type ReactNode } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import * as api from "@/shared/api/auth";
import {
  refreshAccessToken,
  setAccessToken as setAxiosAccessToken,
  setUnauthorizedHandler as setAxiosUnauthorizedHandler
} from "@/shared/api/axiosInstance";
import { AuthContext } from "./AuthContextObject";
import type { AuthContextValue, AuthCredentials, AuthTokens, AuthUser } from "@/entities/auth/model";

const SKIP_SESSION_RESTORE_STORAGE_KEY = "auth:skip-session-restore";

const readSkipSessionRestoreFlag = (): boolean => {
  if (typeof window === "undefined") {
    return false;
  }
  try {
    return window.sessionStorage.getItem(SKIP_SESSION_RESTORE_STORAGE_KEY) === "1";
  } catch {
    return false;
  }
};

const writeSkipSessionRestoreFlag = (value: boolean): void => {
  if (typeof window === "undefined") {
    return;
  }
  try {
    if (value) {
      window.sessionStorage.setItem(SKIP_SESSION_RESTORE_STORAGE_KEY, "1");
    } else {
      window.sessionStorage.removeItem(SKIP_SESSION_RESTORE_STORAGE_KEY);
    }
  } catch {
  }
};

interface AuthProviderProps {
  children: ReactNode;
}

export const AuthProvider = ({ children }: AuthProviderProps) => {
  const queryClient = useQueryClient();
  const [accessToken, setAccessToken] = useState<string | null>(null);
  const [isRestoringSession, setIsRestoringSession] = useState<boolean>(true);
  const hasAttemptedSessionRestore = useRef<boolean>(false);

  const clearSession = useCallback((): void => {
    setAccessToken(null);
    setAxiosAccessToken(null);
    queryClient.removeQueries({ queryKey: ["me"] });
  }, [queryClient]);

  const acceptAccessToken = useCallback((token: string): void => {
    setAxiosAccessToken(token);
    setAccessToken(token);
    writeSkipSessionRestoreFlag(false);
  }, []);

  useEffect(() => {
    setAxiosUnauthorizedHandler(clearSession);
    return () => setAxiosUnauthorizedHandler(null);
  }, [clearSession]);

  const {
    data: user,
    isLoading: isUserLoading,
    isError
  } = useQuery<AuthUser>({
    queryKey: ["me"],
    queryFn: async () => api.getMyProfile(),
    enabled: Boolean(accessToken),
    retry: 1
  });

  const loginMutation = useMutation<AuthTokens, unknown, AuthCredentials>({
    mutationFn: api.loginUser,
    onSuccess: (data) => {
      if (data?.access_token) {
        acceptAccessToken(data.access_token);
      }
      queryClient.invalidateQueries({ queryKey: ["me"] });
    }
  });

  const registerMutation = useMutation<AuthTokens, unknown, AuthCredentials>({
    mutationFn: api.registerUser,
    onSuccess: (data) => {
      if (data?.access_token) {
        acceptAccessToken(data.access_token);
      }
      queryClient.invalidateQueries({ queryKey: ["me"] });
    }
  });

  const logoutMutation = useMutation<void, unknown, void>({
    mutationFn: api.logoutUser,
    onSuccess: () => {
      clearSession();
      queryClient.clear();
    },
    onError: () => {
      clearSession();
      queryClient.clear();
    }
  });

  const handleLogout = useCallback((): void => {
    writeSkipSessionRestoreFlag(true);
    logoutMutation.mutate();
  }, [logoutMutation]);

  useEffect(() => {
    if (hasAttemptedSessionRestore.current) {
      return;
    }
    hasAttemptedSessionRestore.current = true;
    (async () => {
      try {
        if (readSkipSessionRestoreFlag()) return;
        const newAccessToken = await refreshAccessToken();
        if (newAccessToken) {
          acceptAccessToken(newAccessToken);
        }
      } catch {
      } finally {
        setIsRestoringSession(false);
      }
    })();
  }, [acceptAccessToken]);

  const value: AuthContextValue = {
    user: !isError && user ? user : null,
    isUserLoading,
    isRestoringSession,
    login: loginMutation.mutateAsync,
    register: registerMutation.mutateAsync,
    logout: handleLogout,
    isLoggingIn: loginMutation.isPending,
    loginError: loginMutation.error,
    isRegistering: registerMutation.isPending,
    registerError: registerMutation.error
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
};
