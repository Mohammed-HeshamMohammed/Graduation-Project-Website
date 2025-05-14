// components/demo-dashboard/sections/cargo-section.tsx
"use client";

import { PieChart, Pie, Cell, ResponsiveContainer, Legend, Tooltip } from 'recharts';

interface CargoSectionProps {
  data: Array<{
    name: string;
    value: number;
    color: string;
  }>;
}

export function CargoSection({ data }: CargoSectionProps) {
  return (
    <div className="h-64">
      <ResponsiveContainer width="100%" height="100%">
        <PieChart>
          <Pie
            data={data}
            cx="50%"
            cy="50%"
            labelLine={true}
            outerRadius={80}
            innerRadius={40}
            fill="#8884d8"
            dataKey="value"
            paddingAngle={4}
            label={({ name, percent }) => `${name}: ${(percent * 100).toFixed(0)}%`}
          >
            {data.map((entry, index) => (
              <Cell key={`cell-${index}`} fill={entry.color} stroke="rgba(0,0,0,0.1)" strokeWidth={1} />
            ))}
          </Pie>
          <Tooltip formatter={(value) => [`${value}%`, 'Percentage']} contentStyle={{ borderRadius: '8px' }} />
          <Legend layout="vertical" verticalAlign="middle" align="right" />
        </PieChart>
      </ResponsiveContainer>
    </div>
  );
}