"use client"

import { Button } from "@/components/ui/button"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Separator } from "@/components/ui/separator"
import { Switch } from "@/components/ui/switch"

type ChangePasswordProps = {
  isLoading: boolean
  onSave: () => void
}

export default function ChangePassword({ isLoading, onSave }: ChangePasswordProps) {
  return (
    <>
      <Card>
        <CardHeader>
          <CardTitle>Change Password</CardTitle>
          <CardDescription>Update your password to keep your account secure</CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="space-y-2">
            <Label htmlFor="current-password">Current Password</Label>
            <Input id="current-password" type="password" />
          </div>
          <div className="space-y-2">
            <Label htmlFor="new-password">New Password</Label>
            <Input id="new-password" type="password" />
          </div>
          <div className="space-y-2">
            <Label htmlFor="confirm-password">Confirm New Password</Label>
            <Input id="confirm-password" type="password" />
          </div>

          <div className="flex justify-end">
            <Button onClick={onSave} disabled={isLoading}>
              {isLoading ? "Updating..." : "Update Password"}
            </Button>
          </div>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>Two-Factor Authentication</CardTitle>
          <CardDescription>Add an extra layer of security to your account</CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="flex items-center justify-between">
            <div className="space-y-0.5">
              <h4 className="font-medium">Two-Factor Authentication</h4>
              <p className="text-sm text-muted-foreground">
                Enhance your account security by enabling two-factor authentication.
              </p>
            </div>
            <Switch />
          </div>

          <Separator />

          <div className="flex items-center justify-between">
            <div className="space-y-0.5">
              <h4 className="font-medium">Recovery Codes</h4>
              <p className="text-sm text-muted-foreground">
                Generate recovery codes to access your account if you lose your two-factor authentication device.
              </p>
            </div>
            <Button variant="outline" disabled>
              Generate Codes
            </Button>
          </div>
        </CardContent>
      </Card>
    </>
  )
}
