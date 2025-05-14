"use client";

import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Separator } from "@/components/ui/separator";
import { Database } from "lucide-react";
import { Switch } from "@/components/ui/switch";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";

interface DataManagementSettingsProps {
  handleSave: () => void;
  isLoading: boolean;
}

export function DataManagementSettings({ handleSave, isLoading }: DataManagementSettingsProps) {
  return (
    <Card>
      <CardHeader>
        <CardTitle>Data Management</CardTitle>
        <CardDescription>Manage your data settings</CardDescription>
      </CardHeader>
      <CardContent className="space-y-4">
        <div className="space-y-4">
          <h3 className="text-lg font-medium">Automatic Backups</h3>
          <div className="flex items-center justify-between">
            <p className="text-sm text-muted-foreground">
              Automatically backup your data on a regular schedule
            </p>
            <Switch id="auto-backup" defaultChecked />
          </div>

          <div className="flex items-center justify-between">
            <div className="space-y-0.5">
              <p className="text-sm font-medium">Data Export</p>
              <p className="text-sm text-muted-foreground">Allow exporting data to CSV and Excel formats</p>
            </div>
            <Switch id="data-export" defaultChecked />
          </div>

          <div className="flex items-center justify-between">
            <div className="space-y-0.5">
              <p className="text-sm font-medium">Data Retention</p>
              <p className="text-sm text-muted-foreground">Keep historical data for analysis and reporting</p>
            </div>
            <Select defaultValue="1y">
              <SelectTrigger className="w-[180px]">
                <SelectValue placeholder="Select period" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="3m">3 months</SelectItem>
                <SelectItem value="6m">6 months</SelectItem>
                <SelectItem value="1y">1 year</SelectItem>
                <SelectItem value="2y">2 years</SelectItem>
                <SelectItem value="forever">Forever</SelectItem>
              </SelectContent>
            </Select>
          </div>
        </div>

        <div className="flex justify-end">
          <Button variant="outline" className="mr-2">
            <Database className="mr-2 h-4 w-4" /> Backup Now
          </Button>
          <Button onClick={handleSave} disabled={isLoading}>
            {isLoading ? "Saving..." : "Save Changes"}
          </Button>
        </div>
      </CardContent>
    </Card>
  );
}
