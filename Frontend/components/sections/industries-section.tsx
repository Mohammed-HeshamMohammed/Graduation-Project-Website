"use client"

import { motion } from "framer-motion"
import Image from "next/image"
import { Package, Building, Coffee, ShoppingBag, Users } from "lucide-react"

const industries = [
  { name: "Logistics & Distribution", icon: Package },
  { name: "Construction", icon: Building },
  { name: "Food & Beverage Delivery", icon: Coffee },
  { name: "Retail & E-commerce", icon: ShoppingBag },
  { name: "Passenger Transport", icon: Users },
]

export function IndustriesSection() {
  return (
    <section className="relative py-20 bg-white">
      <div className="container mx-auto px-4">
        <div className="grid md:grid-cols-2 gap-12 items-center">
          {/* Left Column */}
          <motion.div
            initial={{ opacity: 0, x: -30 }}
            whileInView={{ opacity: 1, x: 0 }}
            transition={{ duration: 0.6 }}
            viewport={{ once: true }}
          >
            <h2 className="text-3xl font-bold mb-6 bg-gradient-to-r from-blue-600 to-indigo-600 bg-clip-text text-transparent">
              INDUSTRY SECTORS COVERAGE
            </h2>
            <p className="text-gray-600 mb-8">
              We provide specialized fleet management solutions across various industries, ensuring optimal performance
              and efficiency for every type of fleet operation.
            </p>
            <div className="space-y-4">
              {industries.map((industry, index) => (
                <motion.div
                  key={index}
                  className="flex items-center gap-4"
                  initial={{ opacity: 0, x: -10 }}
                  whileInView={{ opacity: 1, x: 0 }}
                  transition={{ duration: 0.4, delay: index * 0.1 }}
                  viewport={{ once: true }}
                >
                  <motion.span
                    whileHover={{ scale: 1.15 }}
                    transition={{ type: "spring", stiffness: 200 }}
                    className="flex items-center justify-center"
                  >
                    <industry.icon className="h-8 w-8 text-yellow-500" />
                  </motion.span>
                  <span className="text-lg text-gray-800 font-medium">{industry.name}</span>
                </motion.div>
              ))}
            </div>
          </motion.div>

          {/* Right Column (Image - No Card Effect) */}
          <motion.div
            className="relative h-[400px] w-full"
            initial={{ opacity: 0, x: 30 }}
            whileInView={{ opacity: 1, x: 0 }}
            transition={{ duration: 0.6 }}
            viewport={{ once: true }}
          >
            <Image
              src="/images/fleet-management.jpg"
              alt="Industry Coverage"
              fill
              className="object-cover rounded-none"
              priority
            />
          </motion.div>
        </div>
      </div>
    </section>
  )
}
