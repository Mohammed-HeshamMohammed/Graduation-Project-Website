// components/sections/drivers/add-driver-form/EmploymentDetailsSection.tsx
"use client";

import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";

export function EmploymentDetailsSection() {
  return (
    <div className="space-y-2">
      <h3 className="text-lg font-medium">Employment Details</h3>
      <div className="grid gap-4 md:grid-cols-2">
        <div className="space-y-2">
          <Label htmlFor="hire-date">Hire Date</Label>
          <Input id="hire-date" type="date" required />
        </div>
        <div className="space-y-2">
          <Label htmlFor="employee-id">Employee ID</Label>
          <Input id="employee-id" placeholder="EMP-12345" />
        </div>
        <div className="space-y-2">
          <Label htmlFor="experience">Years of Experience</Label>
          <Input id="experience" type="number" min="0" placeholder="5" />
        </div>
        <div className="space-y-2">
          <Label htmlFor="status">Employment Status</Label>
          <Select defaultValue="full-time">
            <SelectTrigger id="status">
              <SelectValue placeholder="Select status" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="full-time">Full-time</SelectItem>
              <SelectItem value="part-time">Part-time</SelectItem>
              <SelectItem value="contract">Contract</SelectItem>
              <SelectItem value="probation">Probation</SelectItem>
            </SelectContent>
          </Select>
        </div>
      </div>
    </div>
  );
}
