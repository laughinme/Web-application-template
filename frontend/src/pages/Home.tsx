import { useCallback } from "react"

import { useAuth } from "@/app/providers/auth/useAuth"
import { Button } from "@/shared/components/ui/button"

export default function HomePage() {
  const auth = useAuth()

  const handleLogout = useCallback(() => {
    if (!auth) {
      return
    }

    auth.dismissCsrfWarning()
    auth.logout()
  }, [auth])

  return (
    <div className="min-h-screen bg-neutral-950 flex items-center justify-center">
      <Button type="button" onClick={handleLogout}>
        Logout
      </Button>
    </div>
  )
}
