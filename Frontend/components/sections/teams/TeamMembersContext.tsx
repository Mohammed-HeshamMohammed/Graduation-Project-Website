// src/app/team-management/context/TeamMembersContext.tsx
import { createContext, useContext, useState, ReactNode, useCallback, useEffect } from "react";

export type Member = {
  email: string;
  full_name: string;
  privileges: string[];
  dashboard_role: string | null;
  verified: boolean;
  added_by: string;
  added_at: number;
  is_owner: boolean;
};

type StatusMessageType = {
  type: "success" | "error";
  message: string;
} | null;

interface TeamMembersContextType {
  members: Member[];
  loading: boolean;
  error: string | null;
  selectedMember: Member | null;
  showPrivilegesForm: boolean;
  statusMessage: StatusMessageType;
  selectedPrivileges: string[];
  fetchTeamMembers: () => Promise<void>;
  registerTeamMember: (email: string, name: string, password: string) => Promise<void>;
  removeTeamMember: (email: string) => Promise<void>;
  updateMemberPrivileges: () => Promise<void>;
  openPrivilegesForm: (member: Member) => void;
  closePrivilegesForm: () => void;
  handlePrivilegeChange: (privilege: string, checked: boolean) => void;
  dismissStatusMessage: () => void;
  setStatusMessage: (message: StatusMessageType) => void;
}

const baseurl = "http://localhost:8000";

// Function to get auth token from localStorage
const getAuthToken = () => {
  return localStorage.getItem('authToken') || '';
};

const TeamMembersContext = createContext<TeamMembersContextType | undefined>(undefined);

export const useTeamMembers = () => {
  const context = useContext(TeamMembersContext);
  if (!context) {
    throw new Error("useTeamMembers must be used within a TeamMembersProvider");
  }
  return context;
};

export const TeamMembersProvider = ({ children }: { children: ReactNode }) => {
  const [members, setMembers] = useState<Member[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [showPrivilegesForm, setShowPrivilegesForm] = useState(false);
  const [selectedMember, setSelectedMember] = useState<Member | null>(null);
  const [selectedPrivileges, setSelectedPrivileges] = useState<string[]>([]);
  const [statusMessage, setStatusMessage] = useState<StatusMessageType>(null);

  const fetchTeamMembers = useCallback(async () => {
    setLoading(true);
    try {
      const token = getAuthToken();
      
      if (!token) {
        throw new Error("Authentication token not found");
      }
      
      const response = await fetch(`${baseurl}/api/team/members?token=${token}`, {
        method: "GET",
        headers: {
          "Content-Type": "application/json",
          "Authorization": `Bearer ${token}`
        },
        credentials: "include",
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData.detail || `Failed to fetch team members (${response.status})`);
      }

      const data = await response.json();
      setMembers(data.members || []);
      setError(null);
    } catch (err) {
      setError(err instanceof Error ? err.message : "An unknown error occurred");
      setMembers([]);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchTeamMembers();
  }, [fetchTeamMembers]);

  const registerTeamMember = async (email: string, name: string, password: string) => {
    if (!email || !name || !password) {
      setStatusMessage({
        type: "error",
        message: "All fields are required",
      });
      return;
    }
    
    try {
      const token = getAuthToken();
      
      if (!token) {
        throw new Error("Authentication token not found");
      }
      
      const response = await fetch(`${baseurl}/api/team/register?token=${token}`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "Authorization": `Bearer ${token}`
        },
        credentials: "include",
        body: JSON.stringify({
          email,
          full_name: name,
          password,
        }),
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData.detail || `Registration failed (${response.status})`);
      }
      
      setStatusMessage({
        type: "success",
        message: "Team member registered successfully! Verification email sent.",
      });
      
      fetchTeamMembers();
    } catch (err) {
      setStatusMessage({
        type: "error",
        message: err instanceof Error ? err.message : "Failed to register team member",
      });
    }
  };

  const removeTeamMember = async (email: string) => {
    if (!confirm(`Are you sure you want to remove ${email} from the team?`)) {
      return;
    }
    
    try {
      const token = getAuthToken();
      
      if (!token) {
        throw new Error("Authentication token not found");
      }
      
      const response = await fetch(`${baseurl}/api/team/members/${encodeURIComponent(email)}?token=${token}`, {
        method: "DELETE",
        headers: {
          "Content-Type": "application/json",
          "Authorization": `Bearer ${token}`
        },
        credentials: "include",
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData.detail || `Failed to remove team member (${response.status})`);
      }

      setStatusMessage({
        type: "success",
        message: "Team member removed successfully!",
      });
      
      fetchTeamMembers();
    } catch (err) {
      setStatusMessage({
        type: "error",
        message: err instanceof Error ? err.message : "Failed to remove team member",
      });
    }
  };

  const updateMemberPrivileges = async () => {
    if (!selectedMember) return;
    
    try {
      const token = getAuthToken();
      
      if (!token) {
        throw new Error("Authentication token not found");
      }
      
      const response = await fetch(`${baseurl}/api/team/members/${encodeURIComponent(selectedMember.email)}/privileges?token=${token}`, {
        method: "PUT",
        headers: {
          "Content-Type": "application/json",
          "Authorization": `Bearer ${token}`
        },
        credentials: "include",
        body: JSON.stringify({
          privileges: selectedPrivileges,
        }),
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData.detail || `Failed to update privileges (${response.status})`);
      }

      setStatusMessage({
        type: "success",
        message: "Privileges updated successfully!",
      });
      
      closePrivilegesForm();
      fetchTeamMembers();
    } catch (err) {
      setStatusMessage({
        type: "error",
        message: err instanceof Error ? err.message : "Failed to update privileges",
      });
    }
  };

  const openPrivilegesForm = (member: Member) => {
    setSelectedMember(member);
    setSelectedPrivileges([...member.privileges]);
    setShowPrivilegesForm(true);
  };

  const closePrivilegesForm = () => {
    setShowPrivilegesForm(false);
    setSelectedMember(null);
  };

  const handlePrivilegeChange = (privilege: string, checked: boolean) => {
    if (checked) {
      setSelectedPrivileges(prev => [...prev, privilege]);
    } else {
      setSelectedPrivileges(prev => prev.filter(p => p !== privilege));
    }
  };

  const dismissStatusMessage = () => {
    setStatusMessage(null);
  };

  const value: TeamMembersContextType = {
    members,
    loading,
    error,
    selectedMember,
    showPrivilegesForm,
    statusMessage,
    selectedPrivileges,
    fetchTeamMembers,
    registerTeamMember,
    removeTeamMember,
    updateMemberPrivileges,
    openPrivilegesForm,
    closePrivilegesForm,
    handlePrivilegeChange,
    dismissStatusMessage,
    setStatusMessage,
  };

  return (
    <TeamMembersContext.Provider value={value}>
      {children}
    </TeamMembersContext.Provider>
  );
};