// Define the Driver interface
export interface Driver {
  id: string;
  name: string;
  avatarInitials: string;
  contactNumber: string;
  licenseNum: string;
  licenseExpDate: string;
  status: 'active' | 'inactive';
  experience: string;
  safetyScore: number;
  assignedVehicle: string;
  vehicleType: string;
}

// Create mock data for drivers
export const mockDrivers: Driver[] = [
  {
    id: "driver-001",
    name: "Alex Johnson",
    avatarInitials: "AJ",
    contactNumber: "(555) 123-4567",
    licenseNum: "DL-38291-A",
    licenseExpDate: "2025-06-15",
    status: "active",
    experience: "5 years",
    safetyScore: 92,
    assignedVehicle: "Truck #104",
    vehicleType: "Delivery Van"
  },
  {
    id: "driver-002",
    name: "Sarah Miller",
    avatarInitials: "SM",
    contactNumber: "(555) 234-5678",
    licenseNum: "DL-29384-B",
    licenseExpDate: "2025-09-22",
    status: "active",
    experience: "3 years",
    safetyScore: 88,
    assignedVehicle: "Truck #207",
    vehicleType: "Box Truck"
  },
  {
    id: "driver-003",
    name: "Marcus Chen",
    avatarInitials: "MC",
    contactNumber: "(555) 345-6789",
    licenseNum: "DL-47291-C",
    licenseExpDate: "2025-04-10",
    status: "active",
    experience: "7 years",
    safetyScore: 95,
    assignedVehicle: "Truck #115",
    vehicleType: "Semi-Truck"
  },
  {
    id: "driver-004",
    name: "Jessica Roberts",
    avatarInitials: "JR",
    contactNumber: "(555) 456-7890",
    licenseNum: "DL-58371-D",
    licenseExpDate: "2025-02-28",
    status: "inactive",
    experience: "2 years",
    safetyScore: 82,
    assignedVehicle: "Unassigned",
    vehicleType: ""
  },
  {
    id: "driver-005",
    name: "David Williams",
    avatarInitials: "DW",
    contactNumber: "(555) 567-8901",
    licenseNum: "DL-67281-E",
    licenseExpDate: "2024-04-05",
    status: "active",
    experience: "4 years",
    safetyScore: 90,
    assignedVehicle: "Truck #122",
    vehicleType: "Delivery Van"
  },
  {
    id: "driver-006",
    name: "Maria Garcia",
    avatarInitials: "MG",
    contactNumber: "(555) 678-9012",
    licenseNum: "DL-78291-F",
    licenseExpDate: "2025-08-12",
    status: "active",
    experience: "6 years",
    safetyScore: 93,
    assignedVehicle: "Truck #131",
    vehicleType: "Box Truck"
  },
  {
    id: "driver-007",
    name: "James Smith",
    avatarInitials: "JS",
    contactNumber: "(555) 789-0123",
    licenseNum: "DL-89301-G",
    licenseExpDate: "2024-05-19",
    status: "inactive",
    experience: "1 year",
    safetyScore: 78,
    assignedVehicle: "Unassigned",
    vehicleType: ""
  },
  {
    id: "driver-008",
    name: "Angela Davis",
    avatarInitials: "AD",
    contactNumber: "(555) 890-1234",
    licenseNum: "DL-90412-H",
    licenseExpDate: "2025-11-30",
    status: "active",
    experience: "8 years",
    safetyScore: 97,
    assignedVehicle: "Truck #145",
    vehicleType: "Semi-Truck"
  }
];