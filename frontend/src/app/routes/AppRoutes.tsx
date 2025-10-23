import { Navigate, Outlet, useLocation, useRoutes, type Location, type RouteObject } from "react-router-dom";
import DashboardPage from "@/pages/Dashboard";
import AuthPage from "@/pages/auth/ui/AuthPage";
import { useAuth } from "@/app/providers/auth/useAuth";

const RequireAuth = () => {
  const auth = useAuth();
  const location = useLocation();

  if (!auth) {
    throw new Error("Auth context is unavailable. Wrap routes with <AuthProvider>.");
  }

  if (!auth.user) {
    return <Navigate to="/auth" replace state={{ from: location }} />;
  }

  return <Outlet />;
};

const RedirectIfAuthenticated = () => {
  const auth = useAuth();
  const location = useLocation();

  if (!auth) {
    throw new Error("Auth context is unavailable. Wrap routes with <AuthProvider>.");
  }

  if (auth.user) {
    const state = location.state as { from?: Location } | undefined;
    const from = state?.from;
    const targetPath =
      from && from.pathname && from.pathname !== "/auth" ? from.pathname : "/dashboard";

    return <Navigate to={targetPath} replace />;
  }

  return <AuthPage />;
};

export const routes: RouteObject[] = [
  {
    path: "/",
    element: <RequireAuth />,
    children: [
      { index: true, element: <Navigate to="/dashboard" replace /> },
      { path: "dashboard", element: <DashboardPage /> }
    ]
  },
  {
    path: "/auth",
    element: <RedirectIfAuthenticated />
  },
  {
    path: "*",
    element: <Navigate to="/dashboard" replace />
  }
];

export const AppRoutes = () => {
  return useRoutes(routes);
};
