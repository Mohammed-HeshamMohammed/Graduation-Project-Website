"use client"

import { DemoBadge } from "@/components/demo-dashboard/demo-badge"

export default function PluginsHeader() {
  return (
    <div className="flex justify-between items-center">
      <h1 className="text-2xl font-bold">Plugins</h1>
      <DemoBadge />
    </div>
  )
}
