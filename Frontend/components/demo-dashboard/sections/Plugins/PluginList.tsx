"use client"

import { Card, CardContent } from "@/components/ui/card"
import { AlertTriangle } from "lucide-react"
import PluginCard from "./PluginCard"

type PluginListProps = {
  plugins: any[]
  isLoading: boolean
  onInstall: (pluginId: string) => void
  onUninstall: (pluginId: string) => void
  onConfigure: (pluginId: string) => void
}

export default function PluginList({
  plugins,
  isLoading,
  onInstall,
  onUninstall,
  onConfigure,
}: PluginListProps) {
  if (plugins.length === 0) {
    return (
      <Card>
        <CardContent className="flex flex-col items-center justify-center py-10">
          <AlertTriangle className="h-10 w-10 text-muted-foreground mb-4" />
          <p className="text-lg font-medium">No plugins found</p>
          <p className="text-muted-foreground">
            Try adjusting your search or filter criteria
          </p>
        </CardContent>
      </Card>
    )
  }

  return (
    <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
      {plugins.map((plugin) => (
        <PluginCard
          key={plugin.id}
          plugin={plugin}
          isLoading={isLoading}
          onInstall={onInstall}
          onUninstall={onUninstall}
          onConfigure={onConfigure}
        />
      ))}
    </div>
  )
}
