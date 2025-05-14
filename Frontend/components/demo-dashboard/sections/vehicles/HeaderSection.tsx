"use client";

import { useRouter } from "next/navigation";
import { Button } from "@/components/ui/button";
import { Plus, Car } from "lucide-react";
import { DemoBadge } from "@/components/demo-dashboard/demo-badge";

export function HeaderSection({ router }: { router: ReturnType<typeof useRouter> }) {
  return (
    <div className="flex justify-between items-center p-6 border-b border-purple-500/30 bg-gradient-to-r from-gray-800 via-gray-700 to-gray-800">
      <div className="flex items-center gap-3">
        <div className="p-2 bg-purple-900/50 rounded-full">
          <Car className="h-6 w-6 text-purple-300" />
        </div>
        <h1 className="text-2xl font-bold text-transparent bg-clip-text bg-gradient-to-r from-purple-400 to-pink-300">Vehicles</h1>
      </div>
      <div className="flex gap-2">
        <Button
          className="bg-gradient-to-r from-purple-600 to-indigo-600 hover:from-purple-700 hover:to-indigo-700 text-white border border-purple-400/30"
          onClick={() => router.push("/demo-dashboard/vehicles/add")}
        >
          <Plus className="mr-2 h-4 w-4" /> Add Vehicle
        </Button>
        <DemoBadge />
      </div>
    </div>
  );
}