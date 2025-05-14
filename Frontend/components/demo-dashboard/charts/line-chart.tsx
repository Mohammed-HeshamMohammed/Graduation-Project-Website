"use client"

import type { ChartDataPoint } from "@/types/fleet-management"

interface LineChartProps {
  data: ChartDataPoint[]
  color?: string
  showDots?: boolean
  height?: string
  showGrid?: boolean
  showValues?: boolean
}

export function LineChart({
  data,
  color = "#3b82f6",
  showDots = false,
  height = "h-full",
  showGrid = false,
  showValues = false,
}: LineChartProps) {
  const maxValue = Math.max(...data.map((item) => item.value))
  const minValue = Math.min(...data.map((item) => item.value)) * 0.9 // Add some padding at the bottom
  const range = maxValue - minValue

  // Normalize values to fit in the chart height
  const normalizeValue = (value: number) => {
    return 1 - (value - minValue) / (range || 1)
  }

  // Generate SVG path
  const generatePath = () => {
    return data
      .map((item, index) => {
        const x = (index / (data.length - 1)) * 100
        const y = normalizeValue(item.value) * 100
        return `${index === 0 ? "M" : "L"} ${x} ${y}`
      })
      .join(" ")
  }

  return (
    <div className={`w-full ${height} relative`}>
      {showGrid && (
        <div className="absolute inset-0 grid grid-cols-4 grid-rows-4">
          {Array.from({ length: 16 }).map((_, i) => (
            <div key={i} className="border-t border-l border-gray-100"></div>
          ))}
        </div>
      )}

      <svg className="w-full h-full overflow-visible" preserveAspectRatio="none">
        {/* Area under the line */}
        <path d={`${generatePath()} L 100 100 L 0 100 Z`} fill={color} fillOpacity="0.1" />

        {/* Line */}
        <path d={generatePath()} fill="none" stroke={color} strokeWidth="2" vectorEffect="non-scaling-stroke" />

        {/* Dots */}
        {showDots &&
          data.map((item, index) => {
            const x = (index / (data.length - 1)) * 100
            const y = normalizeValue(item.value) * 100
            return (
              <g key={index}>
                <circle cx={`${x}%`} cy={`${y}%`} r="3" fill="white" stroke={color} strokeWidth="2" />
                {showValues && (
                  <text x={`${x}%`} y={`${y - 10}%`} fontSize="8" textAnchor="middle" fill="currentColor">
                    {item.value}
                  </text>
                )}
              </g>
            )
          })}
      </svg>

      {/* X-axis labels */}
      <div className="absolute bottom-0 left-0 right-0 flex justify-between">
        {data
          .filter((_, i) => i % 3 === 0)
          .map((item, index) => (
            <span key={index} className="text-[8px] text-gray-500">
              {item.name}
            </span>
          ))}
      </div>
    </div>
  )
}

