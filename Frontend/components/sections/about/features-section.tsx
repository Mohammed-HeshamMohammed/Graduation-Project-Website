"use client"

import { motion } from "framer-motion"
import { Building, Users, Truck, Clock, Award, Globe } from "lucide-react"

const features = [
  {
    icon: Building,
    title: "Comprehensive Solution",
    description: "All-in-one platform for vehicle, driver, and maintenance management",
    gradient: "from-blue-500 to-blue-600",
    bgGradient: "from-blue-50 to-blue-100",
    iconColor: "text-blue",
  },
  {
    icon: Users,
    title: "User-Friendly Interface",
    description: "Intuitive design that requires minimal training",
    gradient: "from-green-500 to-green-600",
    bgGradient: "from-green-50 to-green-100",
    iconColor: "text-green",
  },
  {
    icon: Truck,
    title: "Real-Time Tracking",
    description: "Monitor your fleet's performance and location in real-time",
    gradient: "from-purple-500 to-purple-600",
    bgGradient: "from-purple-50 to-purple-100",
    iconColor: "text-purple",
  },
  {
    icon: Clock,
    title: "Proactive Maintenance",
    description: "Schedule and track maintenance to prevent costly breakdowns",
    gradient: "from-amber-500 to-amber-600",
    bgGradient: "from-amber-50 to-amber-100",
    iconColor: "text-amber",
  },
  {
    icon: Award,
    title: "Industry Expertise",
    description: "Built by experts with decades of fleet management experience",
    gradient: "from-indigo-500 to-indigo-600",
    bgGradient: "from-indigo-50 to-indigo-100",
    iconColor: "text-indigo",
  },
  {
    icon: Globe,
    title: "Global Support",
    description: "24/7 customer support to assist you whenever you need help",
    gradient: "from-red-500 to-red-600",
    bgGradient: "from-red-50 to-red-100",
    iconColor: "text-red",
  },
]

export function FeaturesSection() {
  const containerVariants = {
    hidden: { opacity: 0 },
    visible: {
      opacity: 1,
      transition: {
        staggerChildren: 0.08,
        delayChildren: 0.1
      }
    }
  }

  const itemVariants = {
    hidden: { opacity: 0, y: 15 },
    visible: { 
      opacity: 1, 
      y: 0,
      transition: { duration: 0.5, ease: "easeOut" }
    }
  }

  const iconVariants = {
    hidden: { scale: 0, rotate: -5 },
    visible: { 
      scale: 1, 
      rotate: 0,
      transition: { type: "spring", stiffness: 260, damping: 20 }
    },
    hover: { 
      scale: 1.1, 
      rotate: 0,
      transition: { type: "spring", stiffness: 400, damping: 10 }
    }
  }

  return (
    <motion.div 
      className="max-w-4xl mx-auto"
      variants={containerVariants}
      initial="hidden"
      whileInView="visible"
      viewport={{ once: true, margin: "-50px" }}
    >
      <motion.div className="text-center mb-8 md:mb-12" variants={itemVariants}>
        <motion.div 
          className="inline-block mb-2 px-3 py-1 bg-indigo-100 text-indigo-800 rounded-full text-xs sm:text-sm font-medium"
          whileHover={{ scale: 1.05 }}
          whileTap={{ scale: 0.95 }}
        >
          Features
        </motion.div>
        <h2 className="text-2xl sm:text-3xl font-semibold bg-gradient-to-r from-blue-700 to-indigo-700 bg-clip-text text-transparent">
          Why Choose Us
        </h2>
        <p className="text-gray-700 mt-3 max-w-2xl mx-auto text-sm sm:text-base">
          Discover how our platform can transform your fleet operations with these powerful features
        </p>
      </motion.div>
      
      <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 md:gap-6">
        {features.map((feature, index) => (
          <motion.div
            key={index}
            className={`flex items-start space-x-3 sm:space-x-4 p-4 sm:p-6 rounded-xl bg-gradient-to-br ${feature.bgGradient} hover:shadow-md transition-all duration-300 border border-gray-100`}
            variants={itemVariants}
            whileHover={{ 
              y: -3, 
              boxShadow: "0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05)"
            }}
          >
            <motion.div 
              className={`bg-gradient-to-r ${feature.gradient} p-2 sm:p-3 rounded-lg shadow-sm`}
              variants={iconVariants}
              whileHover="hover"
              transition={{ type: "spring", stiffness: 300, damping: 10 }}
            >
              <feature.icon className={`h-5 w-5 sm:h-6 sm:w-6 text-white`} />
            </motion.div>
            <div>
              <h3 className={`font-semibold text-base sm:text-lg bg-gradient-to-r ${feature.gradient} bg-clip-text text-transparent`}>
                {feature.title}
              </h3>
              <p className="text-gray-700 mt-1 text-sm sm:text-base">{feature.description}</p>
            </div>
          </motion.div>
        ))}
      </div>
    </motion.div>
  )
}