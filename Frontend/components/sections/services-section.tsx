"use client"

import { useState } from "react"
import Image from "next/image"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Truck, ChevronDown, ChevronUp, CheckCircle,Shield,Cog } from "lucide-react"
import { motion, AnimatePresence } from "framer-motion"

const services = [
  {
    title: "COMMERCIAL FLEET",
    description:
      "Comprehensive fleet management solutions for commercial vehicles including trucks, vans, and delivery vehicles.",
    image: "/images/commercial-fleet.jpg",
    icon: Truck,
    color: "#3B82F6", // Blue
    details: [
      "Real-time GPS tracking and monitoring",
      "Maintenance scheduling and alerts",
      "Fuel consumption optimization",
      "Driver behavior monitoring",
      "Route optimization and planning",
      "Compliance management",
    ],
  },
  {
    title: "CORPORATE FLEET",
    description:
      "Professional management services for corporate car fleets, ensuring optimal performance and cost efficiency.",
    image: "/images/corporate-fleet.jpg",
    icon: Shield,
    color: "#10B981", // Green
    details: [
      "Vehicle lifecycle management",
      "Cost analysis and reporting",
      "Policy compliance monitoring",
      "Driver assignment and management",
      "Preventive maintenance scheduling",
      "Fuel card management",
    ],
  },
  {
    title: "SPECIALIZED VEHICLES",
    description:
      "Expert management of specialized vehicle fleets including construction equipment and service vehicles.",
    image: "/images/specialized-fleet.jpg",
    icon: Cog,
    color: "#8B5CF6", // Purple
    details: [
      "Equipment utilization tracking",
      "Specialized maintenance management",
      "Custom reporting solutions",
      "Asset lifecycle optimization",
      "Operator certification tracking",
      "Regulatory compliance management",
    ],
  },
]

export function ServicesSection() {
  const [activeService, setActiveService] = useState<number | null>(null)

  const toggleService = (index: number) => {
    setActiveService(activeService === index ? null : index)
  }

  return (
    <section className="relative -mt-32 pb-20 bg-transparent">
      <div className="container mx-auto px-4">
        <div className="grid md:grid-cols-3 gap-8">
          {services.map((service, index) => (
            <motion.div
              key={index}
              initial={{ opacity: 0, y: 50 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.5, delay: index * 0.2 }}
            >
              <Card 
                className="group overflow-hidden hover:shadow-xl transition-all duration-300 bg-white"
                style={{ 
                  borderWidth: '2px', 
                  borderColor: service.color,
                  boxShadow: `0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06), 0 0 0 1px ${service.color}30`
                }}
              >
                <div className="relative h-48 overflow-hidden" style={{ borderBottom: `2px solid ${service.color}` }}>
                  <Image
                    src={service.image || "/placeholder.svg"}
                    alt={service.title}
                    fill
                    className="object-cover scale-105 transition-transform duration-500 group-hover:scale-110"
                  />
                  <div className="absolute inset-0 bg-gradient-to-t from-black/60 to-transparent" />
                  <div 
                    className="absolute bottom-0 left-0 right-0 p-4"
                    style={{ 
                      background: `linear-gradient(to right, ${service.color}99, transparent)`,
                      borderTopRightRadius: '2rem'
                    }}
                  >
                    <h3 className="text-white font-bold text-xl">{service.title}</h3>
                  </div>
                </div>
                <CardHeader style={{ borderBottom: `1px solid ${service.color}20` }}>
                  <CardTitle className="flex items-center gap-2 text-black">
                    <service.icon className="h-5 w-5" style={{ color: service.color }} />
                    <span style={{ color: service.color }}>{service.title}</span>
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <p className="text-gray-600 mb-4">{service.description}</p>
                  <Button
                    variant="outline"
                    className="w-full flex items-center justify-between hover:bg-gray-50"
                    onClick={() => toggleService(index)}
                    style={{ 
                      borderColor: service.color,
                      color: service.color
                    }}
                  >
                    <span>{activeService === index ? "SHOW LESS" : "LEARN MORE"}</span>
                    {activeService === index ? (
                      <ChevronUp className="h-4 w-4" />
                    ) : (
                      <ChevronDown className="h-4 w-4" />
                    )}
                  </Button>

                  <AnimatePresence>
                    {activeService === index && (
                      <motion.div
                        initial={{ opacity: 0, height: 0 }}
                        animate={{ opacity: 1, height: "auto" }}
                        exit={{ opacity: 0, height: 0 }}
                        transition={{ duration: 0.3 }}
                        className="overflow-hidden"
                      >
                        <div className="pt-4 space-y-2">
                          <h4 className="font-semibold" style={{ color: service.color }}>Our Services Include:</h4>
                          <ul className="space-y-3 pl-1 text-gray-600">
                            {service.details.map((detail, i) => (
                              <motion.li
                                key={i}
                                initial={{ opacity: 0, x: -20 }}
                                animate={{ opacity: 1, x: 0 }}
                                transition={{ duration: 0.2, delay: i * 0.1 }}
                                className="flex items-start gap-2"
                              >
                                <CheckCircle className="h-5 w-5 mt-0.5 flex-shrink-0" style={{ color: service.color }} />
                                <span>{detail}</span>
                              </motion.li>
                            ))}
                          </ul>
                        </div>
                      </motion.div>
                    )}
                  </AnimatePresence>
                </CardContent>
              </Card>
            </motion.div>
          ))}
        </div>
      </div>
    </section>
  )
}