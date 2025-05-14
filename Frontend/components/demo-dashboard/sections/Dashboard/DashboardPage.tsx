"use client";

import { useState, useEffect } from "react";
import {
  dashboardData,
  chartData,
  mockVehicles,
  mockDrivers,
} from "@/components/demo-dashboard/mock-data";
import { DemoBadge } from "@/components/demo-dashboard/sections/Dashboard/demo-badge";

// Import section components
import { HeaderSection } from "@/components/demo-dashboard/sections/Dashboard/HeaderSection";
import { SummaryStats } from "@/components/demo-dashboard/sections/Dashboard/SummaryStats";
import { OperationalOverview } from "@/components/demo-dashboard/sections/Dashboard/OperationalOverview";
import { FinancialAnalytics } from "@/components/demo-dashboard/sections/Dashboard/FinancialAnalytics";
import { CargoAnalysis } from "@/components/demo-dashboard/sections/Dashboard/CargoAnalysis";

export function DashboardPage() {
  const [isLoading, setIsLoading] = useState(true);

  // Simulate loading delay
  useEffect(() => {
    const timer = setTimeout(() => setIsLoading(false), 1000);
    return () => clearTimeout(timer);
  }, []);

  // Derived data calculations (example for fleet status)
  const inactiveVehicles =
    dashboardData.totalVehicles -
    dashboardData.activeVehicles -
    dashboardData.maintenanceAlerts;
  const onDutyDrivers = Math.round(dashboardData.activeDrivers * 0.7);
  const availableDrivers = Math.round(dashboardData.activeDrivers * 0.3);
  const offDutyDrivers = dashboardData.totalDrivers - dashboardData.activeDrivers;

  if (isLoading) {
    return (
      <div className="flex items-center justify-center min-h-[calc(100vh-120px)] bg-gray-900">
        <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-purple-500"></div>
      </div>
    );
  }

  return (
    <div className="bg-gray-900 min-h-screen">
      {/* Dashboard Header */}
      <HeaderSection />

      <div className="max-w-7xl mx-auto p-6 bg-gray-900">
        {/* Overall Summary Stats */}
        <SummaryStats 
          dashboardData={dashboardData} 
          inactiveVehicles={inactiveVehicles} 
          onDutyDrivers={onDutyDrivers} 
          availableDrivers={availableDrivers} 
          offDutyDrivers={offDutyDrivers} 
        />

        {/* Operational Overview Section */}
        <OperationalOverview
          dashboardData={dashboardData}
          mockVehicles={mockVehicles}
        />

        {/* Financial Analytics Section */}
        <FinancialAnalytics 
          dashboardData={dashboardData} 
          chartData={chartData} 
        />

        {/* Cargo Analysis Section */}
        <CargoAnalysis 
          chartData={chartData} 
          dashboardData={dashboardData} 
        />
      </div>
    </div>
  );
}

export default DashboardPage;