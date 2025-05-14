"use client";

import { Truck, Users } from "lucide-react";
import { Badge } from "@/components/ui/badge";
import { VehicleStatusSection } from "@/components/demo-dashboard/sections/Dashboard/vehicle-status-section";
import { TripsSection } from "@/components/demo-dashboard/sections/Dashboard/trips-section";

interface OperationalOverviewProps {
  dashboardData: {
    totalVehicles: number;
    activeVehicles: number;
    maintenanceAlerts: number;
    totalDrivers: number;
  };
  mockVehicles: any[];
}

export function OperationalOverview({ dashboardData, mockVehicles }: OperationalOverviewProps) {
  const inactiveVehicles =
    dashboardData.totalVehicles - dashboardData.activeVehicles - dashboardData.maintenanceAlerts;
  return (
    <div className="mb-8">
      <h2 className="text-xl font-bold text-gray-200 mb-4 flex items-center">
        <Truck className="mr-2 h-5 w-5 text-cyan-400" />
        Operational Overview
      </h2>
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div className="bg-gray-800 hover:bg-indigo-900 transition-colors duration-300 p-4 rounded-xl shadow-md">
          <h3 className="text-gray-400 font-medium mb-3 text-sm uppercase">Fleet Status</h3>
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <Badge className="bg-cyan-900 hover:bg-cyan-800 text-cyan-300">{dashboardData.activeVehicles} active</Badge>
              <Badge className="bg-amber-900 hover:bg-amber-800 text-amber-300">{dashboardData.maintenanceAlerts} maintenance</Badge>
              <Badge className="bg-gray-700 hover:bg-gray-600 text-gray-300">{inactiveVehicles} inactive</Badge>
            </div>
          </div>
          {/* Render the vehicle status chart/section */}
          <VehicleStatusSection
            activeVehicles={dashboardData.activeVehicles}
            maintenanceVehicles={dashboardData.maintenanceAlerts}
            inactiveVehicles={inactiveVehicles}
          />
        </div>
        <div className="bg-gray-800 hover:bg-indigo-900 transition-colors duration-300 p-4 rounded-xl shadow-md">
          <h3 className="text-gray-400 font-medium mb-3 text-sm uppercase">Trip Distribution</h3>
          {/* Render trips distribution chart */}
          <TripsSection data={[]} />
          {/* Pass chartData.tripsData if available */}
        </div>
      </div>
    </div>
  );
}