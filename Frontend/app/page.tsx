"use client"

import { HeroSection } from "@/components/sections/hero-section"
import { ServicesSection } from "@/components/sections/services-section"
import { OfferingsSection } from "@/components/sections/offerings-section"
import { IndustriesSection } from "@/components/sections/industries-section"
import { NewsletterSection } from "@/components/sections/newsletter-section"
import { motion } from "framer-motion"

// import { PartnersMarquee } from "@/components/sections/partners-marquee"

export default function Home() {
  // Background animation elements
  const bubbles = Array.from({ length: 6 }, (_, i) => ({
    id: i,
    size: Math.floor(Math.random() * 200) + 100,
    x: Math.floor(Math.random() * 100),
    y: Math.floor(Math.random() * 100),
    duration: Math.floor(Math.random() * 20) + 15
  }))

  return (
    <div className="bg-white relative overflow-hidden">
      {/* Animated background elements */}
      {bubbles.map((bubble) => (
        <motion.div
          key={bubble.id}
          className="absolute rounded-full bg-gradient-to-r from-blue-50 to-indigo-50 opacity-30 blur-3xl"
          style={{
            width: bubble.size,
            height: bubble.size,
            left: `${bubble.x}%`,
            top: `${bubble.y}%`,
            zIndex: 0
          }}
          animate={{
            x: [0, 50, -30, 20, 0],
            y: [0, -40, 20, -20, 0],
          }}
          transition={{
            duration: bubble.duration,
            repeat: Infinity,
            repeatType: "reverse",
            ease: "easeInOut"
          }}
        />
      ))}
      
      {/* Content */}
      <div className="relative z-10">
        <HeroSection />
        <ServicesSection />
        <OfferingsSection />
        <IndustriesSection />
        {/* <PartnersMarquee /> */}
        <NewsletterSection />
      </div>
    </div>
  )
}
