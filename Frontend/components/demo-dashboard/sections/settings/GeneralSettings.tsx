"use client";

import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Separator } from "@/components/ui/separator";
import { Sun, Moon, Laptop } from "lucide-react";

interface GeneralSettingsProps {
  theme: string;
  setTheme: (value: string) => void;
}

export function GeneralSettings({ theme, setTheme }: GeneralSettingsProps) {
  return (
    <Card>
      <CardHeader>
        <CardTitle>General Settings</CardTitle>
        <CardDescription>Manage your general application settings</CardDescription>
      </CardHeader>
      <CardContent className="space-y-4">
        <div className="space-y-4">
          <h3 className="text-lg font-medium">Appearance</h3>
          <div className="grid gap-2">
            <Label>Theme</Label>
            <div className="flex items-center space-x-2">
              <Button
                variant={theme === "light" ? "default" : "outline"}
                size="sm"
                className="w-24"
                onClick={() => setTheme("light")}
              >
                <Sun className="mr-2 h-4 w-4" /> Light
              </Button>
              <Button
                variant={theme === "dark" ? "default" : "outline"}
                size="sm"
                className="w-24"
                onClick={() => setTheme("dark")}
              >
                <Moon className="mr-2 h-4 w-4" /> Dark
              </Button>
              <Button
                variant={theme === "system" ? "default" : "outline"}
                size="sm"
                className="w-24"
                onClick={() => setTheme("system")}
              >
                <Laptop className="mr-2 h-4 w-4" /> System
              </Button>
            </div>
          </div>
        </div>

        <Separator />

        <div className="space-y-4">
          <h3 className="text-lg font-medium">Language & Region</h3>
          <div className="grid gap-4 md:grid-cols-2">
            <div className="space-y-2">
              <Label htmlFor="language">Language</Label>
              <Select defaultValue="en">
                <SelectTrigger id="language">
                  <SelectValue placeholder="Select language" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="en">English</SelectItem>
                  <SelectItem value="es">Spanish</SelectItem>
                  <SelectItem value="fr">French</SelectItem>
                  <SelectItem value="de">German</SelectItem>
                </SelectContent>
              </Select>
            </div>
            <div className="space-y-2">
              <Label htmlFor="timezone">Timezone</Label>
              <Select defaultValue="utc-5">
                <SelectTrigger id="timezone">
                  <SelectValue placeholder="Select timezone" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="utc-8">Pacific Time (UTC-8)</SelectItem>
                  <SelectItem value="utc-7">Mountain Time (UTC-7)</SelectItem>
                  <SelectItem value="utc-6">Central Time (UTC-6)</SelectItem>
                  <SelectItem value="utc-5">Eastern Time (UTC-5)</SelectItem>
                  <SelectItem value="utc">UTC</SelectItem>
                </SelectContent>
              </Select>
            </div>
            <div className="space-y-2">
              <Label htmlFor="date-format">Date Format</Label>
              <Select defaultValue="mdy">
                <SelectTrigger id="date-format">
                  <SelectValue placeholder="Select date format" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="mdy">MM/DD/YYYY</SelectItem>
                  <SelectItem value="dmy">DD/MM/YYYY</SelectItem>
                  <SelectItem value="ymd">YYYY/MM/DD</SelectItem>
                </SelectContent>
              </Select>
            </div>
            <div className="space-y-2">
              <Label htmlFor="time-format">Time Format</Label>
              <Select defaultValue="12h">
                <SelectTrigger id="time-format">
                  <SelectValue placeholder="Select time format" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="12h">12-hour (AM/PM)</SelectItem>
                  <SelectItem value="24h">24-hour</SelectItem>
                </SelectContent>
              </Select>
            </div>
          </div>
        </div>

        <Separator />

        <div className="space-y-2">
          <h3 className="text-lg font-medium">Units</h3>
          <div className="grid gap-4 md:grid-cols-2">
            <div className="space-y-2">
              <Label htmlFor="distance">Distance</Label>
              <Select defaultValue="km">
                <SelectTrigger id="distance">
                  <SelectValue placeholder="Select distance unit" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="km">Kilometers (km)</SelectItem>
                  <SelectItem value="mi">Miles (mi)</SelectItem>
                </SelectContent>
              </Select>
            </div>
            <div className="space-y-2">
              <Label htmlFor="fuel-efficiency">Fuel Efficiency</Label>
              <Select defaultValue="kml">
                <SelectTrigger id="fuel-efficiency">
                  <SelectValue placeholder="Select fuel efficiency unit" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="kml">Kilometers per Liter (km/L)</SelectItem>
                  <SelectItem value="mpg">Miles per Gallon (MPG)</SelectItem>
                </SelectContent>
              </Select>
            </div>
            <div className="space-y-2">
              <Label htmlFor="weight">Weight</Label>
              <Select defaultValue="kg">
                <SelectTrigger id="weight">
                  <SelectValue placeholder="Select weight unit" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="kg">Kilograms (kg)</SelectItem>
                  <SelectItem value="lb">Pounds (lb)</SelectItem>
                </SelectContent>
              </Select>
            </div>
            <div className="space-y-2">
              <Label htmlFor="volume">Volume</Label>
              <Select defaultValue="l">
                <SelectTrigger id="volume">
                  <SelectValue placeholder="Select volume unit" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="l">Liters (L)</SelectItem>
                  <SelectItem value="gal">Gallons (gal)</SelectItem>
                </SelectContent>
              </Select>
            </div>
          </div>
        </div>

        <div className="flex justify-end">
          <Button>Save Changes</Button>
        </div>
      </CardContent>
    </Card>
  );
}
