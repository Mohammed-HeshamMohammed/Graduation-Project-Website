// components/demo-dashboard/sections/trip-metrics-section.tsx
"use client";

import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';
// Import Cell from recharts
import { Cell } from 'recharts';

interface TripMetricsSectionProps {
  totalDistance: number;
  returnTrips: number;
  oneWayTrips: number;
}

export function TripMetricsSection({ totalDistance, returnTrips, oneWayTrips }: TripMetricsSectionProps) {
  const data = [
    {
      name: 'Return Trips',
      trips: returnTrips,
      color: '#14B8A6'
    },
    {
      name: 'One-Way Trips',
      trips: oneWayTrips,
      color: '#0EA5E9'
    }
  ];

  return (
    <div className="h-56">
      <ResponsiveContainer width="100%" height="100%">
        <BarChart
          data={data}
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
          <Bar dataKey="trips" fill="#14B8A6" radius={[8, 8, 0, 0]}>
            {data.map((entry, index) => (
              <Cell key={`cell-${index}`} fill={entry.color} />
            ))}
          </Bar>
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
}