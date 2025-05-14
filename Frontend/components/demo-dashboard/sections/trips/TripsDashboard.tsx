"use client";

import { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import { useToast } from "@/components/ui/use-toast";
import { DemoBadge } from "@/components/demo-dashboard/demo-badge";
import { mockTrips } from "@/components/demo-dashboard/mock-data";
import { Trip } from "./TripsRecordsTable"; // Import Trip from TripsRecordsTable

// Import section components
import { HeaderSection } from "./HeaderSection";
import { StatsCards } from "./StatsCards";
import { TripsRecordsTable } from "./TripsRecordsTable";
import { TimelineView } from "./TimelineView";

// Helper functions
const formatDate = (dateString: string | null): string => {
  if (!dateString) return "N/A";
  return new Date(dateString).toLocaleString();
};

export function TripsDashboard() {
  const router = useRouter();
  const { toast } = useToast();
  
  // Convert mockTrips to match the Trip interface from TripsRecordsTable
  const convertedTrips: Trip[] = mockTrips.map(trip => ({
    id: String(trip.id), // Convert number to string
    startLocation: trip.startLocation,
    endLocation: trip.endLocation,
    driverName: trip.driverName,
    truckCode: trip.truckCode,
    loadType: trip.loadType,
    startTime: trip.startTime,
    status: trip.status as "completed" | "in_progress" | "scheduled" | "cancelled"
  }));
  
  const [trips, setTrips] = useState<Trip[]>(convertedTrips);
  const [searchTerm, setSearchTerm] = useState("");
  const [viewMode, setViewMode] = useState<"table" | "timeline" | "gallery">("table");
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    const timer = setTimeout(() => setIsLoading(false), 1000);
    return () => clearTimeout(timer);
  }, []);

  const filteredTrips = trips.filter((trip) =>
    trip.driverName.toLowerCase().includes(searchTerm.toLowerCase()) ||
    trip.truckCode.toLowerCase().includes(searchTerm.toLowerCase()) ||
    trip.loadType.toLowerCase().includes(searchTerm.toLowerCase()) ||
    trip.startLocation.toLowerCase().includes(searchTerm.toLowerCase()) ||
    trip.endLocation.toLowerCase().includes(searchTerm.toLowerCase())
  );

  // Statistics
  const totalTrips = trips.length;
  const completedTrips = trips.filter((t) => t.status === "completed").length;
  const inProgressTrips = trips.filter((t) => t.status === "in_progress").length;
  
  // These properties don't exist in the TripsRecordsTable Trip interface
  // Using a type assertion to access them from the original mockTrips
  const totalDistance = mockTrips.reduce((sum, trip) => sum + (trip.distance || 0), 0);
  const tripsWithFuel = mockTrips.filter((t) => t.fuelConsumption != null);

  if (isLoading) {
    return (
      <div className="flex items-center justify-center min-h-[calc(100vh-120px)] bg-gray-900">
        <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-indigo-400"></div>
      </div>
    );
  }

  return (
    <div className="space-y-6 bg-gradient-to-b from-gray-900 to-gray-800 p-6 rounded-lg">
      <HeaderSection router={router} />
      <StatsCards
        totalTrips={totalTrips}
        completedTrips={completedTrips}
        inProgressTrips={inProgressTrips}
        totalDistance={totalDistance}
        tripsWithFuel={tripsWithFuel}
      />
      {viewMode === "table" && (
        <TripsRecordsTable
          trips={filteredTrips}
          searchTerm={searchTerm}
          setSearchTerm={setSearchTerm}
          formatDate={formatDate}
          toast={toast}
        />
      )}
      {viewMode === "timeline" && <TimelineView />}
      {/* You can add a GalleryView if desired */}
    </div>
  );
}

export default TripsDashboard;