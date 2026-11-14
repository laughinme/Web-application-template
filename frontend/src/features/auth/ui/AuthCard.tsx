"use client";

import { useState, type FormEvent } from "react";
import { Button } from "@/shared/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/shared/ui/card";
import { Field, FieldDescription, FieldError, FieldGroup, FieldLabel } from "@/shared/ui/field";
import { Input } from "@/shared/ui/input";
import { authErrorMessage, useLogin, useRegister } from "../model/use-auth";

type Mode = "login" | "register";

const COPY = {
  login: {
    title: "С возвращением",
    description: "Войдите по email и паролю",
    submit: "Войти",
    switchText: "Нет аккаунта?",
    switchAction: "Зарегистрироваться",
  },
  register: {
    title: "Создать аккаунт",
    description: "Email и пароль не короче 8 символов",
    submit: "Создать аккаунт",
    switchText: "Уже есть аккаунт?",
    switchAction: "Войти",
  },
} as const;

/** Sign-in and sign-up in one card. On success the session starts; routing is the page's job. */
export function AuthCard() {
  const [mode, setMode] = useState<Mode>("login");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const loginMutation = useLogin();
  const registerMutation = useRegister();
  const active = mode === "login" ? loginMutation : registerMutation;
  const copy = COPY[mode];
  const canSubmit = email.trim() !== "" && password !== "" && !active.isPending;

  const submit = (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    if (!canSubmit) return;
    active.mutate({ email: email.trim(), password });
  };

  const switchMode = () => {
    loginMutation.reset();
    registerMutation.reset();
    setMode(mode === "login" ? "register" : "login");
  };

  return (
    <Card className="w-full max-w-sm">
      <CardHeader className="text-center">
        <CardTitle className="text-xl">{copy.title}</CardTitle>
        <CardDescription>{copy.description}</CardDescription>
      </CardHeader>
      <CardContent>
        <form onSubmit={submit} noValidate>
          <FieldGroup>
            {active.error ? <FieldError>{authErrorMessage(active.error)}</FieldError> : null}
            <Field>
              <FieldLabel htmlFor="email">Email</FieldLabel>
              <Input
                id="email"
                type="email"
                autoComplete="email"
                placeholder="you@example.com"
                value={email}
                onChange={(event) => setEmail(event.target.value)}
              />
            </Field>
            <Field>
              <FieldLabel htmlFor="password">Пароль</FieldLabel>
              <Input
                id="password"
                type="password"
                autoComplete={mode === "login" ? "current-password" : "new-password"}
                value={password}
                onChange={(event) => setPassword(event.target.value)}
              />
            </Field>
            <Field>
              <Button type="submit" disabled={!canSubmit}>
                {active.isPending ? "Подождите…" : copy.submit}
              </Button>
              <FieldDescription className="text-center">
                {copy.switchText}{" "}
                <button
                  type="button"
                  onClick={switchMode}
                  className="font-medium underline-offset-4 hover:underline"
                >
                  {copy.switchAction}
                </button>
              </FieldDescription>
            </Field>
          </FieldGroup>
        </form>
      </CardContent>
    </Card>
  );
}
