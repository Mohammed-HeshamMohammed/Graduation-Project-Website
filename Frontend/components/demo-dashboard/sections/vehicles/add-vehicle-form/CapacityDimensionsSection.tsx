// components/demo-dashboard/vehicles/add-vehicle-form/CapacityDimensionsSection.tsx
"use client";

import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";

export function CapacityDimensionsSection() {
  return (
    <div className="space-y-2">
      <h3 className="text-lg font-medium">Capacity & Dimensions</h3>
      <div className="grid gap-4 md:grid-cols-2">
        <div className="space-y-2">
          <Label htmlFor="load-capacity">Load Capacity (kg)</Label>
          <Input id="load-capacity" type="number" min="0" placeholder="25000" />
        </div>
        <div className="space-y-2">
          <Label htmlFor="axles">Number of Axles</Label>
          <Input id="axles" type="number" min="2" max="10" placeholder="3" />
        </div>
        <div className="space-y-2">
          <Label htmlFor="length">Length (m)</Label>
          <Input id="length" type="number" min="0" step="0.01" placeholder="16.5" />
        </div>
        <div className="space-y-2">
          <Label htmlFor="width">Width (m)</Label>
          <Input id="width" type="number" min="0" step="0.01" placeholder="2.5" />
        </div>
        <div className="space-y-2">
          <Label htmlFor="height">Height (m)</Label>
          <Input id="height" type="number" min="0" step="0.01" placeholder="4.0" />
        </div>
        <div className="space-y-2">
          <Label htmlFor="weight">Empty Weight (kg)</Label>
          <Input id="weight" type="number" min="0" placeholder="9000" />
        </div>
      </div>
    </div>
  );
}
