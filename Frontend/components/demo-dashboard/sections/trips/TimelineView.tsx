"use client";

import { Calendar } from "lucide-react";
import { Button } from "@/components/ui/button";

export function TimelineView() {
  return (
    <div className="p-8">
      <div className="text-center py-12 bg-slate-50 dark:bg-gray-700 rounded-lg border-dashed border-gray-300">
        <Calendar className="h-12 w-12 text-gray-400 mx-auto mb-4" />
        <h3 className="text-lg font-medium text-gray-700 dark:text-gray-200">
          Timeline view is available in the full version
        </h3>
        <p className="text-gray-500 dark:text-gray-400 mt-2 max-w-md mx-auto">
          This view shows trip activities and key events on an interactive timeline.
        </p>
        <Button variant="outline" className="mt-4 text-indigo-600 border-indigo-300 hover:bg-indigo-50">
          Upgrade to access
        </Button>
      </div>
    </div>
  );
}
