"use client"

import {
  Card,
  CardContent,
  CardDescription,
  CardFooter,
  CardHeader,
  CardTitle,
} from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { Settings, Check, X, Download } from "lucide-react"

type Plugin = {
  id: string
  name: string
  description: string
  icon: React.ElementType
  installed: boolean
  version: string
  author: string
  category: string
}

type PluginCardProps = {
  plugin: Plugin
  isLoading: boolean
  onInstall: (pluginId: string) => void
  onUninstall: (pluginId: string) => void
  onConfigure: (pluginId: string) => void
}

export default function PluginCard({
  plugin,
  isLoading,
  onInstall,
  onUninstall,
  onConfigure,
}: PluginCardProps) {
  const Icon = plugin.icon
  return (
    <Card className="overflow-hidden">
      <CardHeader className="pb-2">
        <div className="flex justify-between items-start">
          <div className="flex items-center space-x-2">
            <div className="bg-primary/10 p-2 rounded-md">
              <Icon className="h-5 w-5 text-primary" />
            </div>
            <CardTitle className="text-lg">{plugin.name}</CardTitle>
          </div>
          {plugin.installed ? (
            <Badge className="bg-green-100 text-green-800">
              <Check className="mr-1 h-3 w-3" /> Installed
            </Badge>
          ) : (
            <Badge variant="outline">Available</Badge>
          )}
        </div>
        <CardDescription>{plugin.description}</CardDescription>
      </CardHeader>
      <CardContent className="pb-2">
        <div className="flex flex-wrap gap-2 text-sm">
          <div className="flex items-center">
            <span className="text-muted-foreground mr-1">Version:</span>
            <span>{plugin.version}</span>
          </div>
          <div className="flex items-center">
            <span className="text-muted-foreground mr-1">By:</span>
            <span>{plugin.author}</span>
          </div>
        </div>
      </CardContent>
      <CardFooter className="flex justify-between pt-0">
        {plugin.installed ? (
          <>
            <Button variant="outline" size="sm" onClick={() => onConfigure(plugin.id)}>
              <Settings className="mr-2 h-4 w-4" /> Configure
            </Button>
            <Button
              variant="outline"
              size="sm"
              className="text-red-600"
              onClick={() => onUninstall(plugin.id)}
              disabled={isLoading}
            >
              <X className="mr-2 h-4 w-4" /> {isLoading ? "Uninstalling..." : "Uninstall"}
            </Button>
          </>
        ) : (
          <Button className="w-full" onClick={() => onInstall(plugin.id)} disabled={isLoading}>
            <Download className="mr-2 h-4 w-4" /> {isLoading ? "Installing..." : "Install"}
          </Button>
        )}
      </CardFooter>
    </Card>
  )
}
