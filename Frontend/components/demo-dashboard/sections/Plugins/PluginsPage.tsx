"use client"

import { useState } from "react"
import { useToast } from "@/components/ui/use-toast"
import { DemoBadge } from "@/components/demo-dashboard/demo-badge"
import PluginsHeader from "./PluginsHeader"
import PluginsSearchBar from "./PluginsSearchBar"
import PluginsTabs from "./PluginsTabs"
import PluginSettings from "./PluginSettings"
import { Map, Zap, Calendar, BarChart2, Truck } from "lucide-react"

const plugins = [
  {
    id: "route-optimizer",
    name: "Route Optimizer",
    description: "Optimize routes for your fleet to save time and fuel",
    icon: Map,
    installed: true,
    version: "2.3.1",
    author: "FleetMaster",
    category: "routing",
  },
  {
    id: "fuel-tracker",
    name: "Fuel Tracker Pro",
    description: "Advanced fuel consumption tracking and analytics",
    icon: Zap,
    installed: true,
    version: "1.5.0",
    author: "EcoFleet Solutions",
    category: "analytics",
  },
  {
    id: "maintenance-scheduler",
    name: "Maintenance Scheduler",
    description: "Automated maintenance scheduling and reminders",
    icon: Calendar,
    installed: true,
    version: "3.0.2",
    author: "FleetMaster",
    category: "maintenance",
  },
  {
    id: "driver-performance",
    name: "Driver Performance Analytics",
    description: "Advanced driver behavior and performance metrics",
    icon: BarChart2,
    installed: false,
    version: "2.1.0",
    author: "FleetMetrics Inc.",
    category: "analytics",
  },
  {
    id: "vehicle-diagnostics",
    name: "Vehicle Diagnostics",
    description: "Real-time vehicle diagnostics and OBD integration",
    icon: Truck,
    installed: false,
    version: "1.8.3",
    author: "AutoTech Solutions",
    category: "maintenance",
  },
]

export default function PluginsPage() {
  const [searchTerm, setSearchTerm] = useState("")
  const [activeTab, setActiveTab] = useState("all")
  const [isLoading, setIsLoading] = useState(false)
  const { toast } = useToast()

  const filteredPlugins = plugins.filter(
    (plugin) =>
      (activeTab === "all" ||
        (activeTab === "installed" && plugin.installed) ||
        (activeTab === "available" && !plugin.installed) ||
        activeTab === plugin.category) &&
      (plugin.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
        plugin.description.toLowerCase().includes(searchTerm.toLowerCase()) ||
        plugin.author.toLowerCase().includes(searchTerm.toLowerCase()))
  )

  const handleInstall = (pluginId: string) => {
    setIsLoading(true)
    setTimeout(() => {
      setIsLoading(false)
      toast({
        title: "Plugin installed",
        description: "The plugin has been installed successfully.",
        duration: 3000,
      })
    }, 1500)
  }

  const handleUninstall = (pluginId: string) => {
    setIsLoading(true)
    setTimeout(() => {
      setIsLoading(false)
      toast({
        title: "Plugin uninstalled",
        description: "The plugin has been uninstalled successfully.",
        duration: 3000,
      })
    }, 1500)
  }

  const handleConfigure = (pluginId: string) => {
    const plugin = plugins.find((p) => p.id === pluginId)
    toast({
      title: "Plugin configuration",
      description: "Opening configuration for " + (plugin?.name || ""),
      duration: 3000,
    })
  }

  return (
    <div className="space-y-6">
      <PluginsHeader />
      <PluginsSearchBar searchTerm={searchTerm} setSearchTerm={setSearchTerm} />
      <PluginsTabs
        activeTab={activeTab}
        setActiveTab={setActiveTab}
        filteredPlugins={filteredPlugins}
        isLoading={isLoading}
        onInstall={handleInstall}
        onUninstall={handleUninstall}
        onConfigure={handleConfigure}
      />
      <PluginSettings />
    </div>
  )
}
