"use client"

import { motion } from "framer-motion"
import { ChevronRight } from "lucide-react"

export function AboutHeroSection() {
  return (
    <motion.div 
      className="relative overflow-hidden rounded-xl bg-gradient-to-r from-blue-50 to-indigo-50 p-4 sm:p-6 md:p-8 shadow-sm border border-blue-100"
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      transition={{ duration: 0.6 }}
    >
      {/* Animated background elements */}
      <motion.div 
        className="absolute -right-10 -top-10 h-24 md:h-40 w-24 md:w-40 rounded-full bg-blue-100 opacity-50"
        animate={{ 
          scale: [1, 1.2, 1],
          opacity: [0.5, 0.3, 0.5],
        }}
        transition={{ duration: 12, repeat: Infinity, ease: "easeInOut" }}
      />
      <motion.div 
        className="absolute -bottom-10 -left-10 h-24 md:h-40 w-24 md:w-40 rounded-full bg-indigo-100 opacity-50"
        animate={{ 
          scale: [1, 1.1, 0.9, 1],
          opacity: [0.5, 0.4, 0.6, 0.5],
        }}
        transition={{ duration: 10, repeat: Infinity, repeatType: "reverse", ease: "easeInOut" }}
      />
      
      {/* Small decorative elements */}
      <motion.div 
        className="absolute top-1/4 right-1/4 h-3 md:h-5 w-3 md:w-5 rounded-full bg-blue-400 opacity-20"
        animate={{ y: [0, -10, 0], opacity: [0.2, 0.5, 0.2] }}
        transition={{ duration: 4, repeat: Infinity, repeatType: "reverse", ease: "easeInOut" }}
      />
      <motion.div 
        className="absolute bottom-1/3 left-1/3 h-2 md:h-3 w-2 md:w-3 rounded-full bg-indigo-500 opacity-20"
        animate={{ y: [0, 8, 0], opacity: [0.2, 0.4, 0.2] }}
        transition={{ duration: 3, repeat: Infinity, repeatType: "reverse", delay: 1, ease: "easeInOut" }}
      />
      
      <div className="relative max-w-4xl mx-auto">
        <motion.div 
          className="inline-block mb-2 px-3 py-1 bg-blue-100 text-blue-800 rounded-full text-xs sm:text-sm font-medium"
          initial={{ opacity: 0, x: -10 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ delay: 0.1, ease: "easeOut" }}
        >
          About Us
        </motion.div>
        
        <motion.h1 
          className="text-2xl sm:text-3xl md:text-4xl lg:text-5xl font-bold mb-4 md:mb-6 bg-gradient-to-r from-blue-700 to-indigo-700 bg-clip-text text-transparent"
          initial={{ opacity: 0, y: 15 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.2, duration: 0.5, ease: "easeOut" }}
        >
          About Fleet Management System
        </motion.h1>
        
        <motion.p 
          className="text-base sm:text-lg mb-6 md:mb-8 text-gray-700 max-w-3xl leading-relaxed"
          initial={{ opacity: 0, y: 15 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.3, duration: 0.5, ease: "easeOut" }}
        >
          Fleet Management System is a comprehensive solution designed to help businesses efficiently manage their vehicle
          fleets, drivers, maintenance schedules, and trip data. Our platform provides real-time insights and analytics to
          optimize operations, reduce costs, and improve overall fleet performance.
        </motion.p>
        
        <motion.a 
          href="#learn-more" 
          className="inline-flex items-center px-4 sm:px-6 py-2 sm:py-3 bg-gradient-to-r from-blue-600 to-indigo-600 text-white text-sm sm:text-base font-medium rounded-lg shadow-md hover:shadow-lg transition-all duration-200 group"
          initial={{ opacity: 0, y: 15 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.4, duration: 0.5, ease: "easeOut" }}
          whileHover={{ scale: 1.03 }}
          whileTap={{ scale: 0.98 }}
        >
          Learn More 
          <motion.span
            className="ml-2"
            animate={{ x: [0, 3, 0] }}
            transition={{ duration: 1.5, repeat: Infinity, repeatType: "loop", ease: "easeInOut" }}
          >
            <ChevronRight className="h-4 w-4" />
          </motion.span>
        </motion.a>
      </div>
    </motion.div>
  )
}