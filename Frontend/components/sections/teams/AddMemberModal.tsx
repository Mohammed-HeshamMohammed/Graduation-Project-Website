// src/app/team-management/components/AddMemberModal.tsx
import { useState } from "react";
import { XCircle } from "lucide-react";
import { useTeamMembers } from "./TeamMembersContext";

interface AddMemberModalProps {
  isOpen: boolean;
  onClose: () => void;
}

const AddMemberModal = ({ isOpen, onClose }: AddMemberModalProps) => {
  const { registerTeamMember, fetchTeamMembers } = useTeamMembers();
  const [newMemberEmail, setNewMemberEmail] = useState("");
  const [newMemberName, setNewMemberName] = useState("");
  const [newMemberPassword, setNewMemberPassword] = useState("");
  const [isSubmitting, setIsSubmitting] = useState(false);

  if (!isOpen) return null;

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (isSubmitting) return;
    
    try {
      setIsSubmitting(true);
      await registerTeamMember(newMemberEmail, newMemberName, newMemberPassword);
      
      // Force refresh the member list after adding a new member
      await fetchTeamMembers();
      
      // Reset form
      setNewMemberEmail("");
      setNewMemberName("");
      setNewMemberPassword("");
      
      // Close modal
      onClose();
    } catch (error) {
      console.error("Error adding team member:", error);
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="fixed inset-0 bg-black bg-opacity-70 flex items-center justify-center p-4 z-50">
      <div className="bg-gray-800 rounded-lg shadow-lg max-w-md w-full">
        <div className="p-6 border-b border-gray-700 flex justify-between items-center">
          <h3 className="text-xl font-semibold text-white">Add New Team Member</h3>
          <button 
            onClick={onClose}
            className="text-gray-400 hover:text-gray-200"
            aria-label="Close modal"
            title="Close modal"
          >
            <XCircle size={20} />
          </button>
        </div>
        <form onSubmit={handleSubmit} className="p-6">
          <div className="mb-4">
            <label className="block text-gray-300 text-sm font-bold mb-2" htmlFor="email">
              Email Address
            </label>
            <input
              type="email"
              id="email"
              value={newMemberEmail}
              onChange={(e) => setNewMemberEmail(e.target.value)}
              className="shadow appearance-none border bg-gray-700 border-gray-600 rounded w-full py-2 px-3 text-gray-200 leading-tight focus:outline-none focus:ring-2 focus:ring-indigo-500"
              placeholder="email@example.com"
              required
            />
          </div>
          <div className="mb-4">
            <label className="block text-gray-300 text-sm font-bold mb-2" htmlFor="fullName">
              Full Name
            </label>
            <input
              type="text"
              id="fullName"
              value={newMemberName}
              onChange={(e) => setNewMemberName(e.target.value)}
              className="shadow appearance-none border bg-gray-700 border-gray-600 rounded w-full py-2 px-3 text-gray-200 leading-tight focus:outline-none focus:ring-2 focus:ring-indigo-500"
              placeholder="John Doe"
              required
            />
          </div>
          <div className="mb-6">
            <label className="block text-gray-300 text-sm font-bold mb-2" htmlFor="password">
              Initial Password
            </label>
            <input
              type="password"
              id="password"
              value={newMemberPassword}
              onChange={(e) => setNewMemberPassword(e.target.value)}
              className="shadow appearance-none border bg-gray-700 border-gray-600 rounded w-full py-2 px-3 text-gray-200 leading-tight focus:outline-none focus:ring-2 focus:ring-indigo-500"
              placeholder="••••••••"
              required
            />
            <p className="text-sm text-gray-400 mt-1">
              The member will receive an email to verify their account and can change their password later.
            </p>
          </div>
          <div className="flex items-center justify-end">
            <button
              type="button"
              onClick={onClose}
              className="bg-gray-600 hover:bg-gray-700 text-white px-4 py-2 rounded-md mr-2"
              disabled={isSubmitting}
            >
              Cancel
            </button>
            <button
              type="submit"
              className="bg-indigo-600 hover:bg-indigo-700 text-white px-4 py-2 rounded-md flex items-center"
              disabled={isSubmitting}
            >
              {isSubmitting ? (
                <>
                  <span className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></span>
                  Adding...
                </>
              ) : (
                'Add Member'
              )}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

export default AddMemberModal;