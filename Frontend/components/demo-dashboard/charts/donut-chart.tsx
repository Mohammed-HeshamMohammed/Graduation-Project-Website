"use client"

interface DonutChartProps {
  value: number
  max: number
  color?: string
  size?: string
  thickness?: number
  showPercentage?: boolean
  label?: string
}

export function DonutChart({
  value,
  max,
  color = "#3b82f6",
  size = "h-16 w-16",
  thickness = 2,
  showPercentage = true,
  label,
}: DonutChartProps) {
  const percentage = Math.round((value / max) * 100)
  const radius = 16
  const circumference = 2 * Math.PI * radius
  const strokeDasharray = circumference
  const strokeDashoffset = circumference - (percentage / 100) * circumference

  return (
    <div className={`relative ${size}`}>
      <svg className="h-full w-full" viewBox="0 0 36 36">
        {/* Background circle */}
        <circle cx="18" cy="18" r={radius} fill="none" stroke="#f3f4f6" strokeWidth={thickness} />

        {/* Foreground circle */}
        <circle
          cx="18"
          cy="18"
          r={radius}
          fill="none"
          stroke={color}
          strokeWidth={thickness}
          strokeDasharray={strokeDasharray}
          strokeDashoffset={strokeDashoffset}
          strokeLinecap="round"
          transform="rotate(-90 18 18)"
        />

        {/* Percentage text */}
        {showPercentage && (
          <text
            x="18"
            y="18"
            dominantBaseline="middle"
            textAnchor="middle"
            fontSize="8"
            fontWeight="bold"
            fill="currentColor"
          >
            {percentage}%
          </text>
        )}

        {/* Label text */}
        {label && (
          <text x="18" y="24" dominantBaseline="middle" textAnchor="middle" fontSize="6" fill="currentColor">
            {label}
          </text>
        )}
      </svg>
    </div>
  )
}

