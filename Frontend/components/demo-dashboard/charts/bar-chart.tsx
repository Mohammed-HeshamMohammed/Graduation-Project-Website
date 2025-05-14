"use client"

import type { ChartDataPoint } from "@/types/fleet-management"

interface BarChartProps {
  data: ChartDataPoint[]
  color?: string
  height?: string
  showValues?: boolean
}

export function BarChart({ data, color = "#3b82f6", height = "h-48", showValues = false }: BarChartProps) {
  const maxValue = Math.max(...data.map((item) => item.value))

  return (
    <div className={`w-full ${height} flex items-end`}>
      {data.map((item, index) => (
        <div key={index} className="flex-1 flex flex-col items-center">
          <div className="relative w-full flex justify-center">
            {showValues && <span className="absolute -top-6 text-xs font-medium">{item.value}</span>}
            <div
              className="w-4/5 rounded-t-sm transition-all duration-300 hover:opacity-80"
              style={{
                height: `${(item.value / maxValue) * 100}%`,
                backgroundColor: color,
              }}
            />
          </div>
          <span className="text-xs mt-1 text-gray-500">{item.name}</span>
        </div>
      ))}
    </div>
  )
}

