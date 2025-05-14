"use client";

import { useRouter } from "next/navigation";
import { Button } from "@/components/ui/button";
import { Plus, Car } from "lucide-react";
import { DemoBadge } from "@/components/demo-dashboard/demo-badge";

export function HeaderSection({ router }: { router: ReturnType<typeof useRouter> }) {
  return (
    <div className="flex items-center justify-between mb-6">
      <div className="flex items-center gap-2">
        <Car className="h-6 w-6 text-indigo-300" />
        <h1 className="text-2xl font-bold text-indigo-300">Trips Dashboard</h1>
      </div>
      <div className="flex gap-2">
        <Button
          className="bg-indigo-600 hover:bg-indigo-700 text-white"
          onClick={() => router.push("/demo-dashboard/trips/add")}
        >
          <Plus className="mr-2 h-4 w-4" /> Add Trip
        </Button>
        <DemoBadge />
      </div>
    </div>
  );
}
