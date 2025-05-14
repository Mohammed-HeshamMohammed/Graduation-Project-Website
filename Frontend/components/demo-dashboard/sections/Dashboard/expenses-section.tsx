// components/demo-dashboard/sections/expenses-section.tsx
"use client";

import { PieChart, Pie, Cell, ResponsiveContainer, Legend, Tooltip } from 'recharts';

interface ExpensesSectionProps {
  data: Array<{
    name: string;
    value: number;
    color: string;
  }>;
}

export function ExpensesSection({ data }: ExpensesSectionProps) {
  const totalExpenses = data.reduce((sum, item) => sum + item.value, 0);

  const formattedData = data.map(item => ({
    ...item,
    percentage: ((item.value / totalExpenses) * 100).toFixed(1)
  }));

  return (
    <div className="h-64">
      <ResponsiveContainer width="100%" height="100%">
        <PieChart>
          <Pie
            data={formattedData}
            cx="50%"
            cy="50%"
            labelLine={true}
            outerRadius={80}
            innerRadius={30}
            fill="#8884d8"
            paddingAngle={3}
            dataKey="value"
            label={({ name, percentage }) => `${name}: ${percentage}%`}
          >
            {formattedData.map((entry, index) => (
              <Cell key={`cell-${index}`} fill={entry.color} stroke="rgba(0,0,0,0.1)" strokeWidth={1} />
            ))}
          </Pie>
          <Tooltip 
            formatter={(value) => [`฿${value.toLocaleString()}`, 'Amount']} 
            contentStyle={{ backgroundColor: '#1F2937', borderColor: '#374151', color: '#F9FAFB', borderRadius: '8px' }}
          />
          <Legend layout="vertical" verticalAlign="middle" align="right" />
        </PieChart>
      </ResponsiveContainer>
    </div>
  );
}