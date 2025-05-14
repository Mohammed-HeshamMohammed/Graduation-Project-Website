// components/sections/services/service-details.tsx
"use client";

import React, { useState, useRef } from "react";
import { motion, useScroll, useInView } from "framer-motion";
import { ServiceCard } from "./ServiceCard";
import { ServiceCTA } from "./ServiceCTA";
import { Truck, Users, PenToolIcon, Map, Fuel } from "lucide-react";

// Define the Service interface here to avoid circular dependencies
export interface Service {
  id: string;
  title: string;
  description: string;
  icon: React.ElementType;
  image: string;
  features: string[];
  color: string;
  iconColor: string;
  gradient: string;
  featureColor: string;
  highlightColor: string;
}

const servicesData: Service[] = [
  {
    id: "fleet-management",
    title: "Fleet Management",
    description: "Comprehensive vehicle tracking and management system",
    icon: Truck,
    image: "/images/fleet-m1.jpg",
    features: [
      "Real-time vehicle tracking and location monitoring",
      "Vehicle utilization and performance analytics",
      "Comprehensive vehicle history and documentation",
      "Automated vehicle assignment and scheduling",
      "Custom vehicle grouping and categorization",
      "Vehicle acquisition and disposal management",
    ],
    color: "bg-blue-100 text-blue-600",
    iconColor: "text-blue-500",
    gradient: "from-blue-500 to-indigo-500",
    featureColor: "text-blue-700",
    highlightColor: "bg-blue-50",
  },
  {
    id: "driver-management",
    title: "Driver Management",
    description: "Complete driver monitoring and compliance solution",
    icon: Users,
    image: "/images/driver-management.jpg",
    features: [
      "Driver performance monitoring and scoring",
      "License and certification tracking with expiration alerts",
      "Hours of service compliance and reporting",
      "Driver training and qualification management",
      "Incident and violation tracking",
      "Driver assignment and scheduling",
    ],
    color: "bg-green-100 text-green-600",
    iconColor: "text-green-500",
    gradient: "from-green-500 to-teal-500",
    featureColor: "text-green-700",
    highlightColor: "bg-green-50",
  },
  {
    id: "maintenance-tracking",
    title: "Maintenance Tracking",
    description: "Proactive maintenance management to prevent costly breakdowns",
    icon: PenToolIcon,
    image: "/images/maintenance-tracking.jpg",
    features: [
      "Scheduled maintenance reminders and alerts",
      "Maintenance history and documentation",
      "Service provider management",
      "Parts inventory tracking",
      "Maintenance cost analysis",
      "Warranty tracking and management",
    ],
    color: "bg-yellow-100 text-yellow-600",
    iconColor: "text-yellow-500",
    gradient: "from-yellow-500 to-amber-500",
    featureColor: "text-yellow-700",
    highlightColor: "bg-yellow-50",
  },
  {
    id: "trip-analytics",
    title: "Trip Analytics",
    description: "Detailed trip data analysis for route optimization",
    icon: Map,
    image: "/images/trip-analytics.jpg",
    features: [
      "Route planning and optimization",
      "Trip history and reporting",
      "Fuel consumption analysis by trip",
      "Driver behavior analysis during trips",
      "Geofencing and location-based alerts",
      "Customer delivery time tracking",
    ],
    color: "bg-purple-100 text-purple-600",
    iconColor: "text-purple-500",
    gradient: "from-purple-500 to-indigo-500",
    featureColor: "text-purple-700",
    highlightColor: "bg-purple-50",
  },
  {
    id: "fuel-management",
    title: "Fuel Management",
    description: "Comprehensive fuel usage tracking and optimization",
    icon: Fuel,
    image: "/images/fuel-management.jpg",
    features: [
      "Fuel consumption tracking and reporting",
      "Fuel card integration and management",
      "Fuel theft and fraud detection",
      "Fuel economy analysis by vehicle and driver",
      "Fuel cost forecasting",
      "Alternative fuel tracking and analysis",
    ],
    color: "bg-red-100 text-red-600",
    iconColor: "text-red-500",
    gradient: "from-red-500 to-pink-500",
    featureColor: "text-red-700",
    highlightColor: "bg-red-50",
  },
];

export function ServiceDetails() {
  const [activeService, setActiveService] = useState<string | null>(null);
  const [highlightedFeature, setHighlightedFeature] = useState<{ serviceId: string; featureIndex: number } | null>(null);
  const [hoveredService, setHoveredService] = useState<string | null>(null);

  const containerRef = useRef<HTMLDivElement>(null);
  const { scrollYProgress } = useScroll({
    target: containerRef,
    offset: ["start end", "end start"],
  });

  // Create an array of booleans indicating if each section is in view.
  const sectionRefs = useRef(servicesData.map(() => React.createRef<HTMLElement>()));
  const sectionInViewArray = servicesData.map((_, index) =>
    useInView(sectionRefs.current[index], { margin: "-15% 0px -15% 0px", once: false })
  );

  return (
    <div className="space-y-12 sm:space-y-16 relative rounded-lg" ref={containerRef}>
      {/* Header Section */}
      <motion.div
        initial={{ opacity: 0, y: 15 }}
        whileInView={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.65, ease: "easeOut" }}
        viewport={{ once: true, margin: "-80px" }}
        className="text-center mb-12 sm:mb-16 relative overflow-hidden rounded-lg"
      >
        <div className="absolute inset-0 -z-10 overflow-hidden opacity-20">
          <motion.div
            className="absolute inset-0 bg-gradient-to-r from-blue-100 to-indigo-100 rounded-full blur-lg"
            animate={{ scale: [1, 1.1, 1], rotate: [0, 5, 0] }}
            transition={{ duration: 8, repeat: Infinity, repeatType: "mirror", ease: "easeInOut" }}
            style={{ top: "-40%", left: "20%", width: "60%", height: "150%" }}
          />
        </div>

        <motion.div
          initial={{ scale: 0.95, opacity: 0 }}
          animate={{ scale: 1, opacity: 1 }}
          transition={{ duration: 0.5, delay: 0.2, ease: "easeOut" }}
          className="inline-block mb-2 px-4 py-1 bg-indigo-100 text-indigo-800 rounded-full text-xs sm:text-sm font-medium"
        >
          Detailed Services
        </motion.div>

        <motion.h2
          initial={{ y: 15, opacity: 0 }}
          animate={{ y: 0, opacity: 1 }}
          transition={{ duration: 0.75, delay: 0.3, ease: "easeOut" }}
          className="text-2xl sm:text-3xl md:text-4xl font-bold mb-3 bg-gradient-to-r from-blue-700 to-indigo-700 bg-clip-text text-transparent"
        >
          How We Can Help You
        </motion.h2>

        <motion.p
          initial={{ y: 15, opacity: 0 }}
          animate={{ y: 0, opacity: 1 }}
          transition={{ duration: 0.75, delay: 0.4, ease: "easeOut" }}
          className="text-gray-600 max-w-2xl mx-auto text-sm sm:text-base"
        >
          Explore our comprehensive fleet management solutions in detail
        </motion.p>
      </motion.div>

      {/* Map over services and render a ServiceCard for each */}
      {servicesData.map((service, index) => (
        <ServiceCard
          key={service.id}
          service={service}
          index={index}
          activeService={activeService}
          setActiveService={setActiveService}
          hoveredService={hoveredService}
          setHoveredService={setHoveredService}
          highlightedFeature={highlightedFeature}
          setHighlightedFeature={setHighlightedFeature}
          sectionInView={sectionInViewArray[index]}
        />
      ))}

      {/* Final CTA Section */}
      <ServiceCTA />
    </div>
  );
}