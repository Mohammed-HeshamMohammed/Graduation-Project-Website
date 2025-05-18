// src/app/team-management/components/TeamMembersList.tsx
import { Users, UserCog, Trash2, CheckCircle, XCircle, AlertTriangle, PlusCircle } from "lucide-react";
import { useTeamMembers } from "./TeamMembersContext";

const TeamMembersList = () => {
  const { 
    members, 
    loading, 
    error, 
    openPrivilegesForm, 
    removeTeamMember 
  } = useTeamMembers();

  if (loading) {
    return (
      <div className="bg-gray-800 rounded-lg shadow-md overflow-hidden">
        <div className="px-6 py-4 bg-gray-900 border-b border-gray-700 flex items-center">
          <Users className="mr-2" size={20} />
          <h2 className="text-xl font-semibold text-white">Team Members</h2>
        </div>
        <div className="p-8 text-center text-gray-400">
          <div className="flex flex-col items-center justify-center py-6">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-indigo-500 mb-4"></div>
            <p>Loading team members...</p>
          </div>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="bg-gray-800 rounded-lg shadow-md overflow-hidden">
        <div className="px-6 py-4 bg-gray-900 border-b border-gray-700 flex items-center">
          <Users className="mr-2" size={20} />
          <h2 className="text-xl font-semibold text-white">Team Members</h2>
        </div>
        <div className="p-8">
          <div className="flex flex-col items-center justify-center py-6 text-red-400">
            <AlertTriangle size={48} className="mb-4" />
            <h3 className="text-lg font-semibold mb-2">Error Loading Team Members</h3>
            <p className="text-center mb-4">{error}</p>
            <button 
              onClick={() => window.location.reload()}
              className="bg-indigo-600 hover:bg-indigo-700 text-white px-4 py-2 rounded-md"
            >
              Try Again
            </button>
          </div>
        </div>
      </div>
    );
  }

  if (members.length === 0) {
    return (
      <div className="bg-gray-800 rounded-lg shadow-md overflow-hidden">
        <div className="px-6 py-4 bg-gray-900 border-b border-gray-700 flex items-center">
          <Users className="mr-2" size={20} />
          <h2 className="text-xl font-semibold text-white">Team Members</h2>
          <span className="ml-2 text-gray-400">(0)</span>
        </div>
        <div className="p-8">
          <div className="flex flex-col items-center justify-center py-8 text-gray-400">
            <Users size={48} className="mb-4 opacity-30" />
            <h3 className="text-lg font-semibold mb-2">No Team Members Found</h3>
            <p className="text-center mb-6">Add your first team member to get started</p>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="bg-gray-800 rounded-lg shadow-md overflow-hidden">
      <div className="px-6 py-4 bg-gray-900 border-b border-gray-700 flex items-center">
        <Users className="mr-2" size={20} />
        <h2 className="text-xl font-semibold text-white">Team Members</h2>
        <span className="ml-2 text-gray-400">({members.length})</span>
      </div>
      <div className="overflow-x-auto">
        <table className="min-w-full">
          <thead className="bg-gray-900">
            <tr>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-400 uppercase tracking-wider">Name</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-400 uppercase tracking-wider">Email</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-400 uppercase tracking-wider">Role</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-400 uppercase tracking-wider">Status</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-400 uppercase tracking-wider">Added By</th>
              <th className="px-6 py-3 text-right text-xs font-medium text-gray-400 uppercase tracking-wider">Actions</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-gray-700">
            {members.map((member) => (
              <tr key={member.email} className="hover:bg-gray-700">
                <td className="px-6 py-4 whitespace-nowrap">
                  <div className="text-sm font-medium text-gray-200">{member.full_name}</div>
                </td>
                <td className="px-6 py-4 whitespace-nowrap">
                  <div className="text-sm text-gray-400">{member.email}</div>
                </td>
                <td className="px-6 py-4 whitespace-nowrap">
                  <div className="text-sm">
                    {member.dashboard_role ? (
                      <span className="bg-indigo-900 text-indigo-200 text-xs font-medium px-2.5 py-0.5 rounded">
                        {member.dashboard_role.charAt(0).toUpperCase() + member.dashboard_role.slice(1)}
                      </span>
                    ) : (
                      <span className="bg-gray-700 text-gray-300 text-xs font-medium px-2.5 py-0.5 rounded">Member</span>
                    )}
                    {member.is_owner && (
                      <span className="ml-2 bg-purple-900 text-purple-200 text-xs font-medium px-2.5 py-0.5 rounded">Owner</span>
                    )}
                  </div>
                </td>
                <td className="px-6 py-4 whitespace-nowrap">
                  {member.verified ? (
                    <span className="inline-flex items-center text-green-400 text-sm">
                      <CheckCircle className="mr-1" size={16} />
                      Verified
                    </span>
                  ) : (
                    <span className="inline-flex items-center text-yellow-400 text-sm">
                      <XCircle className="mr-1" size={16} />
                      Pending Verification
                    </span>
                  )}
                </td>
                <td className="px-6 py-4 whitespace-nowrap">
                  <div className="text-sm text-gray-400">{member.added_by || "N/A"}</div>
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                  {!member.is_owner && (
                    <>
                      <button
                        onClick={() => openPrivilegesForm(member)}
                        className="text-indigo-400 hover:text-indigo-300 mr-4"
                      >
                        <span className="flex items-center">
                          <UserCog className="mr-1" size={16} />
                          Privileges
                        </span>
                      </button>
                      <button
                        onClick={() => removeTeamMember(member.email)}
                        className="text-red-400 hover:text-red-300"
                      >
                        <span className="flex items-center">
                          <Trash2 className="mr-1" size={16} />
                          Remove
                        </span>
                      </button>
                    </>
                  )}
                  {member.is_owner && (
                    <span className="text-gray-500">Owner account</span>
                  )}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
};

export default TeamMembersList;