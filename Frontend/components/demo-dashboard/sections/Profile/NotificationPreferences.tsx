"use client"

import { Button } from "@/components/ui/button"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Label } from "@/components/ui/label"
import { Separator } from "@/components/ui/separator"
import { Switch } from "@/components/ui/switch"

type NotificationPreferencesProps = {
  isLoading: boolean
  onSave: () => void
}

export default function NotificationPreferences({ isLoading, onSave }: NotificationPreferencesProps) {
  return (
    <Card>
      <CardHeader>
        <CardTitle>Notification Preferences</CardTitle>
        <CardDescription>Manage how you receive notifications</CardDescription>
      </CardHeader>
      <CardContent className="space-y-4">
        <div className="space-y-4">
          <h3 className="text-lg font-medium">Email Notifications</h3>
          <div className="grid gap-2">
            <div className="flex items-center justify-between">
              <Label htmlFor="email-alerts">System Alerts</Label>
              <Switch id="email-alerts" defaultChecked />
            </div>
            <div className="flex items-center justify-between">
              <Label htmlFor="email-maintenance">Maintenance Reminders</Label>
              <Switch id="email-maintenance" defaultChecked />
            </div>
            <div className="flex items-center justify-between">
              <Label htmlFor="email-reports">Weekly Reports</Label>
              <Switch id="email-reports" defaultChecked />
            </div>
            <div className="flex items-center justify-between">
              <Label htmlFor="email-news">News and Updates</Label>
              <Switch id="email-news" />
            </div>
          </div>
        </div>

        <Separator />

        <div className="space-y-4">
          <h3 className="text-lg font-medium">Push Notifications</h3>
          <div className="grid gap-2">
            <div className="flex items-center justify-between">
              <Label htmlFor="push-alerts">System Alerts</Label>
              <Switch id="push-alerts" defaultChecked />
            </div>
            <div className="flex items-center justify-between">
              <Label htmlFor="push-maintenance">Maintenance Reminders</Label>
              <Switch id="push-maintenance" defaultChecked />
            </div>
            <div className="flex items-center justify-between">
              <Label htmlFor="push-reports">Weekly Reports</Label>
              <Switch id="push-reports" />
            </div>
          </div>
        </div>

        <div className="flex justify-end">
          <Button onClick={onSave} disabled={isLoading}>
            {isLoading ? "Saving..." : "Save Preferences"}
          </Button>
        </div>
      </CardContent>
    </Card>
  )
}
