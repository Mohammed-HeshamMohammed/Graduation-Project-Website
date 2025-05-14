"use client"

import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import ProfilePersonalInformation from "./ProfilePersonalInformation"
import ChangePassword from "./ChangePassword"
import NotificationPreferences from "./NotificationPreferences"
import CompanyInfo from "./CompanyInfo"
import SubscriptionBilling from "./SubscriptionBilling"
import { User, Key, Bell, Building } from "lucide-react"

type ProfileTabsProps = {
  isLoading: boolean
  onSaveProfile: () => void
  onSavePassword: () => void
  onSaveNotifications: () => void
  onSaveCompany: () => void
}

export default function ProfileTabs({
  isLoading,
  onSaveProfile,
  onSavePassword,
  onSaveNotifications,
  onSaveCompany,
}: ProfileTabsProps) {
  return (
    <Tabs defaultValue="profile" className="space-y-4">
      <TabsList>
        <TabsTrigger value="profile">
          <User className="mr-2 h-4 w-4" /> Profile
        </TabsTrigger>
        <TabsTrigger value="password">
          <Key className="mr-2 h-4 w-4" /> Password
        </TabsTrigger>
        <TabsTrigger value="notifications">
          <Bell className="mr-2 h-4 w-4" /> Notifications
        </TabsTrigger>
        <TabsTrigger value="company">
          <Building className="mr-2 h-4 w-4" /> Company
        </TabsTrigger>
      </TabsList>

      <TabsContent value="profile" className="space-y-4">
        <ProfilePersonalInformation 
          isLoading={isLoading} 
          onSave={onSaveProfile} 
        />
      </TabsContent>

      <TabsContent value="password" className="space-y-4">
        <ChangePassword 
          isLoading={isLoading} 
          onSave={onSavePassword} 
        />
      </TabsContent>

      <TabsContent value="notifications" className="space-y-4">
        <NotificationPreferences 
          isLoading={isLoading} 
          onSave={onSaveNotifications} 
        />
      </TabsContent>

      <TabsContent value="company" className="space-y-4">
        <CompanyInfo isLoading={isLoading} onSave={onSaveCompany} />
        <SubscriptionBilling />
      </TabsContent>
    </Tabs>
  )
}
