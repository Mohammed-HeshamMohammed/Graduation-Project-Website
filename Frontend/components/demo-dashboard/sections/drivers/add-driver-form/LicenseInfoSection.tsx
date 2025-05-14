// components/sections/drivers/add-driver-form/LicenseInfoSection.tsx
"use client";

import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";

export function LicenseInfoSection() {
  return (
    <div className="space-y-2">
      <h3 className="text-lg font-medium">License Information</h3>
      <div className="grid gap-4 md:grid-cols-2">
        <div className="space-y-2">
          <Label htmlFor="license-number">License Number</Label>
          <Input id="license-number" placeholder="DL12345678" required />
        </div>
        <div className="space-y-2">
          <Label htmlFor="license-type">License Type</Label>
          <Select defaultValue="cdl-a">
            <SelectTrigger id="license-type">
              <SelectValue placeholder="Select license type" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="cdl-a">CDL Class A</SelectItem>
              <SelectItem value="cdl-b">CDL Class B</SelectItem>
              <SelectItem value="cdl-c">CDL Class C</SelectItem>
              <SelectItem value="non-cdl">Non-CDL</SelectItem>
            </SelectContent>
          </Select>
        </div>
        <div className="space-y-2">
          <Label htmlFor="license-expiry">License Expiry Date</Label>
          <Input id="license-expiry" type="date" required />
        </div>
        <div className="space-y-2">
          <Label htmlFor="license-state">Issuing State/Country</Label>
          <Input id="license-state" placeholder="California" required />
        </div>
      </div>
    </div>
  );
}
