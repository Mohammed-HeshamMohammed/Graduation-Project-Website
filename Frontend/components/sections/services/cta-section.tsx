"use client"

import { useRef } from "react"
import Link from "next/link"
import { Button } from "@/components/ui/button"
import { AuthModal } from "@/components/auth-modal"
import { motion, useScroll } from "framer-motion"
import Image from "next/image"
import { CheckCircle2, ArrowRight, ArrowDown } from "lucide-react"
import { FloatingElement } from "@/components/animations/FloatingElement"
import { ParticleBackground } from "@/components/animations/ParticleBackground"

export function ServicesCTASection() {
  const ref = useRef(null)
  const { scrollYProgress } = useScroll({ target: ref })

  return (
    <motion.section
      ref={ref}
      initial={{ opacity: 0, y: 50 }}
      whileInView={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.8 }}
      viewport={{ once: true, margin: "-100px" }}
      className="my-20 rounded-3xl overflow-hidden shadow-xl relative"
    >
      <div className="relative bg-gradient-to-r from-indigo-600 to-blue-800">
        {/* Animated Background */}
        <ParticleBackground count={15} color="blue" />
        <motion.div
          className="absolute inset-0 opacity-10"
          animate={{ backgroundPosition: ["0% 0%", "100% 100%"] }}
          transition={{ duration: 30, repeat: Infinity, repeatType: "reverse" }}
        >
          <div
            className="absolute inset-0"
            style={{
              backgroundImage: "url('/images/dots-pattern.svg')",
              backgroundSize: "50px 50px",
            }}
          />
        </motion.div>

        <div className="relative grid md:grid-cols-2 gap-8 lg:gap-16 p-8 md:p-12 lg:p-16 items-center">
          {/* Left Column: CTA Text & Features */}
          <div>
            <motion.div
              initial={{ x: -20, opacity: 0 }}
              whileInView={{ x: 0, opacity: 1 }}
              transition={{ duration: 0.5, delay: 0.2 }}
              viewport={{ once: true }}
              className="flex flex-col gap-6"
            >
              <motion.h2
                className="text-3xl md:text-4xl font-bold text-white"
                initial={{ x: -20, opacity: 0 }}
                whileInView={{ x: 0, opacity: 1 }}
                viewport={{ once: true }}
                transition={{ duration: 0.6 }}
              >
                <FloatingElement duration={5}>
                  Ready to Optimize Your Fleet Operations?
                </FloatingElement>
              </motion.h2>
              <motion.p
                className="text-blue-100 text-lg md:text-xl"
                initial={{ y: 20, opacity: 0 }}
                whileInView={{ y: 0, opacity: 1 }}
                transition={{ duration: 0.4, delay: 0.1, ease: "easeOut" }}
                viewport={{ once: true }}
              >
                Join thousands of businesses that have transformed their fleet management with our comprehensive solutions.
              </motion.p>
              <div className="space-y-3 mt-2">
                {[
                  "Reduce operational costs by up to 25%",
                  "Improve driver safety and compliance",
                  "Minimize vehicle downtime",
                  "Real-time insights and reporting",
                ].map((item, index) => (
                  <motion.div
                    key={index}
                    initial={{ x: -20, opacity: 0 }}
                    whileInView={{ x: 0, opacity: 1 }}
                    transition={{ delay: 0.4 + index * 0.1, duration: 0.5 }}
                    viewport={{ once: true }}
                    className="flex items-center gap-3"
                  >
                    <motion.div
                      whileHover={{ scale: 1.2, rotate: 5 }}
                      className="flex-shrink-0"
                    >
                      <CheckCircle2 className="h-5 w-5 text-green-400" />
                    </motion.div>
                    <span className="text-white">{item}</span>
                  </motion.div>
                ))}
              </div>
              <div className="mt-4 flex flex-col sm:flex-row gap-4">
                <motion.div
                  initial={{ y: 20, opacity: 0 }}
                  whileInView={{ y: 0, opacity: 1 }}
                  transition={{ duration: 0.5, delay: 0.8 }}
                  viewport={{ once: true }}
                  whileHover={{ scale: 1.05, y: -5 }}
                  whileTap={{ scale: 0.95 }}
                >
                  <Button size="lg" className="bg-white text-indigo-700 hover:bg-blue-50 hover:shadow-lg">
                    <span className="flex items-center gap-2">
                      Get Started Now
                      <motion.div
                        animate={{ x: [0, 5, 0] }}
                        transition={{ duration: 1.5, repeat: Infinity }}
                      >
                        <ArrowRight className="h-4 w-4" />
                      </motion.div>
                    </span>
                  </Button>
                </motion.div>
                <motion.div
                  initial={{ y: 20, opacity: 0 }}
                  whileInView={{ y: 0, opacity: 1 }}
                  transition={{ duration: 0.5, delay: 0.9 }}
                  viewport={{ once: true }}
                  whileHover={{ scale: 1.05, y: -5 }}
                  whileTap={{ scale: 0.95 }}
                >
                  <Button size="lg" variant="outline" className="text-white border-white hover:bg-white/10">
                    Schedule a Consultation
                  </Button>
                </motion.div>
              </div>
            </motion.div>
          </div>

          {/* Right Column: Image & Decorative Element */}
          <motion.div
            initial={{ scale: 0.9, opacity: 0 }}
            whileInView={{ scale: 1, opacity: 1 }}
            transition={{ duration: 0.7, delay: 0.3 }}
            viewport={{ once: true }}
            className="relative hidden md:block h-[400px] rounded-xl overflow-hidden"
          >
            <motion.div
              whileHover={{ scale: 1.05 }}
              transition={{ duration: 0.5 }}
              className="h-full"
            >
              <Image
                src="/images/fleet-dashboard.jpg"
                alt="Fleet Management Dashboard"
                fill
                className="object-cover"
              />
              <motion.div
                className="absolute inset-0 bg-gradient-to-tl from-indigo-900/50 to-transparent"
                animate={{ opacity: [0.5, 0.7, 0.5] }}
                transition={{ duration: 3, repeat: Infinity }}
              />
            </motion.div>
            <motion.div
              className="absolute top-4 right-4 bg-white/80 backdrop-blur-sm p-2 rounded-lg shadow-lg"
              initial={{ y: -20, opacity: 0 }}
              whileInView={{ y: 0, opacity: 1 }}
              transition={{ delay: 0.6, duration: 0.5 }}
              viewport={{ once: true }}
            >
              <FloatingElement duration={3}>
                <div className="flex items-center gap-2">
                  <div className="w-3 h-3 rounded-full bg-green-500"></div>
                  <span className="text-sm font-medium text-gray-900">Live Data</span>
                </div>
              </FloatingElement>
            </motion.div>
          </motion.div>
        </div>
      </div>
    </motion.section>
  )
}