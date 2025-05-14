"use client"

import { useState } from "react"
import { useToast } from "@/components/ui/use-toast"
import { DemoBadge } from "@/components/demo-dashboard/demo-badge"
import ProfileHeader from "./ProfileHeader"
import ProfileTabs from "./ProfileTabs"

export default function ProfilePage() {
  const [isLoading, setIsLoading] = useState(false)
  const { toast } = useToast()

  // Pass down the isLoading state and toast handling as needed.
  const handleLoading = (action: () => void) => {
    setIsLoading(true)
    setTimeout(() => {
      setIsLoading(false)
      action()
    }, 1000)
  }

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h1 className="text-2xl text-black font-bold">Profile</h1>
        <DemoBadge />
      </div>

      <ProfileHeader isLoading={isLoading} />

      <ProfileTabs 
        isLoading={isLoading} 
        onSaveProfile={() => handleLoading(() => {
          toast({
            title: "Profile updated",
            description: "Your profile information has been updated successfully.",
            duration: 3000,
          })
        })}
        onSavePassword={() => handleLoading(() => {
          toast({
            title: "Password updated",
            description: "Your password has been changed successfully.",
            duration: 3000,
          })
        })}
        onSaveNotifications={() => handleLoading(() => {
          toast({
            title: "Notification preferences updated",
            description: "Your notification preferences have been saved.",
            duration: 3000,
          })
        })}
        onSaveCompany={() => handleLoading(() => {
          toast({
            title: "Company information updated",
            description: "Your company information has been updated successfully.",
            duration: 3000,
          })
        })}
      />
    </div>
  )
}
