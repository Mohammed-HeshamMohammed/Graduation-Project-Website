"use client";

import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Separator } from "@/components/ui/separator";
import { Building, Plus } from "lucide-react";
import { Button } from "@/components/ui/button";

interface CompanySettingsProps {
  handleSave: () => void;
  isLoading: boolean;
}

export function CompanySettings({ handleSave, isLoading }: CompanySettingsProps) {
  return (
    <Card>
      <CardHeader>
        <CardTitle>Company Settings</CardTitle>
        <CardDescription>Manage your company settings</CardDescription>
      </CardHeader>
      <CardContent className="space-y-4">
        <div className="grid gap-4 md:grid-cols-2">
          <div className="space-y-2">
            <Label htmlFor="company-name">Company Name</Label>
            <Input id="company-name" defaultValue="FleetMaster Inc." />
          </div>
          <div className="space-y-2">
            <Label htmlFor="company-logo">Company Logo</Label>
            <div className="flex items-center gap-4">
              <div className="h-16 w-16 rounded-md border flex items-center justify-center">
                <Building className="h-8 w-8 text-muted-foreground" />
              </div>
              <Button variant="outline">Upload Logo</Button>
            </div>
          </div>
          <div className="space-y-2">
            <Label htmlFor="industry">Industry</Label>
            <Select defaultValue="transportation">
              <SelectTrigger id="industry" aria-label="Select industry">
                <SelectValue placeholder="Select industry" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="transportation">Transportation</SelectItem>
                <SelectItem value="logistics">Logistics</SelectItem>
                <SelectItem value="construction">Construction</SelectItem>
                <SelectItem value="delivery">Delivery</SelectItem>
                <SelectItem value="other">Other</SelectItem>
              </SelectContent>
            </Select>
          </div>
          <div className="space-y-2">
            <Label htmlFor="company-size">Company Size</Label>
            <Select defaultValue="medium">
              <SelectTrigger id="company-size" aria-label="Select company size">
                <SelectValue placeholder="Select company size" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="small">Small (1-50 employees)</SelectItem>
                <SelectItem value="medium">Medium (51-200 employees)</SelectItem>
                <SelectItem value="large">Large (201-1000 employees)</SelectItem>
                <SelectItem value="enterprise">Enterprise (1000+ employees)</SelectItem>
              </SelectContent>
            </Select>
          </div>
        </div>

        <Separator />

        <div className="space-y-2">
          <Label htmlFor="business-hours">Business Hours</Label>
          <div className="grid gap-4 md:grid-cols-2">
            <div className="flex items-center space-x-2">
              <Label htmlFor="start-time" className="w-24">
                Start Time
              </Label>
              <Input id="start-time" type="time" defaultValue="09:00" />
            </div>
            <div className="flex items-center space-x-2">
              <Label htmlFor="end-time" className="w-24">
                End Time
              </Label>
              <Input id="end-time" type="time" defaultValue="17:00" />
            </div>
          </div>
          <div className="flex flex-wrap gap-2 mt-2">
            {["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"].map((day, index) => (
              <div key={index} className="flex items-center space-x-2">
                {/* Fixed: Properly associate label with input using htmlFor */}
                <input 
                  type="checkbox" 
                  id={`day-${index}`} 
                  defaultChecked={index < 5} 
                  aria-label={day}
                />
                <Label htmlFor={`day-${index}`}>{day}</Label>
              </div>
            ))}
          </div>
        </div>

        <Separator />

        <div className="space-y-2">
          <h3 className="text-lg font-medium">Locations</h3>
          <div className="rounded-md border">
            <div className="grid grid-cols-4 gap-4 p-4 font-medium">
              <div>Name</div>
              <div>Address</div>
              <div>Type</div>
              <div className="text-right">Actions</div>
            </div>
            <Separator />
            {[
              { name: "Main Depot", address: "123 Main St, Anytown, USA", type: "Headquarters" },
              { name: "North Depot", address: "456 North Ave, Springfield, USA", type: "Depot" },
              { name: "South Depot", address: "789 South Blvd, Somewhere, USA", type: "Depot" },
            ].map((location, index) => (
              <div key={index} className="grid grid-cols-4 gap-4 p-4 items-center">
                <div>{location.name}</div>
                <div className="text-muted-foreground">{location.address}</div>
                <div>{location.type}</div>
                <div className="flex justify-end space-x-2">
                  <Button variant="outline" size="sm">
                    Edit
                  </Button>
                  <Button variant="outline" size="sm" className="text-red-600">
                    Delete
                  </Button>
                </div>
              </div>
            ))}
          </div>
          <Button variant="outline" size="sm">
            <Plus className="mr-2 h-4 w-4" /> Add Location
          </Button>
        </div>

        <div className="flex justify-end">
          <Button onClick={handleSave} disabled={isLoading}>
            {isLoading ? "Saving..." : "Save Changes"}
          </Button>
        </div>
      </CardContent>
    </Card>
  );
}