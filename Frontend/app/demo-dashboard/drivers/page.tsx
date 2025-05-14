"use client";

import DriversHeader from "@/components/demo-dashboard/sections/drivers/DriversHeader";
import DriversStats from "@/components/demo-dashboard/sections/drivers/DriversStats";
import DriversTable from "@/components/demo-dashboard/sections/drivers/DriversTable";

export default function DriversPage() {
  return (
    <div className="space-y-6">
      <DriversHeader />
      <DriversStats />
      <DriversTable />
    </div>
  );
}
