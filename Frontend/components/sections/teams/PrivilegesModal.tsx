// src/app/team-management/components/PrivilegesModal.tsx
import { XCircle } from "lucide-react";
import { useTeamMembers } from "./TeamMembersContext";

// Available privileges definition
const availablePrivileges = [
  { value: "admin", label: "Admin", description: "Can add/remove users and assign privileges" },
  { value: "add", label: "Add Members", description: "Can only add new members" },
  { value: "remove", label: "Remove Members", description: "Can only remove members" },
  { value: "member", label: "Basic Member", description: "Basic member with no special privileges" },
  { value: "manager", label: "Manager", description: "Can control everything in the dashboard" },
  { value: "dispatcher", label: "Dispatcher", description: "Can only control trips in the dashboard" },
  { value: "viewer", label: "Viewer", description: "Can only view the dashboard without making changes" },
];

const PrivilegesModal = () => {
  const { 
    selectedMember, 
    showPrivilegesForm, 
    closePrivilegesForm, 
    updateMemberPrivileges, 
    selectedPrivileges, 
    handlePrivilegeChange 
  } = useTeamMembers();

  if (!showPrivilegesForm || !selectedMember) return null;

  return (
    <div className="fixed inset-0 bg-black bg-opacity-70 flex items-center justify-center p-4 z-50">
      <div className="bg-gray-800 rounded-lg shadow-lg max-w-md w-full">
        <div className="p-6 border-b border-gray-700 flex justify-between items-center">
          <div>
            <h3 className="text-xl font-semibold text-white">
              Update Privileges for {selectedMember.full_name}
            </h3>
            <p className="text-sm text-gray-400 mt-1">{selectedMember.email}</p>
          </div>
          <button 
            onClick={closePrivilegesForm}
            className="text-gray-400 hover:text-gray-200"
            aria-label="Close privileges modal"
            title="Close modal"
          >
            <XCircle size={20} />
          </button>
        </div>
        <form onSubmit={(e) => { e.preventDefault(); updateMemberPrivileges(); }} className="p-6">
          <div className="mb-4">
            <h4 className="text-sm font-medium text-gray-300 mb-3">Privileges</h4>
            <div className="space-y-3">
              {availablePrivileges.map((privilege) => (
                // Skip the owner privilege as it can't be assigned
                privilege.value !== "owner" && (
                  <div key={privilege.value} className="flex items-start">
                    <input
                      type="checkbox"
                      id={`privilege-${privilege.value}`}
                      checked={selectedPrivileges.includes(privilege.value)}
                      onChange={(e) => handlePrivilegeChange(privilege.value, e.target.checked)}
                      className="mt-1 mr-2 h-4 w-4 rounded border-gray-600 bg-gray-700 text-indigo-600 focus:ring-indigo-500"
                    />
                    <label htmlFor={`privilege-${privilege.value}`} className="text-sm">
                      <div className="font-medium text-gray-200">{privilege.label}</div>
                      <div className="text-gray-400">{privilege.description}</div>
                    </label>
                  </div>
                )
              ))}
            </div>
          </div>
          <div className="flex items-center justify-end">
            <button
              type="button"
              onClick={closePrivilegesForm}
              className="bg-gray-600 hover:bg-gray-700 text-white px-4 py-2 rounded-md mr-2"
            >
              Cancel
            </button>
            <button
              type="submit"
              className="bg-indigo-600 hover:bg-indigo-700 text-white px-4 py-2 rounded-md"
            >
              Update Privileges
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

export default PrivilegesModal;