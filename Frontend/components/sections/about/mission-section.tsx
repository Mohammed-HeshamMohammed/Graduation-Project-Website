"use client"

import { motion } from "framer-motion"
import { Target } from "lucide-react"

export function MissionSection() {
  const containerVariants = {
    hidden: { opacity: 0 },
    visible: {
      opacity: 1,
      transition: {
        staggerChildren: 0.15
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

  const valuesVariants = {
    hidden: { opacity: 0, scale: 0.8 },
    visible: (i: number) => ({
      opacity: 1,
      scale: 1,
      transition: { 
        delay: i * 0.15,
        duration: 0.4,
        type: "spring",
        stiffness: 100
      }
    })
  }

  return (
    <motion.div 
      id="learn-more" 
      className="max-w-4xl mx-auto"
      initial="hidden"
      whileInView="visible"
      viewport={{ once: true, margin: "-50px" }}
      variants={containerVariants}
    >
      <motion.div 
        className="bg-gradient-to-r from-white to-blue-50 p-4 sm:p-6 md:p-8 rounded-xl shadow-sm border border-blue-100 relative overflow-hidden"
        variants={itemVariants}
      >
        {/* Background decoration */}
        <motion.div 
          className="absolute -top-16 -right-16 w-24 md:w-40 h-24 md:h-40 rounded-full bg-blue-100 opacity-40 blur-2xl"
          animate={{ 
            scale: [1, 1.2, 1],
            opacity: [0.4, 0.2, 0.4]
          }}
          transition={{ duration: 8, repeat: Infinity, repeatType: "reverse", ease: "easeInOut" }}
        />
        
        <motion.div 
          className="flex items-center mb-4 sm:mb-6"
          variants={itemVariants}
        >
          <motion.div 
            className="bg-gradient-to-r from-blue-600 to-indigo-600 p-2 rounded-lg shadow-sm"
            whileHover={{ scale: 1.05, rotate: 5 }}
            transition={{ type: "spring", stiffness: 400, damping: 10 }}
          >
            <Target className="h-5 w-5 sm:h-6 sm:w-6 text-white" />
          </motion.div>
          <h2 className="text-xl sm:text-2xl font-semibold bg-gradient-to-r from-blue-700 to-indigo-700 bg-clip-text text-transparent ml-3">
            Our Mission
          </h2>
        </motion.div>
        
        <motion.p 
          className="mb-6 text-gray-700 leading-relaxed text-sm sm:text-base"
          variants={itemVariants}
        >
          Our mission is to empower fleet managers with the tools and insights they need to make data-driven decisions,
          enhance operational efficiency, and maintain compliance with industry regulations. We strive to provide a
          user-friendly platform that addresses the complex challenges of modern fleet management.
        </motion.p>
        
        <motion.div 
          className="grid grid-cols-1 sm:grid-cols-3 gap-3 sm:gap-4 mt-6 sm:mt-8"
          variants={itemVariants}
        >
          {['Innovation', 'Reliability', 'Excellence'].map((value, index) => (
            <motion.div 
              key={index} 
              className="bg-white p-3 sm:p-4 rounded-lg shadow-sm text-center border border-gray-100"
              custom={index}
              variants={valuesVariants}
              whileHover={{ 
                y: -3, 
                boxShadow: "0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05)",
                backgroundColor: index === 0 ? "#EFF6FF" : index === 1 ? "#F0F9FF" : "#F5F3FF"
              }}
            >
              <motion.span 
                className="font-medium text-blue-700 text-sm sm:text-base"
                whileHover={{ scale: 1.05 }}
              >
                {value}
              </motion.span>
            </motion.div>
          ))}
        </motion.div>
      </motion.div>
    </motion.div>
  )
}