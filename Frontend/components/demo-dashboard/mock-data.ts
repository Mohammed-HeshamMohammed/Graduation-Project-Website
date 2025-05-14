// components/demo-dashboard/mock-data.ts

// Dashboard summary data
export const dashboardData = {
  totalExpenses: 27200,
  totalSalaries: 12100,
  totalWages: 9000,
  expensesPercentage: 44,
  salariesPercentage: 56,
  driverWage: 11200,
  buddyWage: 8900,
  totalDistance: 868,
  returnTrips: 8,
  oneWayTrips: 16,
  totalVehicles: 48,
  activeVehicles: 32,
  totalDrivers: 56,
  activeDrivers: 42,
  tripsToday: 24,
  tripsThisWeek: 142,
  maintenanceAlerts: 5,
  fuelEfficiency: 8.2,
  vehicleUtilization: 76,
  incidentRate: 2.3,
};

// Chart data for graphs
export const chartData = {
  monthlyExpenses: [
    { name: "Jan", value: 2300 },
    { name: "Feb", value: 2000 },
    { name: "Mar", value: 1800 },
    { name: "Apr", value: 1400 },
    { name: "May", value: 2200 },
    { name: "Jun", value: 1900 },
    { name: "Jul", value: 1600 },
    { name: "Aug", value: 1000 },
    { name: "Sep", value: 1800 },
    { name: "Oct", value: 1600 },
    { name: "Nov", value: 1000 },
    { name: "Dec", value: 1300 },
  ],
  wagesData: [
    { name: "Jan", value: 9500 },
    { name: "Feb", value: 10200 },
    { name: "Mar", value: 11000 },
    { name: "Apr", value: 10800 },
    { name: "May", value: 11200 },
    { name: "Jun", value: 10500 },
    { name: "Jul", value: 11000 },
    { name: "Aug", value: 11500 },
    { name: "Sep", value: 11200 },
    { name: "Oct", value: 10800 },
    { name: "Nov", value: 11000 },
    { name: "Dec", value: 11200 },
  ],
  buddyWagesData: [
    { name: "Jan", value: 8500 },
    { name: "Feb", value: 8700 },
    { name: "Mar", value: 9000 },
    { name: "Apr", value: 8800 },
    { name: "May", value: 8900 },
    { name: "Jun", value: 8700 },
    { name: "Jul", value: 9100 },
    { name: "Aug", value: 9300 },
    { name: "Sep", value: 8900 },
    { name: "Oct", value: 8700 },
    { name: "Nov", value: 8800 },
    { name: "Dec", value: 8900 },
  ],
  tripsData: [
    { name: "Jan", value: 75 },
    { name: "Feb", value: 85 },
    { name: "Mar", value: 95 },
    { name: "Apr", value: 90 },
    { name: "May", value: 100 },
    { name: "Jun", value: 95 },
    { name: "Jul", value: 90 },
    { name: "Aug", value: 85 },
    { name: "Sep", value: 95 },
    { name: "Oct", value: 100 },
    { name: "Nov", value: 90 },
    { name: "Dec", value: 95 },
  ],
  driverIncomeData: [
    { name: "Close", value: 600 },
    { name: "Far", value: 800 },
    { name: "Regular", value: 400 },
  ],
  buddyIncomeData: [
    { name: "Close", value: 400 },
    { name: "Far", value: 600 },
    { name: "Regular", value: 300 },
  ],
  cargoTypes: [
    { name: "Wastepaper", value: 68 },
    { name: "Woodchip", value: 42 },
    { name: "Construction", value: 35 },
    { name: "Hazardous", value: 15 },
  ],
};

// Mock data for vehicles
export interface Vehicle {
  id: number;
  licensePlate: string;
  brand: string;
  model: string;
  status: string;
  lastMileage: number;
  image: string;
  rentals: string[];
}

export const mockVehicles: Vehicle[] = [
  {
    id: 1,
    licensePlate: "HR BF-150",
    brand: "VW",
    model: "Polo Life",
    status: "Active",
    lastMileage: 12496,
    image: "/placeholder.svg?height=80&width=120",
    rentals: ["M-00001", "M-00002"],
  },
  {
    id: 2,
    licensePlate: "M AN-1192",
    brand: "VW",
    model: "Passat Variant",
    status: "Repair",
    lastMileage: 25374,
    image: "/placeholder.svg?height=80&width=120",
    rentals: [],
  },
  {
    id: 3,
    licensePlate: "B OI-1932",
    brand: "BMW",
    model: "2er Active Tourer",
    status: "Active",
    lastMileage: 2356,
    image: "/placeholder.svg?height=80&width=120",
    rentals: ["M-00003", "M-00008"],
  },
  {
    id: 4,
    licensePlate: "D AR-1795",
    brand: "BMW",
    model: "3er Touring M",
    status: "Active",
    lastMileage: 7893,
    image: "/placeholder.svg?height=80&width=120",
    rentals: ["M-00004"],
  },
  {
    id: 5,
    licensePlate: "MZ TR-005",
    brand: "BMW",
    model: "X2 M",
    status: "Active",
    lastMileage: 15736,
    image: "/placeholder.svg?height=80&width=120",
    rentals: [],
  },
];

