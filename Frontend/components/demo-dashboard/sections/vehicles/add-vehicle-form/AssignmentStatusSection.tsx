// components/demo-dashboard/vehicles/add-vehicle-form/AssignmentStatusSection.tsx
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

export function AssignmentStatusSection() {
  return (
    <div className="space-y-2">
      <h3 className="text-lg font-medium">Assignment & Status</h3>
      <div className="grid gap-4 md:grid-cols-2">
        <div className="space-y-2">
          <Label htmlFor="garage">Assigned Garage</Label>
          <Select defaultValue="main">
            <SelectTrigger id="garage">
              <SelectValue placeholder="Select garage" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="main">Main Depot</SelectItem>
              <SelectItem value="north">North Depot</SelectItem>
              <SelectItem value="south">South Depot</SelectItem>
              <SelectItem value="east">East Depot</SelectItem>
              <SelectItem value="west">West Depot</SelectItem>
            </SelectContent>
          </Select>
        </div>
        <div className="space-y-2">
          <Label htmlFor="status">Status</Label>
          <Select defaultValue="active">
            <SelectTrigger id="status">
              <SelectValue placeholder="Select status" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="active">Active</SelectItem>
              <SelectItem value="maintenance">In Maintenance</SelectItem>
              <SelectItem value="inactive">Inactive</SelectItem>
            </SelectContent>
          </Select>
        </div>
        <div className="space-y-2">
          <Label htmlFor="purchase-date">Purchase Date</Label>
          <Input id="purchase-date" type="date" />
        </div>
        <div className="space-y-2">
          <Label htmlFor="purchase-price">Purchase Price</Label>
          <Input id="purchase-price" type="number" min="0" placeholder="150000" />
        </div>
      </div>
    </div>
  );
}
