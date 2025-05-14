"use client";

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Calendar, CheckCircle2, Clock, MapPin } from "lucide-react";

interface StatsCardsProps {
  totalTrips: number;
  completedTrips: number;
  inProgressTrips: number;
  totalDistance: number;
  tripsWithFuel: any[]; // further type as needed
}

export function StatsCards({
  totalTrips,
  completedTrips,
  inProgressTrips,
  totalDistance,
  tripsWithFuel,
}: StatsCardsProps) {
  return (
    <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4 mb-6">
      <Card className="bg-gradient-to-br from-gray-800 to-indigo-950 shadow-md">
        <CardHeader className="pb-2">
          <CardTitle className="text-sm font-medium text-indigo-300">Total Trips</CardTitle>
          <Calendar className="h-4 w-4 text-indigo-400" />
        </CardHeader>
        <CardContent>
          <div className="text-2xl font-bold text-indigo-200">{totalTrips}</div>
        </CardContent>
      </Card>

      <Card className="bg-gradient-to-br from-gray-800 to-emerald-950 shadow-md">
        <CardHeader className="pb-2">
          <CardTitle className="text-sm font-medium text-emerald-300">Completed Trips</CardTitle>
          <CheckCircle2 className="h-4 w-4 text-emerald-400" />
        </CardHeader>
        <CardContent>
          <div className="text-2xl font-bold text-emerald-200">{completedTrips}</div>
        </CardContent>
      </Card>

      <Card className="bg-gradient-to-br from-gray-800 to-amber-950 shadow-md">
        <CardHeader className="pb-2">
          <CardTitle className="text-sm font-medium text-amber-300">In Progress</CardTitle>
          <Clock className="h-4 w-4 text-amber-400" />
        </CardHeader>
        <CardContent>
          <div className="text-2xl font-bold text-amber-200">{inProgressTrips}</div>
        </CardContent>
      </Card>

      <Card className="bg-gradient-to-br from-gray-800 to-violet-950 shadow-md">
        <CardHeader className="pb-2">
          <CardTitle className="text-sm font-medium text-violet-300">Total Distance</CardTitle>
          <MapPin className="h-4 w-4 text-violet-400" />
        </CardHeader>
        <CardContent>
          <div className="text-2xl font-bold text-violet-200">{totalDistance.toFixed(1)} km</div>
        </CardContent>
      </Card>
    </div>
  );
}