// Mock data for drivers
export interface Driver {
  id: number;
  name: string;
  licenseNum: string;
  licenseExpDate: string;
  status: "active" | "inactive";
  experience: string;
  assignedVehicle: string;
}

export const mockDrivers: Driver[] = [
  {
    id: 1,
    name: "John Doe",
    licenseNum: "DL12345678",
    licenseExpDate: "2025-06-15",
    status: "active",
    experience: "8 years",
    assignedVehicle: "HR BF-150",
  },
  {
    id: 2,
    name: "Jane Smith",
    licenseNum: "DL87654321",
    licenseExpDate: "2024-08-22",
    status: "active",
    experience: "12 years",
    assignedVehicle: "M AN-1192",
  },
  {
    id: 3,
    name: "Michael Johnson",
    licenseNum: "DL23456789",
    licenseExpDate: "2025-03-10",
    status: "active",
    experience: "5 years",
    assignedVehicle: "B OI-1932",
  },
  {
    id: 4,
    name: "Sarah Williams",
    licenseNum: "DL34567890",
    licenseExpDate: "2024-05-18",
    status: "active",
    experience: "10 years",
    assignedVehicle: "D AR-1795",
  },
  {
    id: 5,
    name: "Robert Brown",
    licenseNum: "DL45678901",
    licenseExpDate: "2023-12-05",
    status: "inactive",
    experience: "15 years",
    assignedVehicle: "Unassigned",
  },
];

// Mock data for trips
export interface Trip {
  id: number;
  distance: number;
  loadType: string;
  loadCapacity: number;
  driverId: number;
  driverName: string;
  truckId: number;
  truckCode: string;
  startTime: string;
  endTime: string | null;
  status: string;
  startLocation: string;
  endLocation: string;
  fuelConsumption: number | null;
  avgSpeed: number;
}

export const mockTrips: Trip[] = [
  {
    id: 1,
    distance: 450.5,
    loadType: "General Cargo",
    loadCapacity: 15000,
    driverId: 1,
    driverName: "John Doe",
    truckId: 1,
    truckCode: "TR-1001",
    startTime: "2023-12-01T08:00:00",
    endTime: "2023-12-01T16:30:00",
    status: "completed",
    startLocation: "Chicago, IL",
    endLocation: "Indianapolis, IN",
    fuelConsumption: 52.3,
    avgSpeed: 65.2,
  },
  {
    id: 2,
    distance: 780.2,
    loadType: "Refrigerated Goods",
    loadCapacity: 12000,
    driverId: 2,
    driverName: "Jane Smith",
    truckId: 2,
    truckCode: "TR-1002",
    startTime: "2023-12-02T07:30:00",
    endTime: null,
    status: "in_progress",
    startLocation: "Dallas, TX",
    endLocation: "Memphis, TN",
    fuelConsumption: null,
    avgSpeed: 68.7,
  },
  {
    id: 3,
    distance: 320.8,
    loadType: "Construction Materials",
    loadCapacity: 18000,
    driverId: 3,
    driverName: "Michael Johnson",
    truckId: 3,
    truckCode: "TR-1003",
    startTime: "2023-12-03T09:15:00",
    endTime: "2023-12-03T14:45:00",
    status: "completed",
    startLocation: "Denver, CO",
    endLocation: "Salt Lake City, UT",
    fuelConsumption: 38.5,
    avgSpeed: 62.3,
  },
  {
    id: 4,
    distance: 550.0,
    loadType: "Electronics",
    loadCapacity: 8000,
    driverId: 4,
    driverName: "Sarah Williams",
    truckId: 5,
    truckCode: "TR-1005",
    startTime: "2023-12-04T06:00:00",
    endTime: null,
    status: "in_progress",
    startLocation: "Seattle, WA",
    endLocation: "Portland, OR",
    fuelConsumption: null,
    avgSpeed: 60.8,
  },
  {
    id: 5,
    distance: 420.5,
    loadType: "Automotive Parts",
    loadCapacity: 10000,
    driverId: 6,
    driverName: "Emily Davis",
    truckId: 7,
    truckCode: "TR-1007",
    startTime: "2023-12-05T10:30:00",
    endTime: "2023-12-05T18:15:00",
    status: "completed",
    startLocation: "Detroit, MI",
    endLocation: "Cleveland, OH",
    fuelConsumption: 48.2,
    avgSpeed: 64.5,
  },
  {
    id: 6,
    distance: 680.3,
    loadType: "Food Products",
    loadCapacity: 14000,
    driverId: 8,
    driverName: "Jennifer Martinez",
    truckId: 1,
    truckCode: "TR-1001",
    startTime: "2023-12-06T08:45:00",
    endTime: "2023-12-06T19:30:00",
    status: "completed",
    startLocation: "Miami, FL",
    endLocation: "Atlanta, GA",
    fuelConsumption: 75.6,
    avgSpeed: 67.1,
  },
  {
    id: 7,
    distance: 290.7,
    loadType: "Furniture",
    loadCapacity: 9000,
    driverId: 1,
    driverName: "John Doe",
    truckId: 3,
    truckCode: "TR-1003",
    startTime: "2023-12-07T11:00:00",
    endTime: null,
    status: "in_progress",
    startLocation: "Phoenix, AZ",
    endLocation: "Las Vegas, NV",
    fuelConsumption: null,
    avgSpeed: 71.2,
  },
  {
    id: 8,
    distance: 510.4,
    loadType: "Chemicals",
    loadCapacity: 16000,
    driverId: 2,
    driverName: "Jane Smith",
    truckId: 2,
    truckCode: "TR-1002",
    startTime: "2023-12-08T07:00:00",
    endTime: "2023-12-08T16:00:00",
    status: "completed",
    startLocation: "Houston, TX",
    endLocation: "New Orleans, LA",
    fuelConsumption: 61.8,
    avgSpeed: 63.9,
  },
];

