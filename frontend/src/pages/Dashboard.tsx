import * as React from "react"
import { z } from "zod"

import data from "@/app/dashboard/data.json"
import { AppSidebar } from "@/shared/components/app-sidebar"
import { ChartAreaInteractive } from "@/shared/components/chart-area-interactive"
import { DataTable, schema } from "@/shared/components/data-table"
import { SectionCards } from "@/shared/components/section-cards"
import { SiteHeader } from "@/shared/components/site-header"
import {
  SidebarInset,
  SidebarProvider,
} from "@/shared/components/ui/sidebar"

const tableData = z.array(schema).parse(data)

export default function DashboardPage() {
  return (
    <SidebarProvider
      style={
        {
          "--header-height": "4rem",
        } as React.CSSProperties
      }
    >
      <AppSidebar variant="inset" />
      <SidebarInset>
        <SiteHeader />
        <div className="@container/main flex flex-1 flex-col gap-4 py-4">
          <SectionCards />
          <div className="px-4 lg:px-6">
            <ChartAreaInteractive />
          </div>
          <DataTable data={tableData} />
        </div>
      </SidebarInset>
    </SidebarProvider>
  )
}
