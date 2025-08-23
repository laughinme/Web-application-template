import React, { useState, useEffect } from "react";
import { useAuth } from "../../context/useAuth.js";

export default function AuthPage() {
    const [mode, setMode] = useState("login"); 
    const [email, setEmail] = useState("");
    const [password, setPassword] = useState("");
    const [isVisible, setIsVisible] = useState(false);
    
    const { login, register, isLoggingIn, loginError, isRegistering, registerError } = useAuth();
    
    const isLoading = isLoggingIn || isRegistering;
    const error = mode === 'login' ? loginError : registerError;
    
    const canSubmit = email.trim() && password.trim() && !isLoading;

    useEffect(() => {
        setIsVisible(true);
    }, []);

    const submit = async (e) => {
        e.preventDefault();
        if (!canSubmit) return;

        const credentials = { email: email.trim(), password };

        try {
            if (mode === 'login') {
                await login(credentials);
            } else if (mode === 'register') {
                await register(credentials);
            }
        } catch (err) {
            console.error("Ошибка аутентификации:", err);
        }
    };
    
    return (
        <div className="min-h-screen relative overflow-hidden">
            <div className="absolute inset-0">
                <div className="absolute inset-0 bg-gradient-to-br from-indigo-50 via-white to-cyan-50"></div>
                <div className="absolute top-0 left-0 w-full h-full">
                    <div className="absolute top-20 left-20 w-72 h-72 bg-purple-300 rounded-full mix-blend-multiply filter blur-xl opacity-70 animate-blob"></div>
                    <div className="absolute top-40 right-20 w-72 h-72 bg-yellow-300 rounded-full mix-blend-multiply filter blur-xl opacity-70 animate-blob animation-delay-2000"></div>
                    <div className="absolute -bottom-8 left-40 w-72 h-72 bg-pink-300 rounded-full mix-blend-multiply filter blur-xl opacity-70 animate-blob animation-delay-4000"></div>
                </div>
            </div>

            <div className="relative min-h-screen flex items-center justify-center px-4">
                <div className={`w-full max-w-md transform transition-all duration-1000 ${isVisible ? 'translate-y-0 opacity-100' : 'translate-y-8 opacity-0'}`}>
                    <div className="backdrop-blur-lg bg-white/20 rounded-3xl border border-white/30 shadow-2xl p-8 relative">
                        <div className="text-center mb-8">
                            <h1 className="text-4xl md:text-5xl font-bold mt-6 tracking-tight bg-gradient-to-r from-gray-900 via-gray-800 to-gray-900 bg-clip-text text-transparent leading-tight">
                                {mode === "login" ? "Добро пожаловать" : "Создать аккаунт"}
                            </h1>
                            <p className="text-gray-600 mt-3 text-lg font-medium">
                                {mode === "login" ? "Рады видеть вас снова" : "Присоединяйтесь к нам"}
                            </p>
                        </div>

                        <form className="space-y-6" onSubmit={submit}>
                            {error && (
                                <div className="p-4 text-center text-red-700 bg-red-50/80 rounded-2xl border border-red-200">
                                    <span>{error?.response?.data?.detail || error.message || "Произошла ошибка"}</span>
                                </div>
                            )}
                            <input className="w-full h-14 px-6 rounded-2xl bg-white/80 border border-white/50 outline-none focus:ring-2 focus:ring-indigo-300" placeholder="Адрес электронной почты" type="email" value={email} onChange={(e) => setEmail(e.target.value)} disabled={isLoading} />
                            <input className="w-full h-14 px-6 rounded-2xl bg-white/80 border border-white/50 outline-none focus:ring-2 focus:ring-purple-300" placeholder="Пароль" type="password" value={password} onChange={(e) => setPassword(e.target.value)} disabled={isLoading} />
                            <button className="w-full h-14 rounded-2xl text-lg font-semibold transition-all bg-gradient-to-r from-indigo-600 to-purple-600 text-white disabled:bg-gray-200" type="submit" disabled={!canSubmit}>
                                {isLoading ? 'Загрузка...' : (mode === "login" ? "Войти" : "Зарегистрироваться")}
                            </button>
                        </form>

                        <div className="text-center mt-8">
                            {mode === "login" ? (
                                <button className="text-indigo-600 font-semibold" type="button" onClick={() => setMode("register")}>
                                    Нет аккаунта? Зарегистрироваться
                                </button>
                            ) : (
                                <button className="text-indigo-600 font-semibold" type="button" onClick={() => setMode("login")}>
                                    Уже есть аккаунт? Войти
                                </button>
                            )}
                        </div>

                        
                    </div>
                </div>
            </div>
        </div>
    );
}
