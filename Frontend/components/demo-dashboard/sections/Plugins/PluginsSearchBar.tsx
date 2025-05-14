"use client"

import { Input } from "@/components/ui/input"
import { Button } from "@/components/ui/button"
import { Search, Download } from "lucide-react"

type PluginsSearchBarProps = {
  searchTerm: string
  setSearchTerm: (term: string) => void
}

export default function PluginsSearchBar({ searchTerm, setSearchTerm }: PluginsSearchBarProps) {
  return (
    <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
      <div className="relative flex-1">
        <Search className="absolute left-2.5 top-2.5 h-4 w-4 text-muted-foreground" />
        <Input
          type="search"
          placeholder="Search plugins..."
          className="pl-8"
          value={searchTerm}
          onChange={(e) => setSearchTerm(e.target.value)}
        />
      </div>
      <Button>
        <Download className="mr-2 h-4 w-4" /> Install Plugin
      </Button>
    </div>
  )
}
