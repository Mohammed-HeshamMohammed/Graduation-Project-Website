// components/demo-dashboard/sections/wages-section.tsx
"use client";

import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';

interface WagesSectionProps {
  driverWage: number;
  buddyWage: number;
  driverData: Array<{
    name: string;
    value: number;
  }>;
  buddyData: Array<{
    name: string;
    value: number;
  }>;
}

export function WagesSection({ driverWage, buddyWage, driverData, buddyData }: WagesSectionProps) {
  // Combine the data for the chart
  const combinedData = driverData.map((item, index) => ({
    name: item.name,
    driver: item.value,
    buddy: buddyData[index]?.value || 0
  }));

  return (
    <div>
      <div className="mb-4 grid grid-cols-2 gap-4">
        <div className="bg-gray-700 hover:bg-blue-800 transition-colors duration-300 p-3 rounded-lg">
          <p className="text-sm font-medium text-gray-400">Driver Wage</p>
          <p className="text-xl font-bold text-gray-200 mt-1">฿{driverWage.toLocaleString()}</p>
        </div>
        <div className="bg-gray-700 hover:bg-blue-800 transition-colors duration-300 p-3 rounded-lg">
          <p className="text-sm font-medium text-gray-400">Buddy Wage</p>
          <p className="text-xl font-bold text-gray-200 mt-1">฿{buddyWage.toLocaleString()}</p>
        </div>
      </div>

      <div className="h-48">
        <ResponsiveContainer width="100%" height="100%">
          <LineChart
            data={combinedData}
            margin={{
              top: 5,
              right: 30,
              left: 20,
              bottom: 5,
            }}
          >
            <CartesianGrid strokeDasharray="3 3" stroke="#444" strokeOpacity={0.4} />
            <XAxis dataKey="name" tick={{ fill: '#DDD' }} />
            <YAxis tick={{ fill: '#DDD' }} />
            <Tooltip 
              contentStyle={{ backgroundColor: '#1F2937', borderColor: '#374151', color: '#F9FAFB', borderRadius: '8px' }}
              formatter={(value) => [`฿${value.toLocaleString()}`, 'Wage']}
              cursor={{ stroke: '#666', strokeWidth: 1 }}
            />
            <Legend />
            <Line 
              type="monotone" 
              dataKey="driver" 
              stroke="#3B82F6" 
              strokeWidth={3} 
              dot={{ r: 4 }} 
              activeDot={{ r: 6, stroke: '#3B82F6', strokeWidth: 2 }} 
            />
            <Line 
              type="monotone" 
              dataKey="buddy" 
              stroke="#10B981" 
              strokeWidth={3} 
              dot={{ r: 4 }} 
              activeDot={{ r: 6, stroke: '#10B981', strokeWidth: 2 }} 
            />
          </LineChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
}