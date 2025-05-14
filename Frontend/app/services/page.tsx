"use client"

import { ErrorBoundary } from "@/components/errors/ErrorBoundary"
import { ServiceDetails } from "@/components/sections/services/service-details"
import { ServicesOverview } from "@/components/sections/services/services-overview"
import { ServicesHeroSection } from "@/components/sections/services/hero-section"
import { ServicesCTASection } from "@/components/sections/services/cta-section"
import { motion, useScroll, useTransform } from "framer-motion"

// Import animation components with dynamic imports to prevent build failures
import dynamic from 'next/dynamic'

// Define fallback components
const FallbackBackground = () => <div className="fixed inset-0 -z-10 bg-gradient-to-br from-blue-50 to-indigo-50"></div>
const FallbackLayer = ({ children }: { children: React.ReactNode }) => <div>{children}</div>

// Dynamically import animation components with fallbacks
const AnimatedBackground = dynamic(
  () => import('@/components/animations/AnimatedBackground').then(mod => mod.AnimatedBackground),
  { ssr: false, loading: () => <FallbackBackground /> }
)

const ParallaxLayer = dynamic(
  () => import('@/components/animations/ParallaxLayer').then(mod => mod.ParallaxLayer),
  { ssr: false, loading: () => <FallbackLayer children={null} /> }
)

// Fallback animation variants
const defaultContainerVariants = {
  hidden: { opacity: 0 },
  visible: { opacity: 1, transition: { duration: 0.5 } }
}

const defaultItemVariants = {
  hidden: { opacity: 0 },
  visible: { opacity: 1, transition: { duration: 0.3 } }
}

// Import animation variants or use defaults
let containerVariants = defaultContainerVariants
let itemVariants = defaultItemVariants

try {
  const variants = require('@/components/animations/variants')
  containerVariants = variants.containerVariants || defaultContainerVariants
  itemVariants = variants.itemVariants || defaultItemVariants
} catch (error) {
  console.warn('Animation variants not found, using defaults')
}

function ServicesPageContent() {
  const { scrollYProgress } = useScroll()

  const backgroundColor = useTransform(
    scrollYProgress,
    [0, 0.3, 0.6, 1],
    [
      "linear-gradient(to bottom right, rgb(249, 250, 251), rgb(239, 246, 255))",
      "linear-gradient(to bottom right, rgb(243, 244, 246), rgb(238, 242, 255))",
      "linear-gradient(to bottom right, rgb(249, 250, 251), rgb(224, 231, 255))",
      "linear-gradient(to bottom right, rgb(243, 244, 246), rgb(219, 234, 254))"
    ]
  )

  return (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      transition={{ duration: 0.8 }}
      style={{ background: backgroundColor }}
      className="min-h-screen relative"
    >
      {/* Using the dynamically imported component */}
      <AnimatedBackground />

      {/* Hero Section */}
      <ServicesHeroSection />

      <div className="container mx-auto px-4 -mt-20 relative z-20">
        <motion.div
          initial={{ y: 100, opacity: 0 }}
          animate={{ y: 0, opacity: 1 }}
          transition={{ delay: 0.5, duration: 0.8 }}
          className="bg-white shadow-xl rounded-3xl p-8 md:p-12 mb-16"
        >
          <motion.div
            variants={containerVariants}
            initial="hidden"
            whileInView="visible"
            viewport={{ once: true, margin: "-100px" }}
            className="mb-16"
          >
            <motion.div variants={itemVariants} className="text-center mb-12">
              <motion.span
                whileHover={{ y: -3 }}
                transition={{ type: "spring", stiffness: 300 }}
                className="px-4 py-1 bg-indigo-100 text-indigo-800 rounded-full text-sm font-medium inline-block mb-3"
              >
                Our Services
              </motion.span>
              <ServicesOverview />
            </motion.div>
          </motion.div>

          <ServiceDetails />
        </motion.div>

        <ServicesCTASection />
      </div>

      <div className="h-20"></div>
    </motion.div>
  )
}

export default function ServicesPage() {
  return (
    <ErrorBoundary>
      <ServicesPageContent />
    </ErrorBoundary>
  )
}