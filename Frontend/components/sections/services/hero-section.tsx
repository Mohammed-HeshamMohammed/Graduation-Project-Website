"use client"

import { motion, useScroll, useTransform, useSpring } from "framer-motion"
import { Sparkles, Star, ArrowDown } from "lucide-react"
import { Button } from "@/components/ui/button"
import { useRef, useEffect } from "react"

// Import animations from the animations folder
import { ParticleBackground } from "@/components/animations/ParticleBackground"

export function ServicesHeroSection() {
  const ref = useRef<HTMLDivElement>(null)
  const { scrollYProgress } = useScroll({
    target: ref,
    offset: ["start start", "end start"],
  })

  const opacity = useTransform(scrollYProgress, [0, 0.5], [1, 0])
  const scale = useTransform(scrollYProgress, [0, 0.5], [1, 0.95])
  const y = useTransform(scrollYProgress, [0, 0.5], [0, 50])
  const titleSpring = useSpring(0, { stiffness: 100, damping: 25 })

  useEffect(() => {
    titleSpring.set(1)
  }, [titleSpring])

  return (
    <div
      ref={ref}
      className="relative bg-gradient-to-br from-blue-900 via-indigo-900 to-purple-900 text-white overflow-hidden h-screen flex items-center"
    >
      <ParticleBackground count={30} color="indigo" />

      <div className="absolute inset-0 opacity-10">
        <motion.div
          className="absolute inset-0"
          style={{
            backgroundImage: "url('/images/grid-pattern.svg')",
            backgroundSize: "30px 30px",
            y: useTransform(scrollYProgress, [0, 1], [0, 150]),
          }}
        />
      </div>

      <motion.div
        style={{ opacity, scale, y }}
        className="container mx-auto px-4 py-20 lg:py-28 relative z-10"
      >
        <motion.div className="max-w-3xl mx-auto text-center">
          <motion.div
            initial={{ scale: 0.8, opacity: 0 }}
            animate={{ scale: 1, opacity: 1 }}
            transition={{ delay: 0.2, duration: 0.7, type: "spring" }}
            className="mb-6 inline-block px-4 py-1 bg-white/10 backdrop-blur-sm rounded-full text-sm font-medium flex items-center gap-2"
          >
            <motion.span
              animate={{ rotate: [0, 360] }}
              transition={{ duration: 15, repeat: Infinity, ease: "linear" }}
            >
              <Sparkles className="h-4 w-4 text-yellow-300" />
            </motion.span>
            Fleet Management Solutions
          </motion.div>

          <motion.h1
            style={{ scale: titleSpring }}
            className="text-4xl md:text-5xl lg:text-6xl font-bold mb-6 leading-tight"
          >
            <motion.span
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.4, duration: 0.7 }}
              className="block bg-gradient-to-r from-blue-100 to-indigo-100 bg-clip-text text-transparent"
            >
              Transform Your Fleet
            </motion.span>
            <motion.span
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.6, duration: 0.7 }}
              className="block relative"
            >
              Operations
              <motion.div
                className="absolute -right-8 top-0 md:top-4"
                animate={{ rotate: [0, 15, 0, -15, 0], y: [0, -5, 0, -5, 0] }}
                transition={{ duration: 5, repeat: Infinity }}
              >
                <Star className="h-6 w-6 md:h-8 md:w-8 text-yellow-400 fill-yellow-400" />
              </motion.div>
            </motion.span>
          </motion.h1>

          <motion.p
            initial={{ y: 30, opacity: 0 }}
            animate={{ y: 0, opacity: 1 }}
            transition={{ delay: 0.8, duration: 0.7 }}
            className="text-lg md:text-xl text-blue-100 mb-10"
          >
            Streamline management, increase efficiency, and reduce operational costs with our comprehensive suite of fleet management services.
          </motion.p>

          <motion.div
            initial={{ y: 30, opacity: 0 }}
            animate={{ y: 0, opacity: 1 }}
            transition={{ delay: 1, duration: 0.7 }}
            className="flex flex-col sm:flex-row items-center justify-center gap-4"
          >
            <motion.div whileHover={{ scale: 1.05 }} whileTap={{ scale: 0.95 }}>
              <Button size="lg" className="bg-white text-indigo-900 hover:bg-blue-50 hover:shadow-lg transition-all duration-300">
                Get Started
              </Button>
            </motion.div>
            <motion.div whileHover={{ scale: 1.05 }} whileTap={{ scale: 0.95 }}>
              <Button size="lg" variant="outline" className="border-white text-white hover:bg-white/10 transition-all duration-300">
                Book a Demo
              </Button>
            </motion.div>
          </motion.div>
        </motion.div>
      </motion.div>

      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ delay: 1.5, duration: 1 }}
        style={{ opacity: useTransform(scrollYProgress, [0, 0.2], [1, 0]) }}
        className="absolute bottom-8 left-1/2 transform -translate-x-1/2 text-white"
      >
        <motion.div animate={{ y: [0, 10, 0] }} transition={{ duration: 2, repeat: Infinity }} className="flex flex-col items-center gap-1">
          <span className="text-sm font-medium">Scroll to explore</span>
          <ArrowDown className="h-6 w-6" />
        </motion.div>
      </motion.div>
    </div>
  )
}
