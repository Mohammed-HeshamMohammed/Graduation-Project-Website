// components/demo-dashboard/MaintenanceDashboard/MaintenanceOverview.tsx
"use client";

import { Card, CardContent, CardHeader, CardTitle, CardDescription, CardFooter } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Progress } from "@/components/ui/progress";
import {
  Calendar,
  Truck,
  Wrench,
  TrendingUp,
  CheckCircle,
  Clock,
  AlertCircle,
  ChevronRight
} from "lucide-react";

interface MaintenanceOverviewProps {
  maintenance: any[];
  formatDate: (dateString: string) => string;
  getDaysUntil: (dateString: string) => number;
  formatCurrency?: (amount: number) => string; // Add this prop to the interface
}

function UpcomingMaintenance({ maintenance, formatDate, getDaysUntil }: MaintenanceOverviewProps) {
  const upcoming = maintenance
    .filter(
      (m) =>
        (m.status === "scheduled" || m.status === "overdue") &&
        getDaysUntil(m.nextMaintenanceDate) <= 30
    )
    .sort(
      (a, b) => new Date(a.nextMaintenanceDate).getTime() - new Date(b.nextMaintenanceDate).getTime()
    )
    .slice(0, 5);
    
  return (
    <Card className="lg:col-span-1 bg-gray-800 border-gray-700 text-gray-200">
      <CardHeader>
        <CardTitle className="flex items-center text-gray-100">
          <Calendar className="mr-2 h-5 w-5 text-indigo-400" /> Upcoming Maintenance
        </CardTitle>
        <CardDescription className="text-gray-400">Next 30 days</CardDescription>
      </CardHeader>
      <CardContent className="px-2">
        <div className="space-y-4">
          {upcoming.length > 0 ? (
            upcoming.map((item: any) => (
              <div key={item.id} className="flex items-center p-3 rounded-lg hover:bg-gray-700 transition-colors">
                <div className="mr-4">
                  <div className={`rounded-full p-2 ${
                    getDaysUntil(item.nextMaintenanceDate) <= 0 ? "bg-red-900" : 
                    getDaysUntil(item.nextMaintenanceDate) <= 7 ? "bg-yellow-800" : "bg-indigo-900"
                  }`}>
                    <Truck className={`h-5 w-5 ${
                      getDaysUntil(item.nextMaintenanceDate) <= 0 ? "text-red-400" : 
                      getDaysUntil(item.nextMaintenanceDate) <= 7 ? "text-yellow-400" : "text-indigo-400"
                    }`} />
                  </div>
                </div>
                <div className="flex-1">
                  <p className="font-medium flex items-center text-gray-100">
                    {item.truckCode}
                    <span className="ml-2 text-xs px-2 py-1 rounded-full bg-gray-700">{item.type}</span>
                  </p>
                  <div className="flex items-center justify-between mt-1">
                    <p className="text-sm text-gray-400">{formatDate(item.nextMaintenanceDate)}</p>
                    <p className={`text-sm font-medium ${
                      getDaysUntil(item.nextMaintenanceDate) <= 0 ? "text-red-400" : 
                      getDaysUntil(item.nextMaintenanceDate) <= 7 ? "text-yellow-400" : "text-indigo-400"
                    }`}>
                      {getDaysUntil(item.nextMaintenanceDate) <= 0 ? "Overdue" : `${getDaysUntil(item.nextMaintenanceDate)} days`}
                    </p>
                  </div>
                </div>
                <Button variant="ghost" size="icon" className="ml-2 text-gray-300 hover:bg-gray-600 hover:text-gray-100">
                  <ChevronRight className="h-4 w-4" />
                </Button>
              </div>
            ))
          ) : (
            <div className="text-center py-8 text-gray-400">
              No upcoming maintenance in the next 30 days
            </div>
          )}
        </div>
      </CardContent>
      <CardFooter className="flex justify-center border-t border-gray-700 pt-4">
        <Button variant="outline" className="w-full bg-gray-700 border-gray-600 text-gray-200 hover:bg-gray-600 hover:text-white">View All Scheduled</Button>
      </CardFooter>
    </Card>
  );
}

// Fixed the interface for MaintenanceTypes component
function MaintenanceTypes({ maintenance, formatCurrency }: { maintenance: any[]; formatCurrency?: (amount: number) => string; }) {
  const types: Record<string, number> = {};
  maintenance.forEach(item => {
    types[item.type] = (types[item.type] || 0) + 1;
  });
  const totalRecords = maintenance.length;
  const sortedTypes = Object.entries(types).sort((a, b) => b[1] - a[1]);
  
  return (
    <Card className="lg:col-span-1 bg-gray-800 border-gray-700 text-gray-200">
      <CardHeader>
        <CardTitle className="flex items-center text-gray-100">
          <Wrench className="mr-2 h-5 w-5 text-indigo-400" /> Maintenance by Type
        </CardTitle>
        <CardDescription className="text-gray-400">Distribution of maintenance categories</CardDescription>
      </CardHeader>
      <CardContent>
        <div className="space-y-6">
          {sortedTypes.map(([type, count]) => (
            <div key={type}>
              <div className="flex items-center justify-between mb-1">
                <span className="font-medium text-gray-200">{type}</span>
                <span className="text-sm text-gray-400">
                  {count} ({Math.round((count / totalRecords) * 100)}%)
                </span>
              </div>
              <div className="flex items-center gap-3">
                <Progress value={(count / totalRecords) * 100} className="h-2 bg-gray-700" />
                <span className="text-sm w-8 text-gray-300">{Math.round((count / totalRecords) * 100)}%</span>
              </div>
            </div>
          ))}
        </div>
      </CardContent>
      <CardFooter className="flex justify-center border-t border-gray-700 pt-4">
        <Button variant="outline" className="w-full bg-gray-700 border-gray-600 text-gray-200 hover:bg-gray-600 hover:text-white">View Analysis</Button>
      </CardFooter>
    </Card>
  );
}

function MaintenanceSummary({ maintenance }: { maintenance: any[] }) {
  const totalRecords = maintenance.length;
  const inProgressCount = maintenance.filter(m => m.status === "in_progress").length;
  const completedCount = maintenance.filter(m => m.status === "completed").length;
  
  return (
    <Card className="lg:col-span-1 bg-gray-800 border-gray-700 text-gray-200">
      <CardHeader>
        <CardTitle className="flex items-center text-gray-100">
          <TrendingUp className="mr-2 h-5 w-5 text-indigo-400" /> Maintenance Summary
        </CardTitle>
        <CardDescription className="text-gray-400">Key metrics and trends</CardDescription>
      </CardHeader>
      <CardContent>
        <div className="space-y-6">
          <div className="grid grid-cols-2 gap-4">
            <div className="bg-gray-700 rounded-lg p-3">
              <div className="flex items-center justify-between">
                <div className="rounded-full bg-green-900 p-1.5">
                  <CheckCircle className="h-4 w-4 text-green-400" />
                </div>
                <span className="text-sm text-gray-400">Completed</span>
              </div>
              <p className="text-2xl font-bold mt-2 text-gray-100">{completedCount}</p>
            </div>
            <div className="bg-gray-700 rounded-lg p-3">
              <div className="flex items-center justify-between">
                <div className="rounded-full bg-indigo-900 p-1.5">
                  <Clock className="h-4 w-4 text-indigo-400" />
                </div>
                <span className="text-sm text-gray-400">In Progress</span>
              </div>
              <p className="text-2xl font-bold mt-2 text-gray-100">{inProgressCount}</p>
            </div>
            <div className="bg-gray-700 rounded-lg p-3">
              <div className="flex items-center justify-between">
                <div className="rounded-full bg-yellow-900 p-1.5">
                  <Calendar className="h-4 w-4 text-yellow-400" />
                </div>
                <span className="text-sm text-gray-400">Scheduled</span>
              </div>
              <p className="text-2xl font-bold mt-2 text-gray-100">{maintenance.filter(m => m.status === "scheduled").length}</p>
            </div>
            <div className="bg-gray-700 rounded-lg p-3">
              <div className="flex items-center justify-between">
                <div className="rounded-full bg-red-900 p-1.5">
                  <AlertCircle className="h-4 w-4 text-red-400" />
                </div>
                <span className="text-sm text-gray-400">Overdue</span>
              </div>
              <p className="text-2xl font-bold mt-2 text-gray-100">{maintenance.filter(m => m.status === "overdue").length}</p>
            </div>
          </div>
          <div className="mt-4">
            <h4 className="text-sm font-medium mb-2 text-gray-300">Average Cost by Type</h4>
            {/* Calculation of average cost by type here */}
            {/* You can further refactor this if needed */}
          </div>
        </div>
      </CardContent>
      <CardFooter className="flex justify-center border-t border-gray-700 pt-4">
        <Button variant="outline" className="w-full bg-gray-700 border-gray-600 text-gray-200 hover:bg-gray-600 hover:text-white">Generate Report</Button>
      </CardFooter>
    </Card>
  );
}

// Update the MaintenanceOverview function to pass the formatCurrency prop
export function MaintenanceOverview({ maintenance, formatDate, getDaysUntil, formatCurrency }: MaintenanceOverviewProps) {
  return (
    <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-8">
      <UpcomingMaintenance maintenance={maintenance} formatDate={formatDate} getDaysUntil={getDaysUntil} formatCurrency={formatCurrency} />
      <MaintenanceTypes maintenance={maintenance} formatCurrency={formatCurrency} />
      <MaintenanceSummary maintenance={maintenance} />
    </div>
  );
}