// components/demo-dashboard/MaintenanceDashboard/OverviewCards.tsx
"use client";

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";

export function OverviewCards({
  totalRecords,
  inProgressCount,
  scheduledCount,
  completedCount,
  overdueCount,
  totalCost,
  formatCurrency,
}: {
  totalRecords: number;
  inProgressCount: number;
  scheduledCount: number;
  completedCount: number;
  overdueCount: number;
  totalCost: number;
  formatCurrency: (amount: number) => string;
}) {
  return (
    <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-4 mb-8">
      <Card>
        <CardHeader className="pb-2">
          <CardTitle className="text-sm font-medium text-muted-foreground">Total Records</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="text-2xl font-bold">{totalRecords}</div>
        </CardContent>
      </Card>
      <Card className="border-l-4 border-l-blue-500">
        <CardHeader className="pb-2">
          <CardTitle className="text-sm font-medium text-muted-foreground">In Progress</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="text-2xl font-bold">{inProgressCount}</div>
        </CardContent>
      </Card>
      <Card className="border-l-4 border-l-yellow-500">
        <CardHeader className="pb-2">
          <CardTitle className="text-sm font-medium text-muted-foreground">Scheduled</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="text-2xl font-bold">{scheduledCount}</div>
        </CardContent>
      </Card>
      <Card className="border-l-4 border-l-red-500">
        <CardHeader className="pb-2">
          <CardTitle className="text-sm font-medium text-muted-foreground">Overdue</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="text-2xl font-bold">{overdueCount}</div>
        </CardContent>
      </Card>
      <Card className="border-l-4 border-l-green-500">
        <CardHeader className="pb-2">
          <CardTitle className="text-sm font-medium text-muted-foreground">Completed</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="text-2xl font-bold">{completedCount}</div>
        </CardContent>
      </Card>
      <Card>
        <CardHeader className="pb-2">
          <CardTitle className="text-sm font-medium text-muted-foreground">Total Cost</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="text-2xl font-bold">{formatCurrency(totalCost)}</div>
        </CardContent>
      </Card>
    </div>
  );
}
