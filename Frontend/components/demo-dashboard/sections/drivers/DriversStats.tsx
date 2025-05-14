"use client";

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { User, CheckCircle, Car } from "lucide-react";

// Import mockDrivers and the Driver interface
import { mockDrivers, Driver } from "@/components/demo-dashboard/sections/drivers/mock-data";

export default function DriversStats() {
  const activeDrivers = mockDrivers.filter((d: Driver) => d.status === "active").length;
  const assignedDrivers = mockDrivers.filter((d: Driver) => d.assignedVehicle !== "Unassigned").length;
  const licenseAlerts = mockDrivers.filter((d: Driver) => {
    const today = new Date();
    const expiration = new Date(d.licenseExpDate);
    const daysUntilExpiration = Math.ceil((expiration.getTime() - today.getTime()) / (1000 * 60 * 60 * 24));
    return daysUntilExpiration < 30;
  }).length;
  const avgSafetyScore = Math.round(
    mockDrivers.reduce((sum: number, d: Driver) => sum + d.safetyScore, 0) / mockDrivers.length
  );

  return (
    <div className="grid gap-4 grid-cols-2 md:grid-cols-4">
      <Card className="overflow-hidden">
        <CardHeader className="flex flex-row items-center justify-between space-y-0 bg-gray-50 pb-2">
          <CardTitle className="text-blue-600 font-medium">Total Drivers</CardTitle>
          <User className="h-4 w-4 text-blue-600" />
        </CardHeader>
        <CardContent className="pt-4">
          <div className="text-2xl font-bold">{mockDrivers.length}</div>
          <p className="text-xs text-muted-foreground mt-1">Fleet capacity</p>
        </CardContent>
      </Card>

      <Card className="overflow-hidden">
        <CardHeader className="flex flex-row items-center justify-between space-y-0 bg-gray-50 pb-2">
          <CardTitle className="text-green-600 font-medium">Active Status</CardTitle>
          <CheckCircle className="h-4 w-4 text-green-600" />
        </CardHeader>
        <CardContent className="pt-4">
          <div className="text-2xl font-bold">{activeDrivers}</div>
          <p className="text-xs text-muted-foreground mt-1">
            {Math.round((activeDrivers / mockDrivers.length) * 100)}% active rate
          </p>
        </CardContent>
      </Card>

      <Card className="overflow-hidden">
        <CardHeader className="flex flex-row items-center justify-between space-y-0 bg-gray-50 pb-2">
          <CardTitle className="text-indigo-600 font-medium">Vehicle Assignment</CardTitle>
          <Car className="h-4 w-4 text-indigo-600" />
        </CardHeader>
        <CardContent className="pt-4">
          <div className="text-2xl font-bold">{assignedDrivers}</div>
          <p className="text-xs text-muted-foreground mt-1">
            {Math.round((assignedDrivers / mockDrivers.length) * 100)}% assignment rate
          </p>
        </CardContent>
      </Card>

      <Card className="overflow-hidden">
        <CardHeader className="flex flex-row items-center justify-between space-y-0 bg-gray-50 pb-2">
          <CardTitle className="text-green-800 font-medium">Safety Score</CardTitle>
          <Badge variant="outline" className="bg-green-100 text-green-800">
            {avgSafetyScore}
          </Badge>
        </CardHeader>
        <CardContent className="pt-4">
          <div className="text-2xl font-bold">{licenseAlerts}</div>
          <p className="text-xs text-muted-foreground mt-1">License alerts</p>
        </CardContent>
      </Card>
    </div>
  );
}