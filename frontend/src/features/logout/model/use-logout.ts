import { useMutation } from "@tanstack/react-query";
import { logout, useSession } from "@/entities/session";

/** Ends the session locally even if the request fails: the user asked to leave. */
export function useLogout() {
  const session = useSession();
  return useMutation({ mutationFn: logout, onSettled: () => session.end() });
}
