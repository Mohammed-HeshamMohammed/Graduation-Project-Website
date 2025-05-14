"use client"

import type React from "react"
import { useRouter } from "next/navigation"
import { Button } from "@/components/ui/button"
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu"
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar"
import { Download, Copy, Settings, User } from "lucide-react"
import { useToast } from "@/components/ui/use-toast"
import { DemoBanner } from "@/components/demo-dashboard/demo-banner"

// Updated tabs array to include trips and maintenance if needed.
const tabs = [
  { label: "Dashboard", href: "/demo-dashboard" },
  { label: "Vehicles", href: "/demo-dashboard/vehicles" },
  { label: "Drivers", href: "/demo-dashboard/drivers" },
  { label: "Trips", href: "/demo-dashboard/trips" },
  { label: "Maintenance", href: "/demo-dashboard/maintenance" },
]

export default function DemoDashboardLayout({
  children,
}: {
  children: React.ReactNode
}) {
  const router = useRouter()
  const { toast } = useToast()

  return (
    <div className="min-h-screen bg-gray-100 pt-20">
      {/* Demo banner (optional) */}
      <DemoBanner />
      
      {/* Top Navigation specific to demo dashboard */}
      <header className="bg-gray-800 text-white">
        <div className="container mx-auto px-4">
          <div className="flex items-center justify-between h-16">
            <div className="flex items-center space-x-4">
              <h1 className="text-xl font-semibold">Fleet Management</h1>
              <div className="flex items-center space-x-2">
                <Button variant="ghost" size="sm" className="text-white">
                  <Download className="mr-2 h-4 w-4" />
                  Export
                </Button>
                <Button variant="ghost" size="sm" className="text-white">
                  <Copy className="mr-2 h-4 w-4" />
                  Copy
                </Button>
              </div>
            </div>

            <div className="flex items-center space-x-4">
            <a href="/demo-dashboard/plugins" className="text-white">
              <Button variant="ghost" size="sm" className="text-white">
                {/* You can replace this with an actual icon */}
                <Settings className="mr-2 h-4 w-4" />
                Plugins
              </Button>
            </a>
              <DropdownMenu>
                <DropdownMenuTrigger asChild>
                  <Button variant="ghost" className="relative h-8 w-8 rounded-full">
                    <Avatar className="h-8 w-8">
                      <AvatarImage src="/images/avatar-1.jpg" alt="Demo User" />
                      <AvatarFallback>
                        <User className="h-4 w-4" />
                      </AvatarFallback>
                    </Avatar>
                  </Button>
                </DropdownMenuTrigger>
                <DropdownMenuContent align="end">
                  <DropdownMenuLabel>Demo Account</DropdownMenuLabel>
                  <DropdownMenuSeparator />
                  <DropdownMenuItem onClick={() => router.push("/demo-dashboard/profile")}>Profile</DropdownMenuItem>
                  <DropdownMenuItem onClick={() => router.push("/demo-dashboard/settings")}>Settings</DropdownMenuItem>
                  <DropdownMenuSeparator />
                  <DropdownMenuItem onClick={() => router.push("/")}>Back to Home</DropdownMenuItem>
                </DropdownMenuContent>
              </DropdownMenu>
            </div>
          </div>
        </div>
      </header>

      {/* Secondary Navigation */}
      <nav className="bg-gray-700 text-white">
        <div className="container mx-auto px-4">
          <div className="flex items-center space-x-4 h-12 overflow-x-auto">
            {tabs.map((tab) => (
              <Button
                key={tab.href}
                variant="ghost"
                className="text-white hover:bg-gray-600 whitespace-nowrap"
                onClick={() => router.push(tab.href)}
              >
                {tab.label}
              </Button>
            ))}
          </div>
        </div>
      </nav>

      {/* Main Content */}
      <main className="container mx-auto px-4 py-8">{children}</main>
    </div>
  )
}