// Mock data for maintenance
export interface MaintenanceItem {
  id: number | string;
  truckId: number;
  truckCode: string;
  truckModel: string;
  lastMaintenanceDate: string;
  nextMaintenanceDate: string;
  type: string;
  cost: number;
  status: string;
  notes: string;
  garage: string;
}

export const mockMaintenance: MaintenanceItem[] = [
  {
    id: 1,
    truckId: 1,
    truckCode: "TR-1001",
    truckModel: "Volvo FH16",
    lastMaintenanceDate: "2023-10-15",
    nextMaintenanceDate: "2024-01-15",
    type: "Regular Service",
    cost: 1200.5,
    status: "completed",
    notes: "Oil change, filter replacement, brake inspection",
    garage: "Main Depot",
  },
  {
    id: 2,
    truckId: 2,
    truckCode: "TR-1002",
    truckModel: "Mercedes-Benz Actros",
    lastMaintenanceDate: "2023-11-05",
    nextMaintenanceDate: "2023-12-05",
    type: "Tire Replacement",
    cost: 2500.0,
    status: "scheduled",
    notes: "Replace all tires, wheel alignment",
    garage: "North Depot",
  },
  {
    id: 3,
    truckId: 3,
    truckCode: "TR-1003",
    truckModel: "Scania R500",
    lastMaintenanceDate: "2023-09-20",
    nextMaintenanceDate: "2024-01-20",
    type: "Engine Overhaul",
    cost: 5000.0,
    status: "in_progress",
    notes: "Complete engine inspection and repair",
    garage: "Main Depot",
  },
  {
    id: 4,
    truckId: 4,
    truckCode: "TR-1004",
    truckModel: "MAN TGX",
    lastMaintenanceDate: "2023-08-10",
    nextMaintenanceDate: "2023-12-10",
    type: "Electrical System",
    cost: 800.75,
    status: "scheduled",
    notes: "Check and repair electrical systems",
    garage: "South Depot",
  },
  {
    id: 5,
    truckId: 5,
    truckCode: "TR-1005",
    truckModel: "DAF XF",
    lastMaintenanceDate: "2023-10-25",
    nextMaintenanceDate: "2024-01-25",
    type: "Regular Service",
    cost: 1100.0,
    status: "completed",
    notes: "Oil change, filter replacement, general inspection",
    garage: "East Depot",
  },
  {
    id: 6,
    truckId: 6,
    truckCode: "TR-1006",
    truckModel: "Iveco Stralis",
    lastMaintenanceDate: "2023-11-15",
    nextMaintenanceDate: "2023-12-15",
    type: "Brake System",
    cost: 1800.25,
    status: "scheduled",
    notes: "Complete brake system overhaul",
    garage: "West Depot",
  },
  {
    id: 7,
    truckId: 7,
    truckCode: "TR-1007",
    truckModel: "Renault T",
    lastMaintenanceDate: "2023-09-30",
    nextMaintenanceDate: "2024-01-30",
    type: "Transmission",
    cost: 3200.0,
    status: "in_progress",
    notes: "Transmission repair and fluid change",
    garage: "North Depot",
  },
  {
    id: 8,
    truckId: 8,
    truckCode: "TR-1008",
    truckModel: "Volvo FM",
    lastMaintenanceDate: "2023-07-20",
    nextMaintenanceDate: "2023-11-20",
    type: "Regular Service",
    cost: 950.5,
    status: "completed",
    notes: "Oil change, filter replacement, fluid checks",
    garage: "Main Depot",
  },
];
