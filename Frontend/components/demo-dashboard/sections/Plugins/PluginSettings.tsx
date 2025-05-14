"use client"

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Separator } from "@/components/ui/separator"
import { Switch } from "@/components/ui/switch"

export default function PluginSettings() {
  return (
    <Card>
      <CardHeader>
        <CardTitle>Plugin Settings</CardTitle>
        <CardDescription>Configure global plugin settings</CardDescription>
      </CardHeader>
      <CardContent className="space-y-4">
        <div className="flex items-center justify-between">
          <div className="space-y-0.5">
            <h4 className="font-medium">Auto-Update Plugins</h4>
            <p className="text-sm text-muted-foreground">
              Automatically update plugins when new versions are available
            </p>
          </div>
          <Switch defaultChecked />
        </div>

        <Separator />

        <div className="flex items-center justify-between">
          <div className="space-y-0.5">
            <h4 className="font-medium">Plugin Notifications</h4>
            <p className="text-sm text-muted-foreground">
              Receive notifications about plugin updates and new features
            </p>
          </div>
          <Switch defaultChecked />
        </div>

        <Separator />

        <div className="flex items-center justify-between">
          <div className="space-y-0.5">
            <h4 className="font-medium">Developer Mode</h4>
            <p className="text-sm text-muted-foreground">
              Enable advanced features for plugin development and testing
            </p>
          </div>
          <Switch />
        </div>
      </CardContent>
    </Card>
  )
}
