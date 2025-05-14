"use client"

import { useRouter } from "next/navigation";
import { AddDriverForm } from "@/components/demo-dashboard/sections/drivers/add-driver-form"; // this calls the index.tsx
import { DemoBadge } from "@/components/demo-dashboard/demo-badge";

export default function AddDriverPage() {
  const router = useRouter();

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h1 className="text-2xl text-black font-bold">Add New Driver</h1>
        <DemoBadge />
      </div>
      <AddDriverForm
        onSuccess={() => {
          router.push("/demo-dashboard/drivers");
        }}
      />
    </div>
  );
}
