"use client"

import { useState, useEffect, ReactNode } from "react"
import { motion, AnimatePresence } from "framer-motion"
import { AboutHeroSection } from "@/components/sections/about/about-hero-section"
import { MissionSection } from "@/components/sections/about/mission-section"
import { FeaturesSection } from "@/components/sections/about/features-section"
import { TeamSection } from "@/components/sections/about/team-section"

// Animated background elements
const BackgroundElements = () => {
  // Use useState and useEffect to ensure client-side only rendering for random elements
  const [elements, setElements] = useState<Array<{
    size: number;
    xPos: number;
    yPos: number;
    duration: number;
    delay: number;
    isEven: boolean;
  }>>([]);

  useEffect(() => {
    // Generate random properties only on the client side
    const generatedElements = [...Array(8)].map((_, i) => ({
      size: Math.floor(Math.random() * 300) + 100,
      xPos: Math.floor(Math.random() * 100),
      yPos: Math.floor(Math.random() * 100),
      duration: Math.floor(Math.random() * 30) + 20,
      delay: Math.floor(Math.random() * 5),
      isEven: i % 2 === 0
    }));
    
    setElements(generatedElements);
  }, []);

  return (
    <>
      {/* Floating orbs - only rendered client-side */}
      {elements.map((elem, i) => (
        <motion.div
          key={i}
          className="absolute rounded-full opacity-20 blur-3xl"
          style={{
            width: elem.size,
            height: elem.size,
            background: elem.isEven 
              ? "linear-gradient(120deg, #a1c4fd 0%, #c2e9fb 100%)" 
              : "linear-gradient(120deg, #8989ba 0%, #a7a6cb 100%)",
            left: `${elem.xPos}%`,
            top: `${elem.yPos}%`,
            zIndex: 0
          }}
          initial={{ scale: 0.8, opacity: 0 }}
          animate={{ 
            scale: [0.8, 1.2, 0.9, 1.1, 1],
            opacity: [0, 0.2, 0.15, 0.2],
            x: [0, 50, -30, 20, 0],
            y: [0, -40, 20, -20, 0],
          }}
          transition={{
            duration: elem.duration,
            delay: elem.delay,
            repeat: Infinity,
            repeatType: "reverse",
            ease: "easeInOut"
          }}
        />
      ))}

      {/* Grid pattern overlay */}
      <div className="absolute inset-0 bg-grid-pattern opacity-[0.03] pointer-events-none" />
    </>
  )
}

// Scroll indicator animation
const ScrollIndicator = () => {
  const [scrollProgress, setScrollProgress] = useState(0)

  useEffect(() => {
    const handleScroll = () => {
      const totalHeight = document.documentElement.scrollHeight - window.innerHeight
      const progress = (window.scrollY / totalHeight) * 100
      setScrollProgress(progress)
    }

    window.addEventListener("scroll", handleScroll)
    return () => window.removeEventListener("scroll", handleScroll)
  }, [])

  return (
    <div className="fixed top-0 left-0 w-full h-1 z-50">
      <motion.div 
        className="h-full bg-gradient-to-r from-blue-500 to-indigo-600"
        style={{ width: `${scrollProgress}%` }}
      />
    </div>
  )
}

// Section wrapper with animations
interface AnimatedSectionProps {
  children: ReactNode;
  delay?: number;
}

const AnimatedSection = ({ children, delay = 0 }: AnimatedSectionProps) => {
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      whileInView={{ opacity: 1, y: 0 }}
      viewport={{ once: true, margin: "-50px" }}
      transition={{ duration: 0.6, ease: "easeOut", delay }}
    >
      {children}
    </motion.div>
  )
}

export default function AboutPage() {
  // State for client-side only components
  const [isClient, setIsClient] = useState(false)

  useEffect(() => {
    // Mark that we're on the client
    setIsClient(true)
  }, [])

  return (
    <div className="min-h-screen bg-gradient-to-b from-white via-blue-50 to-indigo-50 relative overflow-hidden">
      {/* Animated background elements - only render on client */}
      {isClient && <BackgroundElements />}
      
      {/* Scroll progress indicator - only render on client */}
      {isClient && <ScrollIndicator />}
      
      {/* Main content */}
      <div className="pt-16 md:pt-24 pb-16 relative z-10">
        <div className="container mx-auto px-4 sm:px-6">
          <AnimatedSection>
            <AboutHeroSection />
          </AnimatedSection>
          
          <AnimatedSection delay={0.15}>
            <div className="mt-12 md:mt-16">
              <MissionSection />
            </div>
          </AnimatedSection>
          
          <AnimatedSection delay={0.3}>
            <div className="mt-12 md:mt-16">
              <FeaturesSection />
            </div>
          </AnimatedSection>
          
          <AnimatedSection delay={0.45}>
            <div className="mt-12 md:mt-16 mb-12 md:mb-16">
              <TeamSection />
            </div>
          </AnimatedSection>
        </div>
      </div>
    </div>
  )
}