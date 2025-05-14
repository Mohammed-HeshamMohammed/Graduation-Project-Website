"use client"

import { useState } from "react"
import Image from "next/image"
import { motion } from "framer-motion"
import { MapPin, Maximize2, ZoomIn, ZoomOut } from "lucide-react"

export function ContactMap() {
  const [isHovered, setIsHovered] = useState(false)
  const [isTouched, setIsTouched] = useState(false)
  
  // Add touch event handlers for mobile
  const handleTouchStart = () => {
    setIsTouched(true)
    // Auto-hide controls after 3 seconds
    setTimeout(() => setIsTouched(false), 3000)
  }

  return (
    <motion.div 
      className="relative rounded-xl overflow-hidden shadow-lg border border-blue-100"
      initial={{ opacity: 0, y: 15 }} // Reduced y offset for mobile
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.4, delay: 0.1 }} // Faster animation for mobile
      onMouseEnter={() => setIsHovered(true)}
      onMouseLeave={() => setIsHovered(false)}
      onTouchStart={handleTouchStart}
    >
      <div className="relative h-[200px] sm:h-[250px] md:h-[300px] w-full"> {/* Responsive height */}
        <Image 
          src="/images/office-map.jpg" 
          alt="Office Location" 
          fill 
          className="object-cover transition-transform duration-500" // Reduced duration
          style={{ transform: (isHovered || isTouched) ? 'scale(1.03)' : 'scale(1)' }} // Reduced scale for mobile
        />
        
        <div className="absolute inset-0 bg-gradient-to-br from-blue-600/30 to-indigo-600/30" />
        
        {/* Interactive map pin - simplified animation for mobile */}
        <motion.div 
          className="absolute top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2"
          initial={{ y: -10 }}
          animate={{ y: [-3, 0, -3] }} // Reduced bouncing for mobile
          transition={{ repeat: Infinity, duration: 1.5, ease: "easeInOut" }}
        >
          <motion.div
            whileTap={{ scale: 1.2 }} // Added tap effect for mobile
            whileHover={{ scale: 1.1 }} // Reduced scale for mobile
            className="flex flex-col items-center"
          >
            <MapPin className="h-8 w-8 md:h-10 md:w-10 text-red-500 drop-shadow-lg" fill="#fee2e2" />
            <div className="mt-1 px-2 py-1 rounded-full bg-white shadow-md">
              <span className="text-xs font-medium text-gray-800">Our Office</span>
            </div>
          </motion.div>
        </motion.div>
        
        {/* Controls overlay - appears on hover or touch */}
        <motion.div 
          className="absolute bottom-3 right-3 flex gap-2"
          initial={{ opacity: 0 }}
          animate={{ opacity: (isHovered || isTouched) ? 1 : 0 }}
          transition={{ duration: 0.3 }}
        >
          {/* Increased button size for better touch targets */}
          <motion.button
            className="p-3 bg-white/90 backdrop-blur-sm rounded-full shadow-md hover:bg-white transition-colors"
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
          >
            <ZoomIn className="h-4 w-4 text-gray-700" />
          </motion.button>
          <motion.button
            className="p-3 bg-white/90 backdrop-blur-sm rounded-full shadow-md hover:bg-white transition-colors"
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
          >
            <ZoomOut className="h-4 w-4 text-gray-700" />
          </motion.button>
          <motion.button
            className="p-3 bg-white/90 backdrop-blur-sm rounded-full shadow-md hover:bg-white transition-colors"
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
          >
            <Maximize2 className="h-4 w-4 text-gray-700" />
          </motion.button>
        </motion.div>
      </div>
      
      {/* Caption bar */}
      <div className="absolute bottom-0 inset-x-0 bg-gradient-to-t from-black/70 to-transparent p-3 md:p-4">
        <p className="text-white text-xs md:text-sm font-medium">123 Fleet Street, Business District</p>
      </div>
    </motion.div>
  )
}