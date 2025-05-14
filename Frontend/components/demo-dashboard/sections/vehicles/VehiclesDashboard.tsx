"use client";

import { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import { useToast } from "@/components/ui/use-toast";
import { DemoBadge } from "@/components/demo-dashboard/demo-badge";
import { mockVehicles } from "@/components/demo-dashboard/mock-data";
import { Vehicle } from "@/components/demo-dashboard/mock-data"; 

// Import section components
import { HeaderSection } from "./HeaderSection";
import { Toolbar } from "./Toolbar";
import { TableView } from "./TableView";
import { GalleryView } from "./GalleryView";
import { TimelineView } from "./TimelineView";

export function VehiclesDashboard() {
  const router = useRouter();
  const { toast } = useToast();
  const [vehicles, setVehicles] = useState<Vehicle[]>(mockVehicles);
  const [searchTerm, setSearchTerm] = useState<string>("");
  const [groupBy, setGroupBy] = useState<keyof Vehicle>("brand");
  const [viewMode, setViewMode] = useState<"table" | "timeline" | "gallery">("table");
  const [isLoading, setIsLoading] = useState<boolean>(true);

  // Simulate API call delay
  useEffect(() => {
    const timer = setTimeout(() => setIsLoading(false), 1000);
    return () => clearTimeout(timer);
  }, []);

  // Group vehicles by the selected key
  const groupedVehicles = vehicles.reduce((acc: Record<string, Vehicle[]>, vehicle: Vehicle) => {
    const key = String(vehicle[groupBy]);
    if (!acc[key]) {
      acc[key] = [];
    }
    acc[key].push(vehicle);
    return acc;
  }, {});

  // Filter groups based on search term
  const filteredGroups = Object.entries(groupedVehicles).filter(([group, vehicles]) =>
    vehicles.some(
      (vehicle) =>
        vehicle.licensePlate.toLowerCase().includes(searchTerm.toLowerCase()) ||
        vehicle.brand.toLowerCase().includes(searchTerm.toLowerCase()) ||
        vehicle.model.toLowerCase().includes(searchTerm.toLowerCase())
    )
  );

  // Create a wrapper function to handle the type mismatch
  const handleGroupByChange = (key: string) => {
    setGroupBy(key as keyof Vehicle);
  };

  if (isLoading) {
    return (
      <div className="flex items-center justify-center min-h-[calc(100vh-120px)]">
        <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-purple-500"></div>
      </div>
    );
  }

  return (
    <div className="bg-gray-900 min-h-screen p-6 bg-gradient-to-br from-gray-900 via-gray-800 to-gray-900">
      <div className="bg-gray-800 text-gray-100 rounded-xl shadow-lg border border-purple-500/30">
        <HeaderSection router={router} />
        <Toolbar
          searchTerm={searchTerm}
          setSearchTerm={setSearchTerm}
          groupBy={groupBy}
          setGroupBy={handleGroupByChange}
          setViewMode={setViewMode}
        />
        {viewMode === "table" && (
          <TableView
            filteredGroups={filteredGroups}
            vehicles={vehicles}
            setVehicles={setVehicles}
          />
        )}
        {viewMode === "gallery" && <GalleryView groupedVehicles={groupedVehicles} />}
        {viewMode === "timeline" && <TimelineView />}
      </div>
    </div>
  );
}

export default VehiclesDashboard;