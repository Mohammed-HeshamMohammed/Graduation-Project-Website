"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { DemoBadge } from "@/components/demo-dashboard/demo-badge";
import { useToast } from "@/components/ui/use-toast";
import {
  Settings,
  Users,
  Building,
  Shield
} from "lucide-react";

// Import sub‑components for each settings section
import { GeneralSettings } from "./GeneralSettings";
import { DataManagementSettings } from "./DataManagementSettings";
import { UsersSettings } from "./UsersSettings";
import { CompanySettings } from "./CompanySettings";
import { SecuritySettings } from "./SecuritySettings";

export default function SettingsPage() {
  const router = useRouter();
  const { toast } = useToast();
  const [theme, setTheme] = useState("system");
  const [isLoading, setIsLoading] = useState(false);

  const handleSave = () => {
    setIsLoading(true);
    setTimeout(() => {
      setIsLoading(false);
      toast({
        title: "Settings saved",
        description: "Your settings have been updated successfully.",
        duration: 3000,
      });
    }, 1000);
  };

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h1 className="text-2xl text-black font-bold">Settings</h1>
        <DemoBadge />
      </div>

      <Tabs defaultValue="general" className="space-y-4">
        <TabsList>
          <TabsTrigger value="general">
            <Settings className="mr-2 h-4 w-4" /> General
          </TabsTrigger>
          <TabsTrigger value="users">
            <Users className="mr-2 h-4 w-4" /> Users
          </TabsTrigger>
          <TabsTrigger value="company">
            <Building className="mr-2 h-4 w-4" /> Company
          </TabsTrigger>
          <TabsTrigger value="security">
            <Shield className="mr-2 h-4 w-4" /> Security
          </TabsTrigger>
        </TabsList>

        <TabsContent value="general" className="space-y-4">
          <GeneralSettings theme={theme} setTheme={setTheme} />
          <DataManagementSettings handleSave={handleSave} isLoading={isLoading} />
        </TabsContent>

        <TabsContent value="users" className="space-y-4">
          <UsersSettings handleSave={handleSave} isLoading={isLoading} />
        </TabsContent>

        <TabsContent value="company" className="space-y-4">
          <CompanySettings handleSave={handleSave} isLoading={isLoading} />
        </TabsContent>

        <TabsContent value="security" className="space-y-4">
          <SecuritySettings handleSave={handleSave} isLoading={isLoading} />
        </TabsContent>
      </Tabs>
    </div>
  );
}
