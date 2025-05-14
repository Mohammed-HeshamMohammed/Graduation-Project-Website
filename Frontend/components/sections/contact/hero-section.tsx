"use client"

import { motion } from "framer-motion"
import { Headset, MessageCircle, Mail, ArrowRight } from "lucide-react"
import { Button } from "@/components/ui/button"

export function ContactHeroSection() {
  return (
    <motion.div 
      className="space-y-6 md:space-y-8 relative overflow-hidden px-4 sm:px-6 py-6 sm:py-8" 
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      transition={{ duration: 0.7 }}
    >
      {/* Background decoration - adjusted for mobile */}
      <div className="absolute -top-12 -right-12 sm:-top-16 sm:-right-16 w-48 sm:w-64 h-48 sm:h-64 rounded-full bg-blue-100/50 blur-3xl" />
      <div className="absolute -bottom-24 -left-12 sm:-bottom-32 sm:-left-16 w-56 sm:w-72 h-56 sm:h-72 rounded-full bg-indigo-100/50 blur-3xl" />
      
      <div className="relative">
        {/* Badge - simplified animation for mobile */}
        <motion.div 
          className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full bg-blue-50 border border-blue-100 mb-3 md:mb-4 text-xs sm:text-sm text-blue-700"
          initial={{ opacity: 0, y: -10 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.3 }}
        >
          <span className="relative flex h-1.5 w-1.5 sm:h-2 sm:w-2">
            <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-blue-400 opacity-75"></span>
            <span className="relative inline-flex rounded-full h-1.5 w-1.5 sm:h-2 sm:w-2 bg-blue-600"></span>
          </span>
          24/7 Customer Support
        </motion.div>
        
        {/* Title with animated gradient - responsive text sizes */}
        <motion.h1 
          className="relative text-3xl sm:text-4xl md:text-5xl lg:text-6xl font-bold tracking-tight"
          initial={{ opacity: 0, y: 15 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.1, duration: 0.6 }}
        >
          <span className="bg-gradient-to-r from-blue-700 via-indigo-600 to-purple-700 bg-clip-text text-transparent bg-300% animate-gradient">
            Contact Us
          </span>
        </motion.h1>
        
        {/* Description - responsive text and width */}
        <motion.p 
          className="mt-4 sm:mt-6 text-base sm:text-lg text-gray-600 max-w-full sm:max-w-xl"
          initial={{ opacity: 0, y: 15 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.2, duration: 0.6 }}
        >
          Have questions about our fleet management solution? Our team is here to help you optimize your fleet operations and reduce costs.
        </motion.p>
        
        {/* Quick action buttons - full width on mobile */}
        <motion.div 
          className="mt-6 sm:mt-8 flex flex-col sm:flex-row gap-3 sm:gap-4 w-full"
          initial={{ opacity: 0, y: 15 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.3, duration: 0.6 }}
        >
          <Button 
            className="bg-blue-600 hover:bg-blue-700 group flex items-center justify-center gap-2 w-full sm:w-auto"
          >
            <Mail className="h-4 w-4" />
            <span>Email Us</span>
            <ArrowRight className="h-4 w-4 opacity-0 -ml-4 group-hover:opacity-100 group-hover:ml-0 transition-all" />
          </Button>
          <Button 
            variant="outline" 
            className="border-blue-200 text-blue-700 hover:bg-blue-600 hover:text-white hover:border-blue-600 transition-colors duration-200 group flex items-center justify-center gap-2 w-full sm:w-auto"
          >
            <Headset className="h-4 w-4" />
            <span>Call Support</span>
            <ArrowRight className="h-4 w-4 opacity-0 -ml-4 group-hover:opacity-100 group-hover:ml-0 transition-all" />
          </Button>
        </motion.div>
      </div>
      
      {/* Features/Benefits - grid adjusts to single column on mobile */}
      <motion.div 
        className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-3 sm:gap-4 mt-6 sm:mt-8"
        variants={{
          hidden: { opacity: 0 },
          show: {
            opacity: 1,
            transition: {
              staggerChildren: 0.1,
              delayChildren: 0.3
            }
          }
        }}
        initial="hidden"
        animate="show"
      >
        {[
          { icon: <MessageCircle className="h-5 w-5 text-blue-600" />, text: "Quick Response Time" },
          { icon: <Headset className="h-5 w-5 text-indigo-600" />, text: "Dedicated Support Team" },
          { icon: <Mail className="h-5 w-5 text-purple-600" />, text: "Personalized Solutions" }
        ].map((item, index) => (
          <motion.div
            key={index}
            className="flex items-center gap-3 bg-white rounded-lg p-3 sm:p-4 shadow-sm border border-gray-100"
            variants={{
              hidden: { opacity: 0, y: 15 },
              show: { opacity: 1, y: 0 }
            }}
            // Reduced hover effect for mobile
            whileHover={{ 
              y: -3, 
              transition: { duration: 0.2 } 
            }}
            // Added touch-friendly tap animation
            whileTap={{ 
              scale: 0.98,
              transition: { duration: 0.1 } 
            }}
          >
            <div className="rounded-full bg-gray-50 p-1.5 sm:p-2">{item.icon}</div>
            <span className="text-xs sm:text-sm font-medium text-gray-800">{item.text}</span>
          </motion.div>
        ))}
      </motion.div>
    </motion.div>
  )
}