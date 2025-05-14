// components/demo-dashboard/vehicles/add-vehicle-form/TechnicalSpecificationsSection.tsx
"use client";

import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";

export function TechnicalSpecificationsSection() {
  return (
    <div className="space-y-2">
      <h3 className="text-lg font-medium">Technical Specifications</h3>
      <div className="grid gap-4 md:grid-cols-2">
        <div className="space-y-2">
          <Label htmlFor="engine-type">Engine Type</Label>
          <Input id="engine-type" placeholder="Diesel D13TC" />
        </div>
        <div className="space-y-2">
          <Label htmlFor="horsepower">Horsepower</Label>
          <Input id="horsepower" type="number" min="0" placeholder="500" />
        </div>
        <div className="space-y-2">
          <Label htmlFor="transmission">Transmission Type</Label>
          <Select defaultValue="automatic">
            <SelectTrigger id="transmission">
              <SelectValue placeholder="Select transmission type" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="automatic">Automatic</SelectItem>
              <SelectItem value="manual">Manual</SelectItem>
              <SelectItem value="semi-automatic">Semi-Automatic</SelectItem>
            </SelectContent>
          </Select>
        </div>
        <div className="space-y-2">
          <Label htmlFor="fuel-type">Fuel Type</Label>
          <Select defaultValue="diesel">
            <SelectTrigger id="fuel-type">
              <SelectValue placeholder="Select fuel type" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="diesel">Diesel</SelectItem>
              <SelectItem value="gasoline">Gasoline</SelectItem>
              <SelectItem value="electric">Electric</SelectItem>
              <SelectItem value="hybrid">Hybrid</SelectItem>
              <SelectItem value="cng">CNG</SelectItem>
              <SelectItem value="lpg">LPG</SelectItem>
            </SelectContent>
          </Select>
        </div>
        <div className="space-y-2">
          <Label htmlFor="fuel-capacity">Fuel Tank Capacity (L)</Label>
          <Input id="fuel-capacity" type="number" min="0" placeholder="600" />
        </div>
        <div className="space-y-2">
          <Label htmlFor="fuel-efficiency">Fuel Efficiency (km/L)</Label>
          <Input id="fuel-efficiency" type="number" min="0" step="0.1" placeholder="3.5" />
        </div>
      </div>
    </div>
  );
}
