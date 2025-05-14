"use client"

import { useState, useEffect } from "react"
import type { DashboardData } from "@/types/fleet-management"

export function useDashboardData() {
  const [data, setData] = useState<DashboardData | null>(null)
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState<Error | null>(null)

  useEffect(() => {
    async function fetchDashboardData() {
      try {
        setIsLoading(true)

        // Simulate API call with a short delay for demo purposes
        await new Promise((resolve) => setTimeout(resolve, 1000))

        // Demo data
        setData({
          totalExpenses: 27200,
          totalSalaries: 12100,
          totalWages: 9000,
          expensesPercentage: 44,
          salariesPercentage: 56,
          driverWage: 11200,
          buddyWage: 8900,
          totalDistance: 868,
          returnTrips: 8,
          oneWayTrips: 16,
          totalVehicles: 48,
          activeVehicles: 32,
          totalDrivers: 56,
          activeDrivers: 42,
          tripsToday: 24,
          tripsThisWeek: 142,
          maintenanceAlerts: 5,
          fuelEfficiency: 8.2,
          vehicleUtilization: 76,
          incidentRate: 2.3,
        })
      } catch (err) {
        setError(err instanceof Error ? err : new Error("An unknown error occurred"))
      } finally {
        setIsLoading(false)
      }
    }

    fetchDashboardData()
  }, [])

  return { data, isLoading, error }
}

