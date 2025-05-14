"use client"

import { useState } from "react"
import { X, Info } from "lucide-react"
import { Button } from "@/components/ui/button"

export function DemoBanner() {
  const [isVisible, setIsVisible] = useState(true)

  if (!isVisible) return null

  return (
    <div className="bg-blue-600 text-white py-2 px-4 flex items-center justify-between">
      <div className="flex-1 flex items-center justify-center">
        <Info className="h-4 w-4 mr-2" />
        <p className="text-sm">
          <span className="font-bold">Demo Mode:</span> You are viewing a demo version of the dashboard with sample
          data. No login required.
        </p>
      </div>
      <Button variant="ghost" size="sm" onClick={() => setIsVisible(false)} className="text-white hover:bg-blue-700">
        <X className="h-4 w-4" />
      </Button>
    </div>
  )
}

