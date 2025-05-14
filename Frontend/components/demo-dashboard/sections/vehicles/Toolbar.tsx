"use client";

import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Tabs, TabsList, TabsTrigger } from "@/components/ui/tabs";
import {
  Search,
  Filter,
  ChevronDown,
  List,
  Calendar,
  ImageIcon,
} from "lucide-react";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";

interface ToolbarProps {
  searchTerm: string;
  setSearchTerm: (s: string) => void;
  groupBy: string;
  setGroupBy: (key: string) => void;
  setViewMode: (mode: "table" | "timeline" | "gallery") => void;
}

export function Toolbar({ searchTerm, setSearchTerm, groupBy, setGroupBy, setViewMode }: ToolbarProps) {
  const toolbarButtonClasses = "border border-purple-500/50 text-purple-200 bg-gray-700 hover:bg-purple-900/30";
  return (
    <div className="bg-gray-800 p-5 rounded-lg shadow-lg border-b border-purple-500/30 mb-6 bg-gradient-to-r from-gray-800 via-gray-700 to-gray-800">
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div className="flex flex-wrap items-center gap-2">
          <Button variant="outline" size="sm" className={toolbarButtonClasses}>
            View all brands
            <ChevronDown className="ml-2 h-4 w-4" />
          </Button>
          <Button variant="outline" size="sm" className={toolbarButtonClasses}>
            <Filter className="mr-2 h-4 w-4 text-cyan-300" /> Filter
          </Button>
          <DropdownMenu>
            <DropdownMenuTrigger asChild>
              <Button variant="outline" size="sm" className={toolbarButtonClasses}>
                Grouped by: <span className="text-cyan-300 ml-1">{groupBy}</span>
                <ChevronDown className="ml-2 h-4 w-4" />
              </Button>
            </DropdownMenuTrigger>
            <DropdownMenuContent className="bg-gray-800 border-purple-500/50 text-gray-200">
              <DropdownMenuItem onClick={() => setGroupBy("brand")} className="hover:bg-purple-900/30 text-purple-200">Brand</DropdownMenuItem>
              <DropdownMenuItem onClick={() => setGroupBy("status")} className="hover:bg-purple-900/30 text-purple-200">Status</DropdownMenuItem>
              <DropdownMenuItem onClick={() => setGroupBy("model")} className="hover:bg-purple-900/30 text-purple-200">Model</DropdownMenuItem>
            </DropdownMenuContent>
          </DropdownMenu>
          <Button variant="outline" size="sm" className={toolbarButtonClasses}>
            <ChevronDown className="mr-2 h-4 w-4 text-pink-300" />
            Hide columns
          </Button>
        </div>
        <div className="flex items-center gap-2">
          <div className="relative">
            <Search className="absolute left-2.5 top-2.5 h-4 w-4 text-cyan-400" />
            <Input
              type="search"
              placeholder="Search vehicles..."
              className="pl-8 h-9 border-purple-500/30 bg-gray-700 text-cyan-200 focus:border-purple-500 focus:ring-purple-500"
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
            />
          </div>
          <Tabs defaultValue="table" onValueChange={(value: string) => setViewMode(value as "table" | "timeline" | "gallery")} className="border border-purple-500/30 rounded-md">
            <TabsList className="h-9 bg-gray-700">
              <TabsTrigger value="table" className="data-[state=active]:bg-purple-900/50 data-[state=active]:text-purple-200 text-gray-300">
                <List className="h-4 w-4" />
              </TabsTrigger>
              <TabsTrigger value="timeline" className="data-[state=active]:bg-purple-900/50 data-[state=active]:text-purple-200 text-gray-300">
                <Calendar className="h-4 w-4" />
              </TabsTrigger>
              <TabsTrigger value="gallery" className="data-[state=active]:bg-purple-900/50 data-[state=active]:text-purple-200 text-gray-300">
                <ImageIcon className="h-4 w-4" />
              </TabsTrigger>
            </TabsList>
          </Tabs>
        </div>
      </div>
    </div>
  );
}