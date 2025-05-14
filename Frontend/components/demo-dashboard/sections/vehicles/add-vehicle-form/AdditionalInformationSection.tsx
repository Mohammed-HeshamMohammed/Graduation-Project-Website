// components/demo-dashboard/vehicles/add-vehicle-form/AdditionalInformationSection.tsx
"use client";

import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Checkbox } from "@/components/ui/checkbox";

export function AdditionalInformationSection() {
  return (
    <div className="space-y-2">
      <h3 className="text-lg font-medium">Additional Information</h3>
      <div className="space-y-4">
        <div className="space-y-2">
          <Label htmlFor="notes">Notes</Label>
          <textarea
            id="notes"
            className="flex min-h-[80px] w-full rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50"
            placeholder="Any additional information about this vehicle"
          />
        </div>
        <div className="flex items-center space-x-2">
          <Checkbox id="gps-tracking" defaultChecked />
          <Label htmlFor="gps-tracking">GPS Tracking Enabled</Label>
        </div>
        <div className="flex items-center space-x-2">
          <Checkbox id="dash-cam" defaultChecked />
          <Label htmlFor="dash-cam">Dash Camera Installed</Label>
        </div>
        <div className="flex items-center space-x-2">
          <Checkbox id="telematics" />
          <Label htmlFor="telematics">Telematics System Installed</Label>
        </div>
      </div>
    </div>
  );
}
