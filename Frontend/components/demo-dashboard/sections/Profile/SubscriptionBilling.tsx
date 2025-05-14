"use client"

import { Button } from "@/components/ui/button"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Separator } from "@/components/ui/separator"
import { Shield } from "lucide-react"

export default function SubscriptionBilling() {
  return (
    <Card>
      <CardHeader>
        <CardTitle>Subscription & Billing</CardTitle>
        <CardDescription>Manage your subscription and billing information</CardDescription>
      </CardHeader>
      <CardContent className="space-y-4">
        <div className="flex items-center justify-between">
          <div>
            <h4 className="font-medium">Current Plan</h4>
            <p className="text-sm text-muted-foreground">Enterprise Plan</p>
          </div>
          <Badge className="bg-green-100 text-green-800 hover:bg-green-100">Active</Badge>
        </div>

        <Separator />

        <div className="space-y-2">
          <h4 className="font-medium">Plan Features</h4>
          <ul className="grid gap-2 text-sm">
            <li className="flex items-center">
              <Shield className="mr-2 h-4 w-4 text-green-600" />
              Unlimited vehicles
            </li>
            <li className="flex items-center">
              <Shield className="mr-2 h-4 w-4 text-green-600" />
              Unlimited drivers
            </li>
            <li className="flex items-center">
              <Shield className="mr-2 h-4 w-4 text-green-600" />
              Advanced analytics
            </li>
            <li className="flex items-center">
              <Shield className="mr-2 h-4 w-4 text-green-600" />
              24/7 support
            </li>
          </ul>
        </div>

        <Separator />

        <div className="flex items-center justify-between">
          <div>
            <h4 className="font-medium">Billing Information</h4>
            <p className="text-sm text-muted-foreground">Next billing date: January 1, 2024</p>
          </div>
          <Button variant="outline">View Invoices</Button>
        </div>
      </CardContent>
    </Card>
  )
}
