"use client";

import { Card } from "@/components/ui/card";
import { CargoSection } from "@/components/demo-dashboard/sections/Dashboard/cargo-section";
import { TripMetricsSection } from "@/components/demo-dashboard/sections/Dashboard/trip-metrics-section";

interface CargoAnalysisProps {
  chartData: {
    cargoTypes: any[];
  };
  dashboardData: {
    totalDistance: number;
    returnTrips: number;
    oneWayTrips: number;
  };
}

export function CargoAnalysis({ chartData, dashboardData }: CargoAnalysisProps) {
  return (
    <div className="mb-8">
      <h2 className="text-xl font-bold text-gray-200 mb-4 flex items-center">
        Cargo Analysis
      </h2>
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <Card className="p-4 rounded-xl shadow-md bg-gray-800 hover:bg-teal-900 transition-colors duration-300 border-none">
          <h3 className="text-sm font-medium text-gray-400 uppercase mb-2">Cargo Distribution</h3>
          <CargoSection data={chartData.cargoTypes} />
        </Card>
        <Card className="p-4 rounded-xl shadow-md bg-gray-800 hover:bg-teal-900 transition-colors duration-300 border-none">
          <h3 className="text-sm font-medium text-gray-400 uppercase mb-2">Trip Metrics</h3>
          <div className="mb-4 grid grid-cols-2 gap-4">
            <div className="bg-gray-700 hover:bg-teal-800 transition-colors duration-300 p-3 rounded-lg">
              <p className="text-sm font-medium text-gray-400">Total Distance</p>
              <p className="text-xl font-bold text-gray-200 mt-1">{dashboardData.totalDistance.toLocaleString()} km</p>
            </div>
            <div className="bg-gray-700 hover:bg-teal-800 transition-colors duration-300 p-3 rounded-lg">
              <p className="text-sm font-medium text-gray-400">Total Trips</p>
              <p className="text-xl font-bold text-gray-200 mt-1">
                {dashboardData.oneWayTrips + dashboardData.returnTrips}
              </p>
            </div>
          </div>
          <TripMetricsSection
            totalDistance={dashboardData.totalDistance}
            returnTrips={dashboardData.returnTrips}
            oneWayTrips={dashboardData.oneWayTrips}
          />
        </Card>
      </div>
    </div>
  );
}