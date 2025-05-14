"use client";

import { Calendar } from "lucide-react";
import { Button } from "@/components/ui/button";

export function TimelineView() {
  return (
    <div className="p-8">
      <div className="text-center py-12 bg-gray-800/80 rounded-lg border-dashed border-purple-500/50 shadow-lg">
        <div className="p-4 bg-purple-900/30 rounded-full inline-block mb-4">
          <Calendar className="h-12 w-12 text-purple-300" />
        </div>
        <h3 className="text-lg font-medium text-purple-200">Timeline view is available in the full version</h3>
        <p className="text-cyan-300 mt-2 max-w-md mx-auto">
          This view shows vehicle activities and rental periods on an interactive timeline.
        </p>
        <Button variant="outline" className="mt-6 text-pink-300 border-pink-500 hover:bg-purple-900/30 px-6 py-2">
          Upgrade to access
        </Button>
      </div>
    </div>
  );
}