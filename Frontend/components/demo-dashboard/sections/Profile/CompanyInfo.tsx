"use client"

import { Button } from "@/components/ui/button"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Separator } from "@/components/ui/separator"

type CompanyInfoProps = {
  isLoading: boolean
  onSave: () => void
}

export default function CompanyInfo({ isLoading, onSave }: CompanyInfoProps) {
  return (
    <Card>
      <CardHeader>
        <CardTitle>Company Information</CardTitle>
        <CardDescription>View and update your company details</CardDescription>
      </CardHeader>
      <CardContent className="space-y-4">
        <div className="grid gap-4 md:grid-cols-2">
          <div className="space-y-2">
            <Label htmlFor="company-name">Company Name</Label>
            <Input id="company-name" defaultValue="FleetMaster Inc." />
          </div>
          <div className="space-y-2">
            <Label htmlFor="company-id">Company ID</Label>
            <Input id="company-id" defaultValue="FLT-12345" disabled />
          </div>
          <div className="space-y-2">
            <Label htmlFor="company-address">Address</Label>
            <Input id="company-address" defaultValue="123 Fleet Street, Business District, City, 12345" />
          </div>
          <div className="space-y-2">
            <Label htmlFor="company-phone">Phone</Label>
            <Input id="company-phone" type="tel" defaultValue="+1 (555) 987-6543" />
          </div>
          <div className="space-y-2">
            <Label htmlFor="company-email">Email</Label>
            <Input id="company-email" type="email" defaultValue="info@fleetmaster.com" />
          </div>
          <div className="space-y-2">
            <Label htmlFor="company-website">Website</Label>
            <Input id="company-website" type="url" defaultValue="https://fleetmaster.com" />
          </div>
        </div>

        <Separator />

        <div className="space-y-2">
          <Label htmlFor="company-description">Company Description</Label>
          <textarea
            id="company-description"
            title="Company Description"
            placeholder="Enter a description of your company"
            className="flex min-h-[100px] w-full rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50"
            defaultValue="FleetMaster Inc. is a leading transportation and logistics company specializing in efficient fleet management solutions."
          />
        </div>

        <div className="flex justify-end">
          <Button onClick={onSave} disabled={isLoading}>
            {isLoading ? "Saving..." : "Save Changes"}
          </Button>
        </div>
      </CardContent>
    </Card>
  )
}
