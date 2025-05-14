"use client"

import { motion } from "framer-motion"
import { User, Briefcase, Code, HeadphonesIcon } from "lucide-react"

const teamMembers = [
  {
    icon: Briefcase,
    title: "Industry Experts",
    description: "With decades of transportation and logistics experience",
    color: "text-blue-600",
    gradient: "from-blue-500 to-blue-600"
  },
  {
    icon: Code,
    title: "Software Engineers",
    description: "Creating innovative solutions for complex problems",
    color: "text-indigo-600",
    gradient: "from-indigo-500 to-indigo-600"
  },
  {
    icon: User,
    title: "Data Scientists",
    description: "Turning fleet data into actionable insights",
    color: "text-purple-600",
    gradient: "from-purple-500 to-purple-600"
  },
  {
    icon: HeadphonesIcon,
    title: "Support Specialists",
    description: "Dedicated to your success 24/7",
    color: "text-green-600",
    gradient: "from-green-500 to-green-600"
  }
]

export function TeamSection() {
  const containerVariants = {
    hidden: { opacity: 0 },
    visible: {
      opacity: 1,
      transition: {
        staggerChildren: 0.1
      }
    }
  }

  const titleVariants = {
    hidden: { opacity: 0, y: 15 },
    visible: { 
      opacity: 1, 
      y: 0,
      transition: { duration: 0.5, ease: "easeOut" }
    }
  }

  const memberVariants = {
    hidden: { opacity: 0, y: 15 },
    visible: (i: number) => ({
      opacity: 1,
      y: 0,
      transition: { 
        delay: i * 0.1,
        duration: 0.4,
        ease: "easeOut"
      }
    })
  }

  const buttonVariants = {
    hidden: { opacity: 0, y: 10 },
    visible: { 
      opacity: 1, 
      y: 0,
      transition: { 
        delay: 0.5, 
        duration: 0.5,
        ease: "easeOut"
      }
    },
    hover: { 
      scale: 1.05,
      boxShadow: "0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05)"
    },
    tap: { scale: 0.98 }
  }

  return (
    <motion.div 
      className="max-w-4xl mx-auto"
      variants={containerVariants}
      initial="hidden"
      whileInView="visible"
      viewport={{ once: true, margin: "-50px" }}
    >
      <motion.div 
        className="bg-gradient-to-r from-white to-blue-50 p-4 sm:p-6 md:p-8 rounded-xl shadow-sm border border-blue-100"
        variants={titleVariants}
      >
        <motion.div className="text-center mb-6 sm:mb-8" variants={titleVariants}>
          <motion.div 
            className="inline-block mb-2 px-3 py-1 bg-blue-100 text-blue-800 rounded-full text-xs sm:text-sm font-medium"
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
          >
            Our People
          </motion.div>
          <h2 className="text-2xl sm:text-3xl font-semibold bg-gradient-to-r from-blue-700 to-indigo-700 bg-clip-text text-transparent">
            Our Team
          </h2>
        </motion.div>
        
        <motion.p 
          className="mb-6 sm:mb-8 text-gray-600 leading-relaxed text-center max-w-3xl mx-auto text-sm sm:text-base"
          variants={titleVariants}
        >
          Our team consists of industry experts, software engineers, data scientists, and customer support specialists who
          are passionate about creating the best fleet management solution on the market.
        </motion.p>
        
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 sm:gap-6 mt-6 sm:mt-8">
          {teamMembers.map((member, index) => (
            <motion.div 
              key={index} 
              className="bg-white p-4 sm:p-6 rounded-lg shadow-sm flex items-center space-x-3 sm:space-x-4 border border-gray-100"
              custom={index}
              variants={memberVariants}
              whileHover={{ 
                y: -3, 
                boxShadow: "0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05)"
              }}
              transition={{ type: "spring", stiffness: 300, damping: 20 }}
            >
              <motion.div 
                className={`bg-gradient-to-r ${member.gradient} p-2 sm:p-3 rounded-full shadow-sm`}
                whileHover={{ scale: 1.1 }}
                transition={{ type: "spring", stiffness: 400, damping: 10 }}
              >
                <member.icon className="h-4 w-4 sm:h-6 sm:w-6 text-white" />
              </motion.div>
              <div>
                <h3 className={`font-semibold bg-gradient-to-r ${member.gradient} bg-clip-text text-transparent text-sm sm:text-base`}>
                  {member.title}
                </h3>
                <p className="text-gray-600 text-xs sm:text-sm">{member.description}</p>
              </div>
            </motion.div>
          ))}
        </div>
        
        <motion.div 
          className="mt-8 sm:mt-10 text-center"
          variants={buttonVariants}
        >
          <motion.button 
            className="px-4 sm:px-6 py-2 sm:py-3 bg-gradient-to-r from-blue-600 to-indigo-600 text-white text-sm sm:text-base font-medium rounded-lg shadow-md hover:shadow-lg transition-all duration-200"
            whileHover="hover"
            whileTap="tap"
          >
            Join Our Team
          </motion.button>
        </motion.div>
      </motion.div>
    </motion.div>
  )
}