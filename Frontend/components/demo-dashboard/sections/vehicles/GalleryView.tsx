"use client";

import { Badge } from "@/components/ui/badge";
import Image from "next/image";
import { Vehicle } from "@/components/demo-dashboard/mock-data";

interface GalleryViewProps {
  groupedVehicles: Record<string, Vehicle[]>;
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

export function GalleryView({ groupedVehicles }: GalleryViewProps) {
  return (
    <div className="p-4">
      {Object.entries(groupedVehicles).map(([group, vehicles]) => (
        <div key={group} className="mb-8">
          <div className="flex items-center gap-2 mb-4 p-2 bg-gray-700/50 rounded-lg">
            <Badge className={getBrandColor(group)}>{group}</Badge>
            <h3 className="text-lg font-semibold text-purple-200">Vehicles ({vehicles.length})</h3>
          </div>
          <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-6">
            {vehicles.map((vehicle) => (
              <div key={vehicle.id} className="bg-gray-800 rounded-lg shadow-lg border border-purple-500/30 overflow-hidden transform transition-all duration-300 hover:scale-105 hover:shadow-purple-500/20">
                <div className="relative h-48 w-full">
                  <Image src={vehicle.image || "/placeholder.svg"} alt={vehicle.model} fill className="object-cover" />
                  <div className="absolute top-2 right-2">
                    <Badge className={`${getBrandColor(vehicle.brand)}`}>{vehicle.brand}</Badge>
                  </div>
                </div>
                <div className="p-4 bg-gradient-to-b from-gray-800 to-gray-900">
                  <h4 className="font-semibold text-cyan-300">{vehicle.licensePlate}</h4>
                  <p className="text-sm text-pink-200">{vehicle.model}</p>
                  <div className="mt-2 flex justify-between items-center">
                    <span className="text-xs text-green-300">{vehicle.lastMileage.toLocaleString()} km</span>
                    <Badge variant="outline" className="text-amber-300 border-amber-600">{vehicle.status}</Badge>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      ))}
    </div>
  );
}