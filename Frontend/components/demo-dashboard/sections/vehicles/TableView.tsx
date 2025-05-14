"use client";

import React from "react";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { Badge } from "@/components/ui/badge";
import { Input } from "@/components/ui/input";
import Image from "next/image";
import { Truck, ChevronDown, MoreHorizontal } from "lucide-react";
import { Button } from "@/components/ui/button";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import { useToast } from "@/components/ui/use-toast";
import { Vehicle } from "@/components/demo-dashboard/mock-data";

interface TableViewProps {
  filteredGroups: [string, Vehicle[]][];
  vehicles: Vehicle[];
  setVehicles: (vehicles: Vehicle[]) => void;
}

// Function to get a color based on vehicle brand or status
const getBrandColor = (brand: string) => {
  const colors = {
    "Toyota": "bg-blue-700 text-blue-100",
    "Honda": "bg-green-700 text-green-100",
    "Ford": "bg-red-700 text-red-100",
    "BMW": "bg-yellow-700 text-yellow-100",
    "Mercedes": "bg-purple-700 text-purple-100",
    "Audi": "bg-pink-700 text-pink-100",
    "Nissan": "bg-indigo-700 text-indigo-100",
    "Hyundai": "bg-cyan-700 text-cyan-100",
    "default": "bg-blue-700 text-blue-100"
  };
  return colors[brand as keyof typeof colors] || colors.default;
};

const getStatusColor = (status: string) => {
  const colors = {
    "Available": "bg-green-700 text-green-100",
    "Rented": "bg-red-700 text-red-100",
    "Maintenance": "bg-yellow-700 text-yellow-100",
    "Reserved": "bg-purple-700 text-purple-100",
    "default": "bg-gray-700 text-gray-100"
  };
  return colors[status as keyof typeof colors] || colors.default;
};

const getGroupHeaderColor = (group: string, groupBy: string) => {
  if (groupBy === "brand") {
    return getBrandColor(group);
  } else if (groupBy === "status") {
    return getStatusColor(group);
  }
  return "bg-purple-800/50 text-purple-100";
};

export function TableView({ filteredGroups, vehicles, setVehicles }: TableViewProps) {
  const { toast } = useToast();

  // Example function to update a vehicle status (if needed)
  const handleUpdate = (id: number) => {
    // Update logic...
    toast({ 
      title: "Update", 
      description: "Vehicle updated",
      className: "bg-purple-800 text-purple-100 border-purple-500"
    });
  };

  return (
    <div>
      {filteredGroups.map(([group, vehicles]) => (
        <div key={group} className="mb-4 overflow-hidden rounded-lg shadow-lg">
          <div className="bg-gray-700 p-3 flex justify-between items-center border-b border-gray-600 bg-gradient-to-r from-gray-700 via-gray-800 to-gray-700">
            <div className="flex items-center gap-2">
              <Badge className={`${getGroupHeaderColor(group, "brand")}`}>{group}</Badge>
              <span className="text-sm font-medium text-gray-200">Count: <span className="font-bold text-purple-300">{vehicles.length}</span></span>
            </div>
            <div className="text-sm text-gray-200">Total Mileage: <span className="font-semibold text-cyan-300">{vehicles.reduce((sum, vehicle) => sum + vehicle.lastMileage, 0).toLocaleString()}</span></div>
          </div>
          <Table>
            <TableHeader className="bg-gray-700 bg-gradient-to-r from-gray-700 to-gray-800">
              <TableRow className="border-gray-600">
                <TableHead className="w-12 text-purple-200">#</TableHead>
                <TableHead className="text-purple-200">License Plate</TableHead>
                <TableHead className="text-purple-200">Brand</TableHead>
                <TableHead className="text-purple-200">Picture</TableHead>
                <TableHead className="text-purple-200">Model</TableHead>
                <TableHead className="text-purple-200">Rentals</TableHead>
                <TableHead className="text-purple-200">Status</TableHead>
                <TableHead className="text-purple-200">Last Mileage</TableHead>
                <TableHead></TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {vehicles.map((vehicle, index) => (
                <TableRow key={vehicle.id} className="hover:bg-gray-600/70 border-b border-gray-600 bg-gray-800/70">
                  <TableCell className="text-cyan-300 font-bold">{index + 1}</TableCell>
                  <TableCell className="font-medium text-cyan-100">{vehicle.licensePlate}</TableCell>
                  <TableCell>
                    <Badge className={getBrandColor(vehicle.brand)}>{vehicle.brand}</Badge>
                  </TableCell>
                  <TableCell>
                    <div className="relative h-14 w-20 rounded-md overflow-hidden border border-gray-600 shadow-sm">
                      <Image src={vehicle.image || "/placeholder.svg"} alt={vehicle.model} fill className="object-cover" />
                    </div>
                  </TableCell>
                  <TableCell className="font-medium text-pink-200">{vehicle.model}</TableCell>
                  <TableCell>
                    <div className="flex flex-wrap gap-1">
                      {vehicle.rentals.map((rental: string) => (
                        <Badge key={rental} variant="outline" className="text-xs text-amber-300 border-amber-600">{rental}</Badge>
                      ))}
                    </div>
                  </TableCell>
                  <TableCell>
                    <Badge className={`flex items-center ${getStatusColor(vehicle.status)}`}>
                      <Truck className="h-3 w-3 mr-1" />
                      {vehicle.status}
                    </Badge>
                  </TableCell>
                  <TableCell className="font-medium text-green-300">{vehicle.lastMileage.toLocaleString()} km</TableCell>
                  <TableCell>
                    <DropdownMenu>
                      <DropdownMenuTrigger asChild>
                        <Button variant="ghost" size="icon" className="h-8 w-8 text-purple-300 hover:bg-purple-900/50 hover:text-purple-200">
                          <MoreHorizontal className="h-4 w-4" />
                        </Button>
                      </DropdownMenuTrigger>
                      <DropdownMenuContent align="end" className="bg-gray-800 text-gray-200 border border-purple-500">
                        <DropdownMenuItem onClick={() => handleUpdate(vehicle.id)} className="hover:bg-purple-900/30 hover:text-purple-200">
                          View details
                        </DropdownMenuItem>
                        <DropdownMenuItem onClick={() => handleUpdate(vehicle.id)} className="hover:bg-purple-900/30 hover:text-purple-200">
                          Edit vehicle
                        </DropdownMenuItem>
                      </DropdownMenuContent>
                    </DropdownMenu>
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </div>
      ))}
    </div>
  );
}