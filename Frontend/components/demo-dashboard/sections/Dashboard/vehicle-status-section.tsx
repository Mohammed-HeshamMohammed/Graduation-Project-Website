// components/demo-dashboard/sections/vehicle-status-section.tsx
"use client";

import { PieChart, Pie, Cell, ResponsiveContainer, Legend, Tooltip } from 'recharts';

interface VehicleStatusSectionProps {
  activeVehicles: number;
  maintenanceVehicles: number;
  inactiveVehicles: number;
}

export function VehicleStatusSection({ 
  activeVehicles, 
  maintenanceVehicles, 
  inactiveVehicles 
}: VehicleStatusSectionProps) {
  
  const data = [
    { name: 'Active', value: activeVehicles, color: '#10B981' },
    { name: 'Maintenance', value: maintenanceVehicles, color: '#F59E0B' },
    { name: 'Inactive', value: inactiveVehicles, color: '#6B7280' }
  ];

  return (
    <div className="mt-4 h-56">
      <ResponsiveContainer width="100%" height="100%">
        <PieChart>
          <Pie
            data={data}
            cx="50%"
            cy="50%"
            labelLine={true}
            outerRadius={80}
            innerRadius={35}
            paddingAngle={3}
            fill="#8884d8"
            dataKey="value"
            label={({ name, value, percent }) => `${name}: ${value} (${(percent * 100).toFixed(0)}%)`}
          >
            {data.map((entry, index) => (
              <Cell key={`cell-${index}`} fill={entry.color} stroke="rgba(0,0,0,0.1)" strokeWidth={1} />
            ))}
          </Pie>
          <Tooltip 
            formatter={(value) => [`${value} vehicles`, 'Count']}
            contentStyle={{ backgroundColor: '#1F2937', borderColor: '#374151', color: '#F9FAFB', borderRadius: '8px' }}
          />
          <Legend wrapperStyle={{ paddingTop: '10px' }} />
        </PieChart>
      </ResponsiveContainer>
    </div>
  );
}