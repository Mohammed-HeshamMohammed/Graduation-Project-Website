"use client";

import { BarChart } from "lucide-react";
import { DemoBadge } from "@/components/demo-dashboard/sections/Dashboard/demo-badge";

export function HeaderSection() {
  return (
    <div className="bg-gradient-to-r from-purple-900 to-indigo-900 p-6 shadow-lg">
      <div className="max-w-7xl mx-auto flex justify-between items-center">
        <h1 className="text-3xl text-white font-bold flex items-center">
          <BarChart className="mr-2 h-8 w-8 text-purple-300" />
          Logistics Dashboard
        </h1>
        <DemoBadge />
      </div>
    </div>
  );
}