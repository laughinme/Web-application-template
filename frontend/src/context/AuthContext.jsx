import React, { useState, useEffect } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import * as api from '../api';
import { setAccessToken as setAxiosAccessToken, apiPublic } from '../api/axiosInstance.js';
import { AuthContext } from './AuthContextObject.js';

export const AuthProvider = ({ children }) => {
    const queryClient = useQueryClient();
    const [accessToken, setAccessToken] = useState(null);
    const [isRestoringSession, setIsRestoringSession] = useState(true);

    useEffect(() => {
        setAxiosAccessToken(accessToken);
    }, [accessToken]);

    const { data: user, isLoading: isUserLoading, isError } = useQuery({
        queryKey: ['me'],
        queryFn: async () => {
            try {
                return await api.getMyProfile();
            } catch (error) {
                console.log('API profile fetch failed:', error);
                throw error;
            }
        },
        enabled: !!accessToken, 
        retry: 1,
        onError: (err) => {
            console.error("Ошибка useQuery('me'): Не удалось загрузить профиль. Выход из системы.", err);
            setAccessToken(null);
        }
    });

   
    const loginMutation = useMutation({
        mutationFn: api.loginUser, 
        onSuccess: (data) => {
            if (data?.access_token) {
                setAccessToken(data.access_token);
            }
            queryClient.invalidateQueries({ queryKey: ['me'] });
        },
    });

    const registerMutation = useMutation({
        mutationFn: api.registerUser,
        onSuccess: (data) => {
            if (data?.access_token) {
                setAccessToken(data.access_token);
            }
            queryClient.invalidateQueries({ queryKey: ['me'] });
        },
    });
    
    const logoutMutation = useMutation({
        mutationFn: api.logoutUser,
        onSuccess: () => {
            setAccessToken(null);
            queryClient.clear(); 
        },
        onError: () => {
            setAccessToken(null);
            queryClient.clear();
        }
    });

    useEffect(() => {
        (async () => {
            try {
                const csrfCookie = document.cookie
                    .split(';')
                    .map((c) => c.trim())
                    .find((c) => c.startsWith('csrf_token='));

                const csrfToken = csrfCookie ? decodeURIComponent(csrfCookie.split('=')[1]) : null;

                if (!csrfToken) {
                    console.log("[Auth] CSRF-токен не найден, прекращаем попытку восстановления.");
                    return;
                }

                const { data } = await apiPublic.post('/auth/refresh', {}, {
                    headers: { 'X-CSRF-Token': csrfToken },
                    withCredentials: true,
                });

                if (data?.access_token) {
                    setAccessToken(data.access_token);
                }
            } catch (err) {
                console.error("[Auth] Ошибка при запросе на /auth/refresh:", err);
            } finally {
                setIsRestoringSession(false);
            }
        })();
    }, []);

    const value = {
        user: isError ? null : user,
        isUserLoading,
        isRestoringSession,
        login: loginMutation.mutateAsync,
        register: registerMutation.mutateAsync,
        logout: logoutMutation.mutate,
        isLoggingIn: loginMutation.isLoading,
        loginError: loginMutation.error,
        isRegistering: registerMutation.isLoading,
        registerError: registerMutation.error,
    };

    return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
};
