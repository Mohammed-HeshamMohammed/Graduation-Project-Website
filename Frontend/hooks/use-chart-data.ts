"use client"

import { useState, useEffect } from "react"
import type { ChartDataPoint, DriverIncomeData, CargoTypeData } from "@/types/fleet-management"

interface ChartData {
  monthlyExpenses: ChartDataPoint[]
  wagesData: ChartDataPoint[]
  buddyWagesData: ChartDataPoint[]
  tripsData: ChartDataPoint[]
  driverIncomeData: DriverIncomeData[]
  buddyIncomeData: DriverIncomeData[]
  cargoTypes: CargoTypeData[]
}

export function useChartData() {
  const [data, setData] = useState<ChartData | null>(null)
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState<Error | null>(null)

  useEffect(() => {
    async function fetchChartData() {
      try {
        setIsLoading(true)

        // In a real application, this would be an API call
        // For now, we'll simulate with a timeout and mock data
        await new Promise((resolve) => setTimeout(resolve, 800))

        setData({
          monthlyExpenses: [
            { name: "Jan", value: 2300 },
            { name: "Feb", value: 2000 },
            { name: "Mar", value: 1800 },
            { name: "Apr", value: 1400 },
            { name: "May", value: 2200 },
            { name: "Jun", value: 1900 },
            { name: "Jul", value: 1600 },
            { name: "Aug", value: 1000 },
            { name: "Sep", value: 1800 },
            { name: "Oct", value: 1600 },
            { name: "Nov", value: 1000 },
            { name: "Dec", value: 1300 },
          ],
          wagesData: [
            { name: "Jan", value: 9500 },
            { name: "Feb", value: 10200 },
            { name: "Mar", value: 11000 },
            { name: "Apr", value: 10800 },
            { name: "May", value: 11200 },
            { name: "Jun", value: 10500 },
            { name: "Jul", value: 11000 },
            { name: "Aug", value: 11500 },
            { name: "Sep", value: 11200 },
            { name: "Oct", value: 10800 },
            { name: "Nov", value: 11000 },
            { name: "Dec", value: 11200 },
          ],
          buddyWagesData: [
            { name: "Jan", value: 8500 },
            { name: "Feb", value: 8700 },
            { name: "Mar", value: 9000 },
            { name: "Apr", value: 8800 },
            { name: "May", value: 8900 },
            { name: "Jun", value: 8700 },
            { name: "Jul", value: 9100 },
            { name: "Aug", value: 9300 },
            { name: "Sep", value: 8900 },
            { name: "Oct", value: 8700 },
            { name: "Nov", value: 8800 },
            { name: "Dec", value: 8900 },
          ],
          tripsData: [
            { name: "Jan", value: 75 },
            { name: "Feb", value: 85 },
            { name: "Mar", value: 95 },
            { name: "Apr", value: 90 },
            { name: "May", value: 100 },
            { name: "Jun", value: 95 },
            { name: "Jul", value: 90 },
            { name: "Aug", value: 85 },
            { name: "Sep", value: 95 },
            { name: "Oct", value: 100 },
            { name: "Nov", value: 90 },
            { name: "Dec", value: 95 },
          ],
          driverIncomeData: [
            { name: "Close", value: 600 },
            { name: "Far", value: 800 },
            { name: "Regular", value: 400 },
          ],
          buddyIncomeData: [
            { name: "Close", value: 400 },
            { name: "Far", value: 600 },
            { name: "Regular", value: 300 },
          ],
          cargoTypes: [
            { name: "Wastepaper", value: 68 },
            { name: "Woodchip", value: 42 },
            { name: "Construction", value: 35 },
            { name: "Hazardous", value: 15 },
          ],
        })
      } catch (err) {
        setError(err instanceof Error ? err : new Error("An unknown error occurred"))
      } finally {
        setIsLoading(false)
      }
    }

    fetchChartData()
  }, [])

  return { data, isLoading, error }
}

