// components/demo-dashboard/sections/income-section.tsx
"use client";

import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';

interface IncomeSectionProps {
  driverData: Array<{
    name: string;
    value: number;
  }>;
  buddyData: Array<{
    name: string;
    value: number;
  }>;
}

export function IncomeSection({ driverData, buddyData }: IncomeSectionProps) {
  // Combine the data for the chart
  const combinedData = driverData.map((item, index) => ({
    name: item.name,
    driver: item.value,
    buddy: buddyData[index]?.value || 0,
    total: item.value + (buddyData[index]?.value || 0)
  }));

  // Calculate the total and average income
  const totalIncome = combinedData.reduce((sum, item) => sum + item.total, 0);
  const avgMonthlyIncome = totalIncome / combinedData.length;

  return (
    <div>
      <div className="mb-4 grid grid-cols-2 gap-4">
        <div className="bg-gray-700 hover:bg-blue-800 transition-colors duration-300 p-3 rounded-lg">
          <p className="text-sm font-medium text-gray-400">Total Income</p>
          <p className="text-xl font-bold text-gray-200 mt-1">
            ฿{totalIncome.toLocaleString()}
          </p>
        </div>
        <div className="bg-gray-700 hover:bg-blue-800 transition-colors duration-300 p-3 rounded-lg">
          <p className="text-sm font-medium text-gray-400">Avg Monthly</p>
          <p className="text-xl font-bold text-gray-200 mt-1">
            ฿{avgMonthlyIncome.toLocaleString()}
          </p>
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
              formatter={(value) => [`฿${value.toLocaleString()}`, 'Income']}
              cursor={{ stroke: '#666', strokeWidth: 1 }}
            />
            <Legend />
            <Line type="monotone" dataKey="total" stroke="#EC4899" strokeWidth={3} dot={{ r: 4 }} activeDot={{ r: 6 }} />
            <Line type="monotone" dataKey="driver" stroke="#3B82F6" strokeWidth={2} dot={{ r: 3 }} activeDot={{ r: 5 }} />
            <Line type="monotone" dataKey="buddy" stroke="#10B981" strokeWidth={2} dot={{ r: 3 }} activeDot={{ r: 5 }} />
          </LineChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
}