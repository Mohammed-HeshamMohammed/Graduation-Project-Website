// components/demo-dashboard/mock-data.ts

// Dashboard data with primary metrics
export const dashboardData = {
     totalVehicles: 48,
     activeVehicles: 32,
     maintenanceAlerts: 7,
     totalDrivers: 65,
     activeDrivers: 42,
     tripsToday: 18,
     tripsThisWeek: 87,
     totalDistance: 14893,
     totalExpenses: 783450,
     expensesPercentage: 5.7,
     driverWage: 35000,
     buddyWage: 22000,
     returnTrips: 64,
     oneWayTrips: 23
   };
   
   // Chart data for various visualizations
   export const chartData = {
     // Monthly expenses breakdown
     monthlyExpenses: [
       { name: 'Fuel', value: 347500, color: '#10B981' },
       { name: 'Maintenance', value: 167800, color: '#F59E0B' },
       { name: 'Insurance', value: 82750, color: '#6366F1' },
       { name: 'Tolls', value: 45300, color: '#EC4899' },
       { name: 'Other', value: 140100, color: '#8B5CF6' }
     ],
     
     // Wages data for drivers
     wagesData: [
       { name: 'Jan', value: 32500 },
       { name: 'Feb', value: 33800 },
       { name: 'Mar', value: 35000 },
       { name: 'Apr', value: 35000 },
       { name: 'May', value: 36200 },
       { name: 'Jun', value: 35000 },
     ],
     
     // Wages data for buddies
     buddyWagesData: [
       { name: 'Jan', value: 20000 },
       { name: 'Feb', value: 21500 },
       { name: 'Mar', value: 22000 },
       { name: 'Apr', value: 22000 },
       { name: 'May', value: 22000 },
       { name: 'Jun', value: 22000 },
     ],
     
     // Income data for drivers
     driverIncomeData: [
       { name: 'Jan', value: 846000 },
       { name: 'Feb', value: 912000 },
       { name: 'Mar', value: 875000 },
       { name: 'Apr', value: 923000 },
       { name: 'May', value: 958000 },
       { name: 'Jun', value: 893000 },
     ],
     
     // Income data for buddies
     buddyIncomeData: [
       { name: 'Jan', value: 425000 },
       { name: 'Feb', value: 456000 },
       { name: 'Mar', value: 438000 },
       { name: 'Apr', value: 461000 },
       { name: 'May', value: 479000 },
       { name: 'Jun', value: 447000 },
     ],
     
     // Trip distribution data
     tripsData: [
       { name: 'Bangkok-Chiang Mai', value: 28, color: '#10B981' },
       { name: 'Bangkok-Pattaya', value: 22, color: '#F59E0B' },
       { name: 'Bangkok-Phuket', value: 19, color: '#6366F1' },
       { name: 'Bangkok-Hua Hin', value: 15, color: '#EC4899' },
       { name: 'Other Routes', value: 16, color: '#8B5CF6' }
     ],
     
     // Cargo types data
     cargoTypes: [
       { name: 'Electronics', value: 32, color: '#10B981' },
       { name: 'Perishables', value: 25, color: '#F59E0B' },
       { name: 'Textiles', value: 15, color: '#6366F1' },
       { name: 'Construction', value: 18, color: '#EC4899' },
       { name: 'Miscellaneous', value: 10, color: '#8B5CF6' }
     ]
   };
   
   // Mock data for vehicles
   export const mockVehicles = [
     {
       id: 'V001',
       type: 'Heavy Truck',
       status: 'active',
       lastMaintenance: '2025-03-15',
       fuelLevel: 85,
       location: 'Bangkok'
     },
     {
       id: 'V002',
       type: 'Delivery Van',
       status: 'active',
       lastMaintenance: '2025-03-10',
       fuelLevel: 72,
       location: 'Chiang Mai'
     },
     {
       id: 'V003',
       type: 'Heavy Truck',
       status: 'maintenance',
       lastMaintenance: '2025-03-28',
       fuelLevel: 45,
       location: 'Service Center'
     },
     {
       id: 'V004',
       type: 'Refrigerated Truck',
       status: 'active',
       lastMaintenance: '2025-02-18',
       fuelLevel: 63,
       location: 'Phuket'
     },
     {
       id: 'V005',
       type: 'Light Truck',
       status: 'inactive',
       lastMaintenance: '2025-01-22',
       fuelLevel: 12,
       location: 'Warehouse'
     }
   ];
   
   // Mock data for drivers
   export const mockDrivers = [
     {
       id: 'D001',
       name: 'Somchai Jaidee',
       status: 'on-duty',
       hoursThisWeek: 32,
       rating: 4.8,
       vehicleAssigned: 'V001'
     },
     {
       id: 'D002',
       name: 'Pranee Suksai',
       status: 'available',
       hoursThisWeek: 28,
       rating: 4.7,
       vehicleAssigned: null
     },
     {
       id: 'D003',
       name: 'Chaiyaporn Wattana',
       status: 'on-duty',
       hoursThisWeek: 35,
       rating: 4.9,
       vehicleAssigned: 'V002'
     },
     {
       id: 'D004',
       name: 'Malee Srisuk',
       status: 'off-duty',
       hoursThisWeek: 40,
       rating: 4.6,
       vehicleAssigned: null
     },
     {
       id: 'D005',
       name: 'Niwat Thongdee',
       status: 'on-duty',
       hoursThisWeek: 30,
       rating: 4.5,
       vehicleAssigned: 'V004'
     }
   ];
   
   // Trip metrics data (can be used for comparative analysis)
   export const tripMetricsData = {
     averageDistance: 273,
     averageDuration: 5.2, // In hours
     fuelConsumption: 14.3, // Liters per 100km
     deliveryOnTime: 0.92, // 92% on time
     routeEfficiency: 0.85 // 85% optimal route efficiency
   };