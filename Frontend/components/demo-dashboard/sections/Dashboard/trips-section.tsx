// components/demo-dashboard/sections/trips-section.tsx
"use client";

import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Cell } from 'recharts';
import { chartData } from "@/components/demo-dashboard/sections/Dashboard/mock-data";

interface TripsSectionProps {
  data: Array<{
    name: string;
    value: number;
    color: string;
  }>;
}

export function TripsSection({ data }: TripsSectionProps) {
  // If no data is provided, use the mock data
  const tripData = data.length > 0 ? data : chartData.tripsData;

  return (
    <div className="h-56">
      <ResponsiveContainer width="100%" height="100%">
        <BarChart
          data={tripData}
          margin={{
            top: 20,
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
            formatter={(value) => [`${value} trips`, 'Count']}
            cursor={{ fill: 'rgba(255, 255, 255, 0.1)' }}
          />
          <Bar dataKey="value" radius={[8, 8, 0, 0]}>
            {tripData.map((entry, index) => (
              <Cell key={`cell-${index}`} fill={entry.color} />
            ))}
          </Bar>
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
}