"use client"

import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import PluginList from "./PluginList"

type PluginsTabsProps = {
  activeTab: string
  setActiveTab: (tab: string) => void
  filteredPlugins: any[]
  isLoading: boolean
  onInstall: (pluginId: string) => void
  onUninstall: (pluginId: string) => void
  onConfigure: (pluginId: string) => void
}

export default function PluginsTabs({
  activeTab,
  setActiveTab,
  filteredPlugins,
  isLoading,
  onInstall,
  onUninstall,
  onConfigure,
}: PluginsTabsProps) {
  return (
    <Tabs
      defaultValue="all"
      className="space-y-4"
      value={activeTab}
      onValueChange={setActiveTab}
    >
      <TabsList>
        <TabsTrigger value="all">All</TabsTrigger>
        <TabsTrigger value="installed">Installed</TabsTrigger>
        <TabsTrigger value="available">Available</TabsTrigger>
        <TabsTrigger value="routing">Routing</TabsTrigger>
        <TabsTrigger value="analytics">Analytics</TabsTrigger>
        <TabsTrigger value="maintenance">Maintenance</TabsTrigger>
      </TabsList>

      <TabsContent value={activeTab} className="space-y-4">
        <PluginList
          plugins={filteredPlugins}
          isLoading={isLoading}
          onInstall={onInstall}
          onUninstall={onUninstall}
          onConfigure={onConfigure}
        />
      </TabsContent>
    </Tabs>
  )
}
