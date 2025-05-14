"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import {
  User,
  CheckCircle,
  Clock,
  AlertTriangle,
  Car,
  CalendarClock,
  MoreHorizontal,
  RefreshCw,
  Search,
} from "lucide-react";
import { Input } from "@/components/ui/input";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Avatar, AvatarFallback } from "@/components/ui/avatar";

// Import helper functions (create a helpers file as needed)
import { getStatusBadge, getLicenseStatus, getSafetyScoreBadge } from "@/components/demo-dashboard/sections/drivers/helpers";
import { mockDrivers } from "@/components/demo-dashboard/sections/drivers/mock-data";

export default function DriversTable() {
  const router = useRouter();
  const [searchTerm, setSearchTerm] = useState("");
  const [statusFilter, setStatusFilter] = useState("all");
  const [licenseFilter, setLicenseFilter] = useState("all");

  const filteredDrivers = mockDrivers.filter((driver) => {
    const matchesSearch =
      driver.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
      driver.licenseNum.toLowerCase().includes(searchTerm.toLowerCase()) ||
      driver.assignedVehicle.toLowerCase().includes(searchTerm.toLowerCase());

    const matchesStatus = statusFilter === "all" || driver.status === statusFilter;

    let matchesLicense = true;
    if (licenseFilter !== "all") {
      const today = new Date();
      const expiration = new Date(driver.licenseExpDate);
      const daysUntilExpiration = Math.ceil(
        (expiration.getTime() - today.getTime()) / (1000 * 60 * 60 * 24)
      );
      if (licenseFilter === "expired" && daysUntilExpiration >= 0) {
        matchesLicense = false;
      } else if (licenseFilter === "expiring" && (daysUntilExpiration < 0 || daysUntilExpiration >= 30)) {
        matchesLicense = false;
      } else if (licenseFilter === "valid" && daysUntilExpiration < 30) {
        matchesLicense = false;
      }
    }

    return matchesSearch && matchesStatus && matchesLicense;
  });

  return (
    <Card>
      <CardHeader className="pb-3">
        <CardTitle>Driver Management</CardTitle>
      </CardHeader>
      <CardContent>
        <Tabs defaultValue="roster" className="mb-6">
          <TabsList>
            <TabsTrigger value="roster">Driver Roster</TabsTrigger>
            <TabsTrigger value="licenses">License Management</TabsTrigger>
            <TabsTrigger value="assignments">Vehicle Assignments</TabsTrigger>
          </TabsList>
          
          <TabsContent value="roster" className="pt-4">
            <div className="flex flex-col md:flex-row justify-between gap-4 mb-6">
              <div className="flex flex-1 items-center relative">
                <Search className="absolute left-3 h-4 w-4 text-muted-foreground" />
                <Input
                  placeholder="Search by name, license, or vehicle..."
                  className="pl-10"
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                />
              </div>
              <div className="flex gap-2">
                <div className="w-40">
                  <Select value={statusFilter} onValueChange={setStatusFilter}>
                    <SelectTrigger>
                      <SelectValue placeholder="Status" />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="all">All Statuses</SelectItem>
                      <SelectItem value="active">Active</SelectItem>
                      <SelectItem value="inactive">Inactive</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
                <div className="w-40">
                  <Select value={licenseFilter} onValueChange={setLicenseFilter}>
                    <SelectTrigger>
                      <SelectValue placeholder="License" />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="all">All Licenses</SelectItem>
                      <SelectItem value="valid">Valid</SelectItem>
                      <SelectItem value="expiring">Expiring Soon</SelectItem>
                      <SelectItem value="expired">Expired</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
                <Button variant="ghost" size="icon">
                  <RefreshCw className="h-4 w-4" />
                </Button>
              </div>
            </div>
            
            <div className="rounded-md border overflow-hidden">
              <Table>
                <TableHeader className="bg-indigo bg-opacity-60">
                  <TableRow>
                    <TableHead>Driver</TableHead>
                    <TableHead>License</TableHead>
                    <TableHead>Status</TableHead>
                    <TableHead className="hidden md:table-cell">Experience</TableHead>
                    <TableHead className="hidden md:table-cell">Safety Score</TableHead>
                    <TableHead>Vehicle</TableHead>
                    <TableHead className="text-right">Actions</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {filteredDrivers.map((driver) => (
                    <TableRow key={driver.id} className="hover:bg-opacity-60 hover:text-blue-800">
                      <TableCell>
                        <div className="flex items-center gap-3">
                          <Avatar className="h-10 w-10 border">
                            <AvatarFallback className="text-sm bg-blue-100 text-blue-800">
                              {driver.avatarInitials}
                            </AvatarFallback>
                          </Avatar>
                          <div>
                            <div className="font-medium">{driver.name}</div>
                            <div className="text-sm text-muted-foreground hidden md:block">
                              {driver.contactNumber}
                            </div>
                          </div>
                        </div>
                      </TableCell>
                      <TableCell>
                        <div className="space-y-1">
                          <div className="text-sm">{driver.licenseNum}</div>
                          <div>{getLicenseStatus(driver.licenseExpDate)}</div>
                        </div>
                      </TableCell>
                      <TableCell>{getStatusBadge(driver.status)}</TableCell>
                      <TableCell className="hidden md:table-cell">{driver.experience}</TableCell>
                      <TableCell className="hidden md:table-cell">{getSafetyScoreBadge(driver.safetyScore)}</TableCell>
                      <TableCell>
                        {driver.assignedVehicle === "Unassigned" ? (
                          <span className="text-muted-foreground">Unassigned</span>
                        ) : (
                          <div className="space-y-1">
                            <div className="font-medium">{driver.assignedVehicle}</div>
                            <div className="text-sm text-muted-foreground">{driver.vehicleType}</div>
                          </div>
                        )}
                      </TableCell>
                      <TableCell className="text-right">
                        <Button variant="ghost" size="sm" onClick={() => router.push(`/demo-dashboard/drivers/${driver.id}`)}>
                          <MoreHorizontal className="h-4 w-4" />
                        </Button>
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </div>
            
            {filteredDrivers.length === 0 && (
              <div className="text-center py-8">
                <p className="text-muted-foreground">No drivers match your filters</p>
              </div>
            )}
            
            <div className="flex items-center justify-between mt-4">
              <p className="text-sm text-muted-foreground">
                Showing {filteredDrivers.length} of {mockDrivers.length} drivers
              </p>
              <div className="flex items-center gap-2">
                <Button variant="outline" size="sm" disabled>Previous</Button>
                <Button variant="outline" size="sm" disabled>Next</Button>
              </div>
            </div>
          </TabsContent>
          
          <TabsContent value="licenses" className="pt-4">
            <div className="p-8 text-center">
              <CalendarClock className="h-12 w-12 text-muted-foreground mx-auto mb-4" />
              <h3 className="text-lg font-medium mb-2">License Management View</h3>
              <p className="text-muted-foreground mb-4">
                Track and manage driver license expirations and renewals.
              </p>
              <Button variant="outline">View License Calendar</Button>
            </div>
          </TabsContent>
          
          <TabsContent value="assignments" className="pt-4">
            <div className="p-8 text-center">
              <Car className="h-12 w-12 text-muted-foreground mx-auto mb-4" />
              <h3 className="text-lg font-medium mb-2">Vehicle Assignment View</h3>
              <p className="text-muted-foreground mb-4">
                Manage vehicle assignments and driver rotations.
              </p>
              <Button variant="outline">Manage Assignments</Button>
            </div>
          </TabsContent>
        </Tabs>
      </CardContent>
    </Card>
  );
}
