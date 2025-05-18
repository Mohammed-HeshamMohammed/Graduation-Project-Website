"use client";

// src/app/team-management/page.tsx
import { useState } from "react";
import TeamMembersList from "@/components/sections/teams/TeamMembersList";
import AddMemberModal from "@/components/sections/teams/AddMemberModal";
import PrivilegesModal from "@/components/sections/teams/PrivilegesModal";
import StatusMessage from "@/components/sections/teams/StatusMessage";
import { PlusCircle } from "lucide-react";
import { TeamMembersProvider } from "@/components/sections/teams/TeamMembersContext";

const TeamManagementPage = () => {
  const [showAddMemberForm, setShowAddMemberForm] = useState(false);

  return (
    <TeamMembersProvider>
      {/* Add pt-24 to ensure content starts below the navbar */}
      <div className="container mx-auto px-4 py-8 pt-24 text-gray-200">
        <div className="flex justify-between items-center mb-8">
          <div>
            <h1 className="text-3xl font-bold text-white">Team Management</h1>
            <p className="text-gray-400">Manage your team members and their access privileges</p>
          </div>
          <button
            onClick={() => setShowAddMemberForm(true)}
            className="bg-indigo-600 hover:bg-indigo-700 text-white px-4 py-2 rounded-md flex items-center"
          >
            <PlusCircle className="mr-2" size={18} />
            Add Team Member
          </button>
        </div>

        <StatusMessage />
        <TeamMembersList />
        <AddMemberModal 
          isOpen={showAddMemberForm} 
          onClose={() => setShowAddMemberForm(false)} 
        />
        <PrivilegesModal />
      </div>
    </TeamMembersProvider>
  );
};

export default TeamManagementPage;