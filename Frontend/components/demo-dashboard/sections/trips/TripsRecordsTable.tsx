"use client";

import { useRouter } from "next/navigation";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { Search, Filter, MoreHorizontal, MapPin, Truck, User, ChevronRight, Calendar, CheckCircle2, Clock, AlertTriangle } from "lucide-react";
import { DropdownMenu, DropdownMenuContent, DropdownMenuItem, DropdownMenuLabel, DropdownMenuSeparator, DropdownMenuTrigger } from "@/components/ui/dropdown-menu";
import { Badge } from "@/components/ui/badge";
import Image from "next/image";
import { useToast } from "@/components/ui/use-toast";

// Define the Trip interface here instead of importing it
export interface Trip {
  id: string;
  startLocation: string;
  endLocation: string;
  driverName: string;
  truckCode: string;
  loadType: string;
  startTime: string | null;
  status: "completed" | "in_progress" | "scheduled" | "cancelled";
}

interface TripsRecordsTableProps {
  trips: Trip[];
  searchTerm: string;
  setSearchTerm: (s: string) => void;
  formatDate: (dateString: string | null) => string;
  toast: any;
}

export function TripsRecordsTable({
  trips,
  searchTerm,
  setSearchTerm,
  formatDate,
  toast,
}: TripsRecordsTableProps) {
  const router = useRouter();

  return (
    <Card>
      <CardHeader>
        <div className="flex items-center justify-between">
          <div>
            <CardTitle>Trip Records</CardTitle>
            <p className="text-sm text-muted-foreground">View and manage all trips</p>
          </div>
          <div className="flex items-center space-x-2">
            <div className="relative">
              <Search className="absolute left-2.5 top-2.5 h-4 w-4 text-indigo-400" />
              <Input
                type="search"
                placeholder="Search trips..."
                className="pl-8 w-64 bg-gray-800 border-gray-700 focus:border-indigo-500 focus:ring-indigo-500 text-gray-200"
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
              />
            </div>
            <Button variant="outline" size="icon" className="border-gray-700 text-indigo-400 hover:bg-gray-700">
              <Filter className="h-4 w-4" />
              <span className="sr-only">Filter</span>
            </Button>
          </div>
        </div>
      </CardHeader>
      <CardContent>
        <Tabs defaultValue="all" className="border rounded-md">
          <TabsList className="mb-4">
            <TabsTrigger value="all">All Trips</TabsTrigger>
            <TabsTrigger value="completed">Completed</TabsTrigger>
            <TabsTrigger value="in_progress">In Progress</TabsTrigger>
            <TabsTrigger value="scheduled">Scheduled</TabsTrigger>
            <TabsTrigger value="cancelled">Cancelled</TabsTrigger>
          </TabsList>
          <TabsContent value="all" className="pt-4">
            <Table>
              <TableHeader className="bg-gray-800">
                <TableRow className="border-b border-gray-700">
                  <TableHead className="text-indigo-300">ID</TableHead>
                  <TableHead className="text-indigo-300">Route</TableHead>
                  <TableHead className="text-indigo-300">Driver</TableHead>
                  <TableHead className="text-indigo-300">Vehicle</TableHead>
                  <TableHead className="text-indigo-300">Load Type</TableHead>
                  <TableHead className="text-indigo-300">Start Time</TableHead>
                  <TableHead className="text-indigo-300">Status</TableHead>
                  <TableHead className="text-right text-indigo-300">Actions</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {trips.length === 0 ? (
                  <TableRow>
                    <TableCell colSpan={8} className="text-center py-10 text-gray-400">
                      No trips found
                    </TableCell>
                  </TableRow>
                ) : (
                  trips.map((trip, index) => (
                    <TableRow key={trip.id} className={`${index % 2 === 0 ? "bg-gray-800" : "bg-gray-750"} hover:bg-gray-700`}>
                      <TableCell className="font-medium text-indigo-300">#{trip.id}</TableCell>
                      <TableCell>
                        <div className="flex items-center">
                          <MapPin className="h-4 w-4 text-violet-400 mr-1" />
                          <span className="text-gray-300">
                            {trip.startLocation} → {trip.endLocation}
                          </span>
                        </div>
                      </TableCell>
                      <TableCell>
                        <div className="flex items-center">
                          <User className="h-4 w-4 text-sky-400 mr-1" />
                          <span className="text-gray-300">{trip.driverName}</span>
                        </div>
                      </TableCell>
                      <TableCell>
                        <div className="flex items-center">
                          <Truck className="h-4 w-4 text-emerald-400 mr-1" />
                          <span className="text-gray-300">{trip.truckCode}</span>
                        </div>
                      </TableCell>
                      <TableCell className="text-gray-300">{trip.loadType}</TableCell>
                      <TableCell className="text-gray-300">{formatDate(trip.startTime)}</TableCell>
                      <TableCell>
                        {(() => {
                          switch (trip.status) {
                            case "completed":
                              return (
                                <Badge variant="outline" className="bg-emerald-900/20 text-emerald-400 hover:bg-emerald-900/30 border-emerald-800">
                                  <CheckCircle2 className="mr-1 h-3 w-3" /> Completed
                                </Badge>
                              );
                            case "in_progress":
                              return (
                                <Badge variant="outline" className="bg-indigo-900/20 text-indigo-400 hover:bg-indigo-900/30 border-indigo-800">
                                  <Clock className="mr-1 h-3 w-3" /> In Progress
                                </Badge>
                              );
                            case "scheduled":
                              return (
                                <Badge variant="outline" className="bg-amber-900/20 text-amber-400 hover:bg-amber-900/30 border-amber-800">
                                  <Calendar className="mr-1 h-3 w-3" /> Scheduled
                                </Badge>
                              );
                            case "cancelled":
                              return (
                                <Badge variant="outline" className="bg-rose-900/20 text-rose-400 hover:bg-rose-900/30 border-rose-800">
                                  <AlertTriangle className="mr-1 h-3 w-3" /> Cancelled
                                </Badge>
                              );
                            default:
                              return <Badge variant="outline">Unknown</Badge>;
                          }
                        })()}
                      </TableCell>
                      <TableCell className="text-right">
                        <DropdownMenu>
                          <DropdownMenuTrigger asChild>
                            <Button variant="ghost" size="icon" className="text-indigo-400 hover:text-indigo-300 hover:bg-gray-700">
                              <MoreHorizontal className="h-4 w-4" />
                              <span className="sr-only">Actions</span>
                            </Button>
                          </DropdownMenuTrigger>
                          <DropdownMenuContent align="end" className="border-gray-700 bg-gray-800">
                            <DropdownMenuLabel className="text-indigo-300">Actions</DropdownMenuLabel>
                            <DropdownMenuItem onClick={() => toast({ title: "View Details" })} className="text-gray-300 focus:bg-gray-700 focus:text-indigo-300">
                              View Details
                            </DropdownMenuItem>
                            <DropdownMenuItem onClick={() => toast({ title: "Edit Trip" })} className="text-gray-300 focus:bg-gray-700 focus:text-indigo-300">
                              Edit Trip
                            </DropdownMenuItem>
                            <DropdownMenuSeparator className="bg-gray-700" />
                            <DropdownMenuItem onClick={() => toast({ title: "Track Location" })} className="text-gray-300 focus:bg-gray-700 focus:text-indigo-300">
                              Track Location
                            </DropdownMenuItem>
                            <DropdownMenuItem onClick={() => toast({ title: "View Documents" })} className="text-gray-300 focus:bg-gray-700 focus:text-indigo-300">
                              View Documents
                            </DropdownMenuItem>
                            <DropdownMenuSeparator className="bg-gray-700" />
                            <DropdownMenuItem onClick={() => toast({ title: "Cancel Trip" })} className="text-rose-400 focus:bg-gray-700 focus:text-rose-300">
                              Cancel Trip
                            </DropdownMenuItem>
                          </DropdownMenuContent>
                        </DropdownMenu>
                      </TableCell>
                    </TableRow>
                  ))
                )}
              </TableBody>
            </Table>
          </TabsContent>
        </Tabs>
      </CardContent>
      <div className="border-t pt-6 flex items-center justify-between">
        <div className="text-sm text-muted-foreground">
          Showing {trips.length} of {trips.length} records
        </div>
        <div className="flex gap-2">
          <Button variant="outline" size="sm" disabled>
            Previous
          </Button>
          <Button variant="outline" size="sm" disabled>
            Next
          </Button>
        </div>
      </div>
    </Card>
  );
}