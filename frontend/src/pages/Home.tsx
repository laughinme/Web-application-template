import { useCallback } from "react"

import { useAuth } from "@/app/providers/auth/useAuth"
import { Button } from "@/shared/components/ui/button"
import DashboardPage from "./Dashboard"

export default function HomePage() {
  const auth = useAuth()

  const handleLogout = useCallback(() => {
    if (!auth) {
      return
    }

    auth.logout()
  }, [auth])

  return (
    <div className="min-h-screen bg-neutral-950 flex items-center justify-center">
      <DashboardPage/>
      {/* <Button type="button" onClick={handleLogout}>
        Logout
      </Button> */}
    </div>
  )
}
