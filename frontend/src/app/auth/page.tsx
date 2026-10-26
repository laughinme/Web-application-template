import { Suspense } from "react";
import { AuthGuard, SessionLoading } from "@/app/providers/auth/AuthGuard";
import AuthPage from "@/views/auth/ui/AuthPage";

export default function SignInPage() {
  return (
    <Suspense fallback={<SessionLoading />}>
      <AuthGuard guest>
        <AuthPage />
      </AuthGuard>
    </Suspense>
  );
}
