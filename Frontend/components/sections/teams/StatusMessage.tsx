// src/app/team-management/components/StatusMessage.tsx
import { CheckCircle, XCircle } from "lucide-react";
import { useTeamMembers } from "./TeamMembersContext";

const StatusMessage = () => {
  const { statusMessage, dismissStatusMessage } = useTeamMembers();

  if (!statusMessage) return null;

  return (
    <div 
      className={`p-4 mb-6 rounded-md flex justify-between items-center ${
        statusMessage.type === "success" ? "bg-green-900 text-green-200" : "bg-red-900 text-red-200"
      }`}
    >
      <div className="flex items-center">
        {statusMessage.type === "success" ? (
          <CheckCircle className="mr-2" size={18} />
        ) : (
          <XCircle className="mr-2" size={18} />
        )}
        <p>{statusMessage.message}</p>
      </div>
      <button 
        onClick={dismissStatusMessage} 
        className="text-gray-300 hover:text-white"
        aria-label="Dismiss message"
        title="Dismiss message"
      >
        <XCircle size={18} />
      </button>
    </div>
  );
};

export default StatusMessage;