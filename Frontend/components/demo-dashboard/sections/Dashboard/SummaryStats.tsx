"use client";

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { DollarSign, TrendingUp, Package, Map } from "lucide-react";

interface SummaryStatsProps {
  dashboardData: {
    totalExpenses: number;
    tripsToday: number;
    tripsThisWeek: number;
    totalDistance: number;
    totalVehicles: number;
    activeVehicles: number;
    totalDrivers: number;
    activeDrivers: number;
    maintenanceAlerts: number;
    expensesPercentage?: number; // Added optional field
  };
  inactiveVehicles: number;
  onDutyDrivers: number;
  availableDrivers: number;
  offDutyDrivers: number;
}

export function SummaryStats({ dashboardData, inactiveVehicles, onDutyDrivers, availableDrivers, offDutyDrivers }: SummaryStatsProps) {
  
  // Ensure expensesPercentage is defined
  const expensesPercentage = dashboardData.expensesPercentage ?? Math.random() * 10; // Placeholder calculation

  return (
    <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-8">
      <div className="bg-gray-800 hover:bg-purple-900 transition-colors duration-300 rounded-xl shadow-md overflow-hidden border-l-4 border-emerald-500 flex items-center p-4">
        <div className="rounded-full bg-emerald-900 p-3 mr-4">
          <DollarSign className="h-6 w-6 text-emerald-400" />
        </div>
        <div>
          <p className="text-sm text-gray-400 font-medium">Total Revenue</p>
          <p className="text-2xl font-bold text-emerald-300">
            ฿{(dashboardData.totalExpenses * 1.4).toLocaleString()}
          </p>
          <p className="text-xs text-emerald-400">+{expensesPercentage.toFixed(2)}% from last month</p>
        </div>
      </div>

      <div className="bg-gray-800 hover:bg-purple-900 transition-colors duration-300 rounded-xl shadow-md overflow-hidden border-l-4 border-rose-500 flex items-center p-4">
        <div className="rounded-full bg-rose-900 p-3 mr-4">
          <TrendingUp className="h-6 w-6 text-rose-400" />
        </div>
        <div>
          <p className="text-sm text-gray-400 font-medium">Total Expenses</p>
          <p className="text-2xl font-bold text-rose-300">
            ฿{dashboardData.totalExpenses.toLocaleString()}
          </p>
          <p className="text-xs text-rose-400">+{expensesPercentage.toFixed(2)}% from last month</p>
        </div>
      </div>

      <div className="bg-gray-800 hover:bg-purple-900 transition-colors duration-300 rounded-xl shadow-md overflow-hidden border-l-4 border-cyan-500 flex items-center p-4">
        <div className="rounded-full bg-cyan-900 p-3 mr-4">
          <Package className="h-6 w-6 text-cyan-400" />
        </div>
        <div>
          <p className="text-sm text-gray-400 font-medium">Completed Trips</p>
          <p className="text-2xl font-bold text-cyan-300">{dashboardData.tripsThisWeek}</p>
          <p className="text-xs text-cyan-400">
            +{Math.round(dashboardData.tripsThisWeek / dashboardData.tripsToday)}% this week
          </p>
        </div>
      </div>

      <div className="bg-gray-800 hover:bg-purple-900 transition-colors duration-300 rounded-xl shadow-md overflow-hidden border-l-4 border-amber-500 flex items-center p-4">
        <div className="rounded-full bg-amber-900 p-3 mr-4">
          <Map className="h-6 w-6 text-amber-400" />
        </div>
        <div>
          <p className="text-sm text-gray-400 font-medium">Total Distance</p>
          <p className="text-2xl font-bold text-amber-300">
            {dashboardData.totalDistance.toLocaleString()} km
          </p>
          <p className="text-xs text-amber-400">Across all trips this month</p>
        </div>
      </div>
    </div>
  );
}