// components/sections/drivers/add-driver-form/AdditionalInfoSection.tsx
"use client";

import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Separator } from "@/components/ui/separator";
import { Checkbox } from "@/components/ui/checkbox";

export function AdditionalInfoSection() {
  return (
    <div className="space-y-2">
      <h3 className="text-lg font-medium">Additional Information</h3>
      <div className="space-y-4">
        <div className="space-y-2">
          <Label htmlFor="medical-info">Medical Information</Label>
          <textarea
            id="medical-info"
            className="flex min-h-[80px] w-full rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50"
            placeholder="Any relevant medical information"
          />
        </div>
        <div className="space-y-2">
          <Label htmlFor="emergency-contact">Emergency Contact</Label>
          <Input
            id="emergency-contact"
            placeholder="Name: John Doe, Relation: Spouse, Phone: +1 (555) 987-6543"
          />
        </div>
        <div className="flex items-center space-x-2">
          <Checkbox id="hazmat" />
          <Label htmlFor="hazmat">Hazardous Materials Endorsement</Label>
        </div>
        <div className="flex items-center space-x-2">
          <Checkbox id="tanker" />
          <Label htmlFor="tanker">Tanker Endorsement</Label>
        </div>
        <div className="flex items-center space-x-2">
          <Checkbox id="passenger" />
          <Label htmlFor="passenger">Passenger Endorsement</Label>
        </div>
      </div>
    </div>
  );
}
