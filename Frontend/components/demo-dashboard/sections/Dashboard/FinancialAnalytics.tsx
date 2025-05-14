"use client";

import { Card } from "@/components/ui/card";
import { ExpensesSection } from "@/components/demo-dashboard/sections/Dashboard/expenses-section";
import { WagesSection } from "@/components/demo-dashboard/sections/Dashboard/wages-section";
import { IncomeSection } from "@/components/demo-dashboard/sections/Dashboard/income-section";

interface FinancialAnalyticsProps {
  dashboardData: {
    driverWage: number;
    buddyWage: number;
  };
  chartData: {
    monthlyExpenses: any[];
    wagesData: any[];
    buddyWagesData: any[];
    driverIncomeData: any[];
    buddyIncomeData: any[];
  };
}

export function FinancialAnalytics({ dashboardData, chartData }: FinancialAnalyticsProps) {
  return (
    <div className="mb-8">
      <h2 className="text-xl font-bold text-gray-200 mb-4 flex items-center">
        Financial Analytics
      </h2>
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <Card className="p-4 rounded-xl shadow-md bg-gray-800 hover:bg-blue-900 transition-colors duration-300 border-none">
          <h3 className="text-sm font-medium text-gray-400 uppercase mb-2">Monthly Expenses</h3>
          <ExpensesSection data={chartData.monthlyExpenses} />
        </Card>
        <Card className="p-4 rounded-xl shadow-md bg-gray-800 hover:bg-blue-900 transition-colors duration-300 border-none">
          <h3 className="text-sm font-medium text-gray-400 uppercase mb-2">Driver & Buddy Wages</h3>
          <WagesSection
            driverWage={dashboardData.driverWage}
            buddyWage={dashboardData.buddyWage}
            driverData={chartData.wagesData}
            buddyData={chartData.buddyWagesData}
          />
        </Card>
        <Card className="p-4 rounded-xl shadow-md bg-gray-800 hover:bg-blue-900 transition-colors duration-300 border-none">
          <h3 className="text-sm font-medium text-gray-400 uppercase mb-2">Income Analysis</h3>
          <IncomeSection
            driverData={chartData.driverIncomeData}
            buddyData={chartData.buddyIncomeData}
          />
        </Card>
      </div>
    </div>
  );
}