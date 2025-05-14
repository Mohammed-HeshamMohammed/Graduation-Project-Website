"use client";

import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Separator } from "@/components/ui/separator";
import { Switch } from "@/components/ui/switch";
import { Label } from "@/components/ui/label";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { Users } from "lucide-react";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";

interface UsersSettingsProps {
  handleSave: () => void;
  isLoading: boolean;
}

export function UsersSettings({ handleSave, isLoading }: UsersSettingsProps) {
  return (
    <Card>
      <CardHeader>
        <CardTitle>User Management</CardTitle>
        <CardDescription>Manage users and their permissions</CardDescription>
      </CardHeader>
      <CardContent className="space-y-4">
        <div className="flex items-center justify-between">
          <h3 className="text-lg font-medium">User Roles</h3>
          <Button size="sm">
            <Users className="mr-2 h-4 w-4" /> Add User
          </Button>
        </div>

        <div className="rounded-md border">
          <div className="grid grid-cols-5 gap-4 p-4 font-medium">
            <div>Name</div>
            <div>Email</div>
            <div>Role</div>
            <div>Status</div>
            <div className="text-right">Actions</div>
          </div>
          <Separator />
          {[
            { name: "John Doe", email: "john.doe@example.com", role: "Admin", status: "Active" },
            { name: "Jane Smith", email: "jane.smith@example.com", role: "Manager", status: "Active" },
            { name: "Michael Johnson", email: "michael.johnson@example.com", role: "Dispatcher", status: "Active" },
            { name: "Sarah Williams", email: "sarah.williams@example.com", role: "Viewer", status: "Inactive" },
          ].map((user, index) => (
            <div key={index} className="grid grid-cols-5 gap-4 p-4 items-center">
              <div>{user.name}</div>
              <div className="text-muted-foreground">{user.email}</div>
              <div>
                <select
                  defaultValue={user.role.toLowerCase()}
                  aria-label="Select user role"
                  className="w-[130px] p-1 border rounded"
                >
                  <option value="admin">Admin</option>
                  <option value="manager">Manager</option>
                  <option value="dispatcher">Dispatcher</option>
                  <option value="viewer">Viewer</option>
                </select>
              </div>
              <div>
                <Switch id={`user-status-${index}`} defaultChecked={user.status === "Active"} aria-label="User status" />
              </div>
              <div className="flex justify-end space-x-2">
                <Button variant="outline" size="sm">
                  Edit
                </Button>
                <Button variant="outline" size="sm" className="text-red-600">
                  Delete
                </Button>
              </div>
            </div>
          ))}
        </div>
        <Separator />
        <div className="flex justify-end">
          <Button onClick={handleSave} disabled={isLoading}>
            {isLoading ? "Saving..." : "Save Changes"}
          </Button>
        </div>
      </CardContent>
    </Card>
  );
}