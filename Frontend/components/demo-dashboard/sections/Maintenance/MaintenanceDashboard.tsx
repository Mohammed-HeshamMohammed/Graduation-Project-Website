// components/demo-dashboard/MaintenanceDashboard/MaintenanceDashboard.tsx
"use client";

import { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import { useToast } from "@/components/ui/use-toast";
import { DemoBadge } from "@/components/demo-dashboard/demo-badge";  // Fixed import path

// Import subcomponents
import { HeaderSection } from "./HeaderSection";
import { OverviewCards } from "./OverviewCards";
import { MaintenanceOverview } from "./MaintenanceOverview";
import { MaintenanceRecordsTable } from "./MaintenanceRecordsTable";

// Import your mock data (ensure this file exists and is properly typed)
import { mockMaintenance } from "@/components/demo-dashboard/mock-data";

// Helper functions (could be moved to a helpers file)
const formatDate = (dateString: string) => {
  if (!dateString) return "N/A";
  return new Date(dateString).toLocaleDateString();
};

const formatCurrency = (amount: number) => {
  return new Intl.NumberFormat("en-US", {
    style: "currency",
    currency: "USD",
  }).format(amount);
};

const getDaysUntil = (dateString: string) => {
  const today = new Date();
  const targetDate = new Date(dateString);
  const diffTime = targetDate.getTime() - today.getTime();
  return Math.ceil(diffTime / (1000 * 60 * 60 * 24));
};

export function MaintenanceDashboard() {
  const router = useRouter();
  const { toast } = useToast();
  const [maintenance, setMaintenance] = useState<any[]>(mockMaintenance);
  const [searchTerm, setSearchTerm] = useState("");
  const [activeFilter, setActiveFilter] = useState("all");
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    const timer = setTimeout(() => setIsLoading(false), 800);
    return () => clearTimeout(timer);
  }, []);

  const getFilteredMaintenance = () => {
    let filtered = [...maintenance];
    if (searchTerm) {
      filtered = filtered.filter((item) =>
        item.truckCode.toLowerCase().includes(searchTerm.toLowerCase()) ||
        item.truckModel.toLowerCase().includes(searchTerm.toLowerCase()) ||
        item.type.toLowerCase().includes(searchTerm.toLowerCase()) ||
        item.garage.toLowerCase().includes(searchTerm.toLowerCase())
      );
    }
    if (activeFilter !== "all") {
      filtered = filtered.filter((item) => item.status === activeFilter);
    }
    return filtered;
  };

  const handleMarkComplete = (id: number | string) => {
    setMaintenance((prev) =>
      prev.map((item) => (item.id === id ? { ...item, status: "completed" } : item))
    );
    toast({
      title: "Status Updated",
      description: "Maintenance record marked as completed",
    });
  };

  // Statistics calculation
  const totalRecords = maintenance.length;
  const scheduledCount = maintenance.filter((m) => m.status === "scheduled").length;
  const inProgressCount = maintenance.filter((m) => m.status === "in_progress").length;
  const completedCount = maintenance.filter((m) => m.status === "completed").length;
  const overdueCount = maintenance.filter((m) => m.status === "overdue").length;
  const totalCost = maintenance.reduce((sum, item) => sum + item.cost, 0);

  if (isLoading) {
    return (
      <div className="flex items-center justify-center min-h-screen bg-gray-900">
        <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-indigo-600"></div>
      </div>
    );
  }

  return (
    <div className="space-y-6 bg-gray-900 p-6 rounded-lg">
      <HeaderSection router={router} />
      <OverviewCards
        totalRecords={totalRecords}
        inProgressCount={inProgressCount}
        scheduledCount={scheduledCount}
        completedCount={completedCount}
        overdueCount={overdueCount}
        totalCost={totalCost}
        formatCurrency={formatCurrency}
      />
      <MaintenanceOverview
        maintenance={maintenance}
        formatDate={formatDate}
        getDaysUntil={getDaysUntil}
        formatCurrency={formatCurrency} // Pass the formatCurrency function here
      />
      <MaintenanceRecordsTable
        searchTerm={searchTerm}
        setSearchTerm={setSearchTerm}
        activeFilter={activeFilter}
        setActiveFilter={setActiveFilter}
        filteredMaintenance={getFilteredMaintenance()}
        totalRecords={totalRecords}
        handleMarkComplete={handleMarkComplete}
        formatDate={formatDate}
        formatCurrency={formatCurrency}
        getDaysUntil={getDaysUntil}
      />
    </div>
  );
}

export default MaintenanceDashboard;