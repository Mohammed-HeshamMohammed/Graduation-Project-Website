// components/sections/drivers/add-driver-form/Form.tsx
"use client";

import React, { useState } from "react";
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Separator } from "@/components/ui/separator";
import { useToast } from "@/components/ui/use-toast";

// Import the subsections
import { PersonalInfoSection } from "./PersonalInfoSection";
import { LicenseInfoSection } from "./LicenseInfoSection";
import { EmploymentDetailsSection } from "./EmploymentDetailsSection";
import { AdditionalInfoSection } from "./AdditionalInfoSection";

export function AddDriverForm({ onSuccess }: { onSuccess?: () => void }) {
  const [isLoading, setIsLoading] = useState(false);
  const { toast } = useToast();

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    setIsLoading(true);

    // Simulate API call
    setTimeout(() => {
      setIsLoading(false);
      toast({
        title: "Driver added",
        description: "The driver has been added successfully.",
        duration: 3000,
      });
      if (onSuccess) onSuccess();
    }, 1500);
  };

  return (
    <Card>
      <CardHeader>
        <CardTitle>Add New Driver</CardTitle>
        <CardDescription>Enter driver details to add them to your fleet</CardDescription>
      </CardHeader>
      <form onSubmit={handleSubmit}>
        <CardContent className="space-y-4">
          <PersonalInfoSection />
          <Separator />
          <LicenseInfoSection />
          <Separator />
          <EmploymentDetailsSection />
          <Separator />
          <AdditionalInfoSection />
        </CardContent>
        <CardFooter className="flex justify-end space-x-2">
          <Button variant="outline" type="button">
            Cancel
          </Button>
          <Button type="submit" disabled={isLoading}>
            {isLoading ? "Adding Driver..." : "Add Driver"}
          </Button>
        </CardFooter>
      </form>
    </Card>
  );
}
