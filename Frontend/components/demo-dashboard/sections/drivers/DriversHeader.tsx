"use client";

import { useRouter } from "next/navigation";
import { Button } from "@/components/ui/button";
import { Download, Plus } from "lucide-react";
import { DemoBadge } from "@/components/demo-dashboard/demo-badge";

export default function DriversHeader() {
  const router = useRouter();

  return (
    <div className="flex justify-between items-center">
      <div>
        <h1 className="text-2xl text-black md:text-3xl font-bold">Fleet Drivers</h1>
        <p className="text-muted-foreground mt-1">Manage and monitor your driver roster</p>
      </div>
      <div className="flex gap-2">
        <Button variant="outline" onClick={() => router.push("/demo-dashboard/drivers/reports")}>
          <Download className="mr-2 h-4 w-4" /> Export
        </Button>
        <Button onClick={() => router.push("/demo-dashboard/drivers/add")}>
          <Plus className="mr-2 h-4 w-4" /> Add Driver
        </Button>
        <DemoBadge />
      </div>
    </div>
  );
}
