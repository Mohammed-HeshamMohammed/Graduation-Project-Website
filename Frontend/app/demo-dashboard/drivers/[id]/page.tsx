// File: app/demo-dashboard/drivers/[id]/page.tsx
"use client";

import { Button } from "@/components/ui/button";
import { useRouter } from "next/navigation";
import { ArrowLeft } from "lucide-react";
import { useParams } from "next/navigation";

export default function DriverDetailsPage() {
  const router = useRouter();
  const params = useParams();
  const driverId = params.id;
  
  return (
    <div className="space-y-6">
      <div className="flex items-center gap-2 mb-6">
        <Button variant="ghost" onClick={() => router.back()}>
          <ArrowLeft className="h-4 w-4 mr-2" />
          Back to Drivers
        </Button>
      </div>
      
      <h1 className="text-2xl font-bold">Driver Details</h1>
      <p className="text-muted-foreground">Viewing details for driver ID: {driverId}</p>
      
      {/* Placeholder content for the driver details page */}
      <div className="p-8 bg-gray-50 rounded-lg border text-center">
        <h2 className="text-lg font-medium mb-2">Driver Profile</h2>
        <p className="text-muted-foreground">Full driver details will be implemented in a future update.</p>
      </div>
    </div>
  );
}