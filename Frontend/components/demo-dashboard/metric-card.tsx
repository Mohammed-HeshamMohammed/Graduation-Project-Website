import type React from "react"
import { Card, CardContent } from "@/components/ui/card"
import { DonutChart } from "@/components/demo-dashboard/charts/donut-chart"

interface MetricCardProps {
  title: string
  value: string
  percentage?: number
  subtitle?: string
  icon?: React.ReactNode
}

export function MetricCard({ title, value, percentage, subtitle, icon }: MetricCardProps) {
  return (
    <Card className="overflow-hidden">
      <CardContent className="p-6">
        <div className="flex justify-between items-start">
          <div>
            <h3 className="text-sm font-medium text-gray-500 mb-1 flex items-center">
              {icon && <span className="mr-2">{icon}</span>}
              {title}
            </h3>
            <p className="text-2xl font-bold">{value}</p>
            {subtitle && <p className="text-xs text-gray-500">{subtitle}</p>}
          </div>
          {percentage !== undefined && (
            <DonutChart value={percentage} max={100} color={percentage >= 50 ? "#ef4444" : "#3b82f6"} />
          )}
        </div>
      </CardContent>
    </Card>
  )
}

