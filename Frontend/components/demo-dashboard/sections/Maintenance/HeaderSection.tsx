// components/demo-dashboard/MaintenanceDashboard/HeaderSection.tsx
"use client";

import { useRouter } from "next/navigation";
import { Button } from "@/components/ui/button";
import { PlusCircle, Settings } from "lucide-react";
import { DemoBadge } from "@/components/demo-dashboard/demo-badge";

export function HeaderSection({ router }: { router: ReturnType<typeof useRouter> }) {
  return (
    <div className="flex items-center justify-between mb-8 bg-gray-900 p-6 rounded-lg">
      <div>
        <h1 className="text-3xl font-bold text-white tracking-tight">Fleet Maintenance</h1>
        <p className="text-gray-400 mt-1">
          Monitor and manage maintenance activities for your fleet
        </p>
      </div>
      <div className="flex items-center gap-4">
        <Button 
          onClick={() => router.push("/demo-dashboard/maintenance/new")}
          className="bg-indigo-600 hover:bg-indigo-700 text-white"
        >
          <PlusCircle className="mr-2 h-4 w-4" /> New Record
        </Button>
        <Button 
          variant="outline" 
          className="border-gray-600 text-gray-300 hover:bg-gray-700 hover:text-gray-200"
        >
          <Settings className="h-4 w-4" /> Settings
        </Button>
        <DemoBadge />
      </div>
    </div>
  );
}