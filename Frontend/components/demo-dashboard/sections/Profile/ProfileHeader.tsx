"use client"

import { Button } from "@/components/ui/button"
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar"
import { Badge } from "@/components/ui/badge"
import { LogOut } from "lucide-react"

type ProfileHeaderProps = {
  isLoading: boolean
}

export default function ProfileHeader({ isLoading }: ProfileHeaderProps) {
  return (
    <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4">
      <div className="flex items-center gap-4">
        <Avatar className="h-16 w-16">
          <AvatarImage src="/images/avatar-1.jpg" alt="Demo User" />
          <AvatarFallback>DU</AvatarFallback>
        </Avatar>
        <div>
          <h1 className="text-xl text-black font-bold">Demo User</h1>
          <div className="text-sm text-muted-foreground text-black flex items-center gap-2">
            <Badge variant="outline" className="bg-blue-100 text-blue-800">Admin</Badge>
            <span>Fleet Manager</span>
          </div>
        </div>
      </div>
      <Button variant="outline" className="md:self-end" disabled={isLoading}>
        <LogOut className="mr-2 h-4 w-4" /> Sign Out
      </Button>
    </div>
  )
}
