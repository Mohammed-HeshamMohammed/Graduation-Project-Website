"use client"
import React from 'react';
import { Truck, PenToolIcon as Tool, Users, Fuel } from "lucide-react";

const offerings = [
  {
    title: "Fleet Tracking & Monitoring",
    description:
      "Real-time GPS tracking and monitoring for your entire fleet. Know where your vehicles are at all times and monitor driver behavior.",
    icon: Truck,
    bgColor: "bg-blue-500",
    borderColor: "border-blue-700",
    iconColor: "text-blue-100",
    hoverBg: "hover:bg-blue-600",
  },
  {
    title: "Maintenance Management",
    description:
      "Proactive maintenance scheduling and tracking to prevent costly breakdowns. Keep your vehicles in optimal condition.",
    icon: Tool,
    bgColor: "bg-purple-500",
    borderColor: "border-purple-700",
    iconColor: "text-purple-100",
    hoverBg: "hover:bg-purple-600",
  },
  {
    title: "Driver Management",
    description:
      "Complete driver management solutions including performance monitoring, license tracking, and compliance management.",
    icon: Users,
    bgColor: "bg-green-500",
    borderColor: "border-green-700",
    iconColor: "text-green-100",
    hoverBg: "hover:bg-green-600",
  },
  {
    title: "Fuel Management",
    description: "Comprehensive fuel consumption tracking and optimization. Reduce fuel costs with detailed analytics.",
    icon: Fuel,
    bgColor: "bg-amber-500",
    borderColor: "border-amber-700",
    iconColor: "text-amber-100",
    hoverBg: "hover:bg-amber-600",
  },
];

export function OfferingsSection() {
  return (
    <>
      <style jsx>{`
        @keyframes fadeIn {
          from { opacity: 0; }
          to { opacity: 1; }
        }

        @keyframes fadeInUp {
          from {
            opacity: 0;
            transform: translateY(20px);
          }
          to {
            opacity: 1;
            transform: translateY(0);
          }
        }

        .animate-fade-in {
          animation: fadeIn 0.5s ease-out forwards;
        }

        .animate-fade-in-up {
          animation: fadeInUp 0.5s ease-out forwards;
        }
      `}</style>

      <section className="py-20 bg-white">
        <div className="container mx-auto px-4">
          <div className="text-center mb-16 animate-fade-in">
            <h2 className="text-3xl font-bold mb-4 bg-gradient-to-r from-blue-700 to-indigo-700 bg-clip-text text-transparent">
              What We Offer
            </h2>
            <p className="text-gray-700 font-medium">TAILORED FLEET MANAGEMENT SERVICES</p>
          </div>
          
          <div className="grid md:grid-cols-2 gap-8">
            {offerings.map((offering, index) => (
              <div
                key={index}
                style={{
                  animationDelay: `${index * 100}ms`,
                }}
                className={`group flex gap-6 p-6 rounded-xl border-2 ${offering.borderColor} ${offering.bgColor} ${offering.hoverBg} shadow-md hover:shadow-xl transition-all duration-300 ease-out hover:-translate-y-1 animate-fade-in-up`}
              >
                <div className="flex-shrink-0">
                  <div className="flex h-12 w-12 items-center justify-center">
                    <offering.icon 
                      className={`h-12 w-12 ${offering.iconColor} transition-all duration-300 group-hover:scale-110`} 
                    />
                  </div>
                </div>
                
                <div>
                  <h3 className="text-xl font-bold text-white mb-2 group-hover:translate-x-1 transition-transform duration-300">
                    {offering.title}
                  </h3>
                  
                  <p className="text-gray-100">
                    {offering.description}
                  </p>
                  
                  <div className="mt-3 h-0.5 w-0 bg-white/40 transition-all duration-500 group-hover:w-full"></div>
                </div>
              </div>
            ))}
          </div>
        </div>
      </section>
    </>
  );
}