"use client"

import { Mail, Phone, MapPin, Clock } from "lucide-react"
import { motion } from "framer-motion"

export function ContactInfo() {
  // Simplified animations for mobile performance
  const containerVariants = {
    hidden: { opacity: 0 },
    visible: {
      opacity: 1,
      transition: {
        delayChildren: 0.2,
        staggerChildren: 0.1 // Faster staggering for mobile
      }
    }
  }

  const itemVariants = {
    hidden: { y: 10, opacity: 0 }, // Reduced offset for mobile
    visible: {
      y: 0,
      opacity: 1,
      transition: { duration: 0.3 } // Faster animation for mobile
    }
  }

  // Simplified icon animation for mobile
  const iconVariants = {
    initial: { scale: 0.9 }, // Less dramatic initial state
    animate: { scale: 1 },
    hover: { scale: 1.05, y: -1 } // Smaller animation effect for mobile
  }

  return (
    <motion.div 
      className="grid gap-4 md:gap-6" // Reduced gap for mobile
      variants={containerVariants}
      initial="hidden"
      animate="visible"
    >
      <motion.div 
        className="group flex items-start gap-3 md:gap-4" // Reduced gap for mobile
        variants={itemVariants}
        whileHover={{ x: 3 }} // Reduced hover effect for mobile
      >
        <motion.div 
          className="rounded-full bg-gradient-to-br from-blue-500 to-indigo-600 p-2 md:p-3 shadow-md shadow-blue-200"
          variants={iconVariants}
          initial="initial"
          animate="animate"
          whileHover="hover"
          transition={{ type: "spring", stiffness: 300, damping: 15 }} // Reduced spring effect
        >
          <Mail className="h-5 w-5 md:h-6 md:w-6 text-white" />
        </motion.div>
        <div className="pt-1">
          <h3 className="font-semibold text-base md:text-lg text-blue-600">Email</h3>
          <a 
            href="mailto:info@fleetmanager.com" 
            className="text-gray-600 group-hover:text-blue-600 transition-colors duration-300 hover:underline text-sm md:text-base"
          >
            info@fleetmanager.com
          </a>
        </div>
      </motion.div>

      <motion.div 
        className="group flex items-start gap-3 md:gap-4" // Reduced gap for mobile
        variants={itemVariants}
        whileHover={{ x: 3 }} // Reduced hover effect for mobile
      >
        <motion.div 
          className="rounded-full bg-gradient-to-br from-indigo-500 to-purple-600 p-2 md:p-3 shadow-md shadow-indigo-200"
          variants={iconVariants}
          initial="initial"
          animate="animate"
          whileHover="hover"
          transition={{ type: "spring", stiffness: 300, damping: 15 }} // Reduced spring effect
        >
          <Phone className="h-5 w-5 md:h-6 md:w-6 text-white" />
        </motion.div>
        <div className="pt-1">
          <h3 className="font-semibold text-base md:text-lg text-indigo-600">Phone</h3>
          <a 
            href="tel:+15551234567" 
            className="text-gray-600 group-hover:text-indigo-600 transition-colors duration-300 hover:underline text-sm md:text-base"
          >
            +1 (555) 123-4567
          </a>
        </div>
      </motion.div>

      <motion.div 
        className="group flex items-start gap-3 md:gap-4" // Reduced gap for mobile
        variants={itemVariants}
        whileHover={{ x: 3 }} // Reduced hover effect for mobile
      >
        <motion.div 
          className="rounded-full bg-gradient-to-br from-purple-500 to-pink-600 p-2 md:p-3 shadow-md shadow-purple-200"
          variants={iconVariants}
          initial="initial"
          animate="animate"
          whileHover="hover"
          transition={{ type: "spring", stiffness: 300, damping: 15 }} // Reduced spring effect
        >
          <MapPin className="h-5 w-5 md:h-6 md:w-6 text-white" />
        </motion.div>
        <div className="pt-1">
          <h3 className="font-semibold text-base md:text-lg text-purple-600">Address</h3>
          <p className="text-gray-600 group-hover:text-purple-600 transition-colors duration-300 text-sm md:text-base">
            123 Fleet Street, Business District, City, 12345
          </p>
        </div>
      </motion.div>

      <motion.div 
        className="group flex items-start gap-3 md:gap-4" // Reduced gap for mobile
        variants={itemVariants}
        whileHover={{ x: 3 }} // Reduced hover effect for mobile
      >
        <motion.div 
          className="rounded-full bg-gradient-to-br from-pink-500 to-rose-600 p-2 md:p-3 shadow-md shadow-pink-200"
          variants={iconVariants}
          initial="initial"
          animate="animate"
          whileHover="hover"
          transition={{ type: "spring", stiffness: 300, damping: 15 }} // Reduced spring effect
        >
          <Clock className="h-5 w-5 md:h-6 md:w-6 text-white" />
        </motion.div>
        <div className="pt-1">
          <h3 className="font-semibold text-base md:text-lg text-pink-600">Business Hours</h3>
          <p className="text-gray-600 group-hover:text-pink-600 transition-colors duration-300 text-sm md:text-base">
            Monday - Friday: 9:00 AM - 5:00 PM
          </p>
        </div>
      </motion.div>
    </motion.div>
  )
}