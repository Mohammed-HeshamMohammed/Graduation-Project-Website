// components/demo-dashboard/vehicles/add-vehicle-form/Form.tsx
"use client";

import React, { useState } from "react";
import {
  Card,
  CardContent,
  CardDescription,
  CardFooter,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Separator } from "@/components/ui/separator";
import { useToast } from "@/components/ui/use-toast";

// Import our subsections
import { BasicInformationSection } from "./BasicInformationSection";
import { TechnicalSpecificationsSection } from "./TechnicalSpecificationsSection";
import { CapacityDimensionsSection } from "./CapacityDimensionsSection";
import { AssignmentStatusSection } from "./AssignmentStatusSection";
import { AdditionalInformationSection } from "./AdditionalInformationSection";

export function AddVehicleForm({ onSuccess }: { onSuccess?: () => void }) {
  const [isLoading, setIsLoading] = useState(false);
  const { toast } = useToast();

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    setIsLoading(true);
    // Simulate API call delay
    setTimeout(() => {
      setIsLoading(false);
      toast({
        title: "Vehicle added",
        description: "The vehicle has been added successfully.",
        duration: 3000,
      });
      if (onSuccess) onSuccess();
    }, 1500);
  };

  return (
    <Card>
      <CardHeader>
        <CardTitle>Add New Vehicle</CardTitle>
        <CardDescription>Enter vehicle details to add it to your fleet</CardDescription>
      </CardHeader>
      <form onSubmit={handleSubmit}>
        <CardContent className="space-y-4">
          <BasicInformationSection />
          <Separator />
          <TechnicalSpecificationsSection />
          <Separator />
          <CapacityDimensionsSection />
          <Separator />
          <AssignmentStatusSection />
          <Separator />
          <AdditionalInformationSection />
        </CardContent>
        <CardFooter className="flex justify-end space-x-2">
          <Button variant="outline" type="button">
            Cancel
          </Button>
          <Button type="submit" disabled={isLoading}>
            {isLoading ? "Adding Vehicle..." : "Add Vehicle"}
          </Button>
        </CardFooter>
      </form>
    </Card>
  );
}
