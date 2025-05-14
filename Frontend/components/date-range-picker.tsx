// date-range-picker.tsx
"use client"

import * as React from "react"
import { format } from "date-fns"
import { CalendarIcon, ChevronDown } from "lucide-react"
import type { DateRange } from "react-day-picker"

import { cn } from "@/lib/utils"
import { Button } from "@/components/ui/button"
import { Calendar } from "@/components/ui/calendar"
import { Popover, PopoverContent, PopoverTrigger } from "@/components/ui/popover"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"

interface DatePickerWithRangeProps extends React.HTMLAttributes<HTMLDivElement> {
  className?: string
  position?: "top" | "bottom"
  align?: "start" | "center" | "end"
  variant?: "default" | "compact" | "card"
  showPresets?: boolean
}

export function DatePickerWithRange({
  className,
  position = "bottom",
  align = "start",
  variant = "default",
  showPresets = true,
}: DatePickerWithRangeProps) {
  const [date, setDate] = React.useState<DateRange | undefined>({
    from: new Date(2023, 11, 1), // December 1, 2023
    to: new Date(),
  })

  const [isOpen, setIsOpen] = React.useState(false)

  // Preset date ranges
  const presets = [
    {
      label: "Today",
      getValue: () => {
        const today = new Date()
        return { from: today, to: today }
      },
    },
    {
      label: "Yesterday",
      getValue: () => {
        const yesterday = new Date()
        yesterday.setDate(yesterday.getDate() - 1)
        return { from: yesterday, to: yesterday }
      },
    },
    {
      label: "Last 7 days",
      getValue: () => {
        const today = new Date()
        const lastWeek = new Date()
        lastWeek.setDate(lastWeek.getDate() - 6)
        return { from: lastWeek, to: today }
      },
    },
    {
      label: "Last 30 days",
      getValue: () => {
        const today = new Date()
        const lastMonth = new Date()
        lastMonth.setDate(lastMonth.getDate() - 29)
        return { from: lastMonth, to: today }
      },
    },
    {
      label: "This month",
      getValue: () => {
        const today = new Date()
        const startOfMonth = new Date(today.getFullYear(), today.getMonth(), 1)
        return { from: startOfMonth, to: today }
      },
    },
    {
      label: "Last month",
      getValue: () => {
        const today = new Date()
        const startOfLastMonth = new Date(today.getFullYear(), today.getMonth() - 1, 1)
        const endOfLastMonth = new Date(today.getFullYear(), today.getMonth(), 0)
        return { from: startOfLastMonth, to: endOfLastMonth }
      },
    },
  ]

  const presetDateRange = (preset: typeof presets[number]) => {
    const range = preset.getValue()
    setDate(range)
  }

  const getButtonStyles = () => {
    switch (variant) {
      case "compact":
        return "h-9 px-3 py-1 text-sm"
      case "card":
        return "bg-white border-blue-200 shadow-sm hover:bg-gray-50 hover:shadow"
      default:
        return ""
    }
  }

  return (
    <div className={cn("grid gap-2", className)}>
      <Popover open={isOpen} onOpenChange={setIsOpen}>
        <PopoverTrigger asChild>
          <Button
            id="date"
            variant={"outline"}
            className={cn(
              "w-full justify-between text-left font-normal",
              getButtonStyles(),
              !date && "text-muted-foreground",
              variant === "card" && "rounded-lg border border-blue-200 shadow-sm"
            )}
          >
            <div className="flex items-center">
              <CalendarIcon className="mr-2 h-4 w-4 text-blue-500" />
              {date?.from ? (
                date.to ? (
                  <>
                    {format(date.from, "LLL dd, y")} - {format(date.to, "LLL dd, y")}
                  </>
                ) : (
                  format(date.from, "LLL dd, y")
                )
              ) : (
                <span>Pick a date</span>
              )}
            </div>
            <ChevronDown className="h-4 w-4 opacity-50" />
          </Button>
        </PopoverTrigger>
        <PopoverContent
          className={cn("w-auto p-0", variant === "card" && "rounded-lg border border-blue-200 shadow-lg")}
          align={align}
          side={position}
        >
          <div className={cn("flex flex-col sm:flex-row gap-0 sm:gap-4", showPresets ? "sm:divide-x" : "")}>
            {showPresets && (
              <div className="p-3 sm:p-4 border-b sm:border-b-0 border-gray-200 sm:pr-6">
                <h3 className="font-medium text-sm mb-3 text-gray-500">Quick Select</h3>
                <div className="flex flex-wrap gap-2 max-w-[200px]">
                  {presets.map((preset) => (
                    <Button
                      key={preset.label}
                      onClick={() => {
                        presetDateRange(preset)
                        setIsOpen(false)
                      }}
                      variant="outline"
                      size="sm"
                      className="text-xs h-8 bg-gray-50 hover:bg-blue-50 hover:text-blue-600 border-gray-200"
                    >
                      {preset.label}
                    </Button>
                  ))}
                </div>
              </div>
            )}
            <div className={cn("p-0", !showPresets && "min-w-[350px]")}>
              <Calendar
                initialFocus
                mode="range"
                defaultMonth={date?.from}
                selected={date}
                onSelect={setDate}
                numberOfMonths={showPresets ? 1 : 2}
                className={showPresets ? "p-3" : ""}
              />
              {!showPresets && (
                <div className="flex items-center justify-between px-4 py-2 border-t border-gray-200">
                  <Button variant="ghost" size="sm" onClick={() => setIsOpen(false)} className="text-gray-500">
                    Cancel
                  </Button>
                  <Button size="sm" onClick={() => setIsOpen(false)} className="bg-blue-600 hover:bg-blue-700">
                    Apply
                  </Button>
                </div>
              )}
            </div>
          </div>
        </PopoverContent>
      </Popover>
    </div>
  )
}
