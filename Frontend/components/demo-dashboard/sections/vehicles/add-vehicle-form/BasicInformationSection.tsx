// components/demo-dashboard/vehicles/add-vehicle-form/BasicInformationSection.tsx
"use client";

import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";

export function BasicInformationSection() {
  return (
    <div className="space-y-2">
      <h3 className="text-lg font-medium">Basic Information</h3>
      <div className="grid gap-4 md:grid-cols-2">
        <div className="space-y-2">
          <Label htmlFor="vehicle-code">Vehicle Code</Label>
          <Input id="vehicle-code" placeholder="TR-1001" required />
        </div>
        <div className="space-y-2">
          <Label htmlFor="license-plate">License Plate</Label>
          <Input id="license-plate" placeholder="ABC-1234" required />
        </div>
        <div className="space-y-2">
          <Label htmlFor="brand">Brand/Manufacturer</Label>
          <Input id="brand" placeholder="Volvo" required />
        </div>
        <div className="space-y-2">
          <Label htmlFor="model">Model</Label>
          <Input id="model" placeholder="FH16" required />
        </div>
        <div className="space-y-2">
          <Label htmlFor="year">Year</Label>
          <Input id="year" type="number" min="1900" max="2099" placeholder="2023" required />
        </div>
        <div className="space-y-2">
          <Label htmlFor="vin">VIN</Label>
          <Input id="vin" placeholder="1HGBH41JXMN109186" required />
        </div>
      </div>
    </div>
  );
}
