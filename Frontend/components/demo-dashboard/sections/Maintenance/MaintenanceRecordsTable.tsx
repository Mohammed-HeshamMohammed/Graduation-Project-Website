// components/demo-dashboard/MaintenanceDashboard/MaintenanceRecordsTable.tsx
"use client";

import { useRouter } from "next/navigation";
import { Card, CardContent, CardHeader, CardTitle, CardFooter } from "@/components/ui/card";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { Search, Filter, ChevronRight } from "lucide-react";

interface MaintenanceRecordsTableProps {
  searchTerm: string;
  setSearchTerm: (s: string) => void;
  activeFilter: string;
  setActiveFilter: (s: string) => void;
  filteredMaintenance: any[];
  totalRecords: number;
  handleMarkComplete: (id: number | string) => void;
  formatDate: (dateString: string) => string;
  formatCurrency: (amount: number) => string;
  getDaysUntil: (dateString: string) => number;
}

export function MaintenanceRecordsTable({
  searchTerm,
  setSearchTerm,
  activeFilter,
  setActiveFilter,
  filteredMaintenance,
  totalRecords,
  handleMarkComplete,
  formatDate,
  formatCurrency,
  getDaysUntil,
}: MaintenanceRecordsTableProps) {
  const router = useRouter();

  return (
    <Card className="bg-gray-800 border-gray-700 text-gray-200">
      <CardHeader>
        <div className="flex items-center justify-between">
          <div>
            <CardTitle className="text-gray-100">Maintenance Records</CardTitle>
            {/* You can add a description here if desired */}
          </div>
          <div className="flex items-center space-x-2">
            <div className="relative">
              <Search className="absolute left-2.5 top-2.5 h-4 w-4 text-gray-400" />
              <Input
                type="search"
                placeholder="Search records..."
                className="pl-8 w-64 bg-gray-700 border-gray-600 text-gray-200 placeholder-gray-400 focus:border-indigo-500"
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
              />
            </div>
            <Button variant="outline" size="icon" className="border-gray-600 text-gray-300 hover:bg-gray-700 hover:text-gray-200">
              <Filter className="h-4 w-4" />
            </Button>
          </div>
        </div>
      </CardHeader>
      <CardContent>
        <Tabs defaultValue="all" onValueChange={setActiveFilter} className="text-gray-200">
          <TabsList className="mb-4 bg-gray-700">
            <TabsTrigger value="all" className="data-[state=active]:bg-indigo-600 data-[state=active]:text-white">All Records</TabsTrigger>
            <TabsTrigger value="scheduled" className="data-[state=active]:bg-indigo-600 data-[state=active]:text-white">Scheduled</TabsTrigger>
            <TabsTrigger value="in_progress" className="data-[state=active]:bg-indigo-600 data-[state=active]:text-white">In Progress</TabsTrigger>
            <TabsTrigger value="completed" className="data-[state=active]:bg-indigo-600 data-[state=active]:text-white">Completed</TabsTrigger>
            <TabsTrigger value="overdue" className="data-[state=active]:bg-indigo-600 data-[state=active]:text-white">Overdue</TabsTrigger>
          </TabsList>
          <TabsContent value={activeFilter} className="pt-4">
            <Table>
              <TableHeader className="bg-gray-700 border-b border-gray-600">
                <TableRow>
                  <TableHead className="text-gray-300">Vehicle</TableHead>
                  <TableHead className="text-gray-300">Maintenance Type</TableHead>
                  <TableHead className="text-gray-300">Last Service</TableHead>
                  <TableHead className="text-gray-300">Next Service</TableHead>
                  <TableHead className="text-gray-300">Cost</TableHead>
                  <TableHead className="text-gray-300">Status</TableHead>
                  <TableHead className="text-gray-300">Actions</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {filteredMaintenance.length === 0 ? (
                  <TableRow className="border-b border-gray-700">
                    <TableCell colSpan={7} className="text-center py-10 text-gray-400">
                      No maintenance records found
                    </TableCell>
                  </TableRow>
                ) : (
                  filteredMaintenance.map((item: any) => (
                    <TableRow key={item.id} className="hover:bg-gray-700 border-b border-gray-700">
                      <TableCell className="text-gray-200">
                        <div className="flex items-center">
                          <div className="rounded-full bg-indigo-900 p-2 mr-2">
                            <ChevronRight className="h-4 w-4 text-indigo-400" />
                          </div>
                          <div>
                            <div className="font-medium text-gray-100">{item.truckCode}</div>
                            <div className="text-xs text-gray-400">{item.truckModel}</div>
                          </div>
                        </div>
                      </TableCell>
                      <TableCell className="text-gray-200">
                        <div className="font-medium text-gray-100">{item.type}</div>
                        <div className="text-xs text-gray-400">{item.garage}</div>
                      </TableCell>
                      <TableCell className="text-gray-200">{formatDate(item.lastMaintenanceDate)}</TableCell>
                      <TableCell className="text-gray-200">
                        <div className="flex flex-col">
                          <span>{formatDate(item.nextMaintenanceDate)}</span>
                          {getDaysUntil(item.nextMaintenanceDate) <= 0 ? (
                            <span className="text-xs text-red-400">Overdue</span>
                          ) : getDaysUntil(item.nextMaintenanceDate) <= 7 ? (
                            <span className="text-xs text-yellow-400">
                              Soon ({getDaysUntil(item.nextMaintenanceDate)} days)
                            </span>
                          ) : null}
                        </div>
                      </TableCell>
                      <TableCell className="text-gray-200">{formatCurrency(item.cost)}</TableCell>
                      <TableCell>
                        <span className={`px-2 py-1 rounded text-xs font-medium ${
                          item.status === "completed" ? "bg-green-900 text-green-300" :
                          item.status === "in_progress" ? "bg-indigo-900 text-indigo-300" :
                          item.status === "scheduled" ? "bg-yellow-900 text-yellow-300" :
                          "bg-red-900 text-red-300"
                        }`}>
                          {item.status}
                        </span>
                      </TableCell>
                      <TableCell>
                        <div className="flex gap-2">
                          <Button 
                            variant="outline" 
                            size="sm"
                            className="border-gray-600 text-gray-300 hover:bg-gray-700 hover:text-gray-100"
                            onClick={() => alert("Viewing details")}
                          >
                            Details
                          </Button>
                          {item.status !== "completed" && (
                            <Button
                              variant="outline"
                              size="sm"
                              className="text-green-400 border-green-800 hover:bg-green-900 hover:text-green-300"
                              onClick={() => handleMarkComplete(item.id)}
                            >
                              Complete
                            </Button>
                          )}
                        </div>
                      </TableCell>
                    </TableRow>
                  ))
                )}
              </TableBody>
            </Table>
          </TabsContent>
        </Tabs>
      </CardContent>
      <CardFooter className="flex items-center justify-between border-t border-gray-700 pt-6">
        <div className="text-sm text-gray-400">
          Showing {filteredMaintenance.length} of {totalRecords} records
        </div>
        <div className="flex gap-2">
          <Button 
            variant="outline" 
            size="sm" 
            disabled
            className="border-gray-600 text-gray-400 hover:bg-gray-700 hover:text-gray-200 disabled:bg-gray-800 disabled:text-gray-600"
          >
            Previous
          </Button>
          <Button 
            variant="outline" 
            size="sm" 
            disabled
            className="border-gray-600 text-gray-400 hover:bg-gray-700 hover:text-gray-200 disabled:bg-gray-800 disabled:text-gray-600"
          >
            Next
          </Button>
        </div>
      </CardFooter>
    </Card>
  );
}