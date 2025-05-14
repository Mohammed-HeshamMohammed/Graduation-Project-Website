"use client";

import { motion, useScroll, useTransform } from "framer-motion";

export function AnimatedBackground() {
  const { scrollYProgress } = useScroll();
  
  // Transform scroll progress to control animation intensity
  const animationIntensity = useTransform(
    scrollYProgress,
    [0, 0.5, 1],
    [1, 1.5, 1]
  );
  
  // Transform scroll progress to control gradient rotation
  const gradientRotation = useTransform(
    scrollYProgress,
    [0, 1],
    [0, 15]
  );
  
  return (
    <div className="fixed inset-0 -z-10 pointer-events-none overflow-hidden">
      {/* Main gradient background */}
      <motion.div
        style={{
          rotate: gradientRotation,
          scale: animationIntensity,
        }}
        className="absolute inset-0 opacity-30"
      >
        <div className="absolute inset-0 bg-gradient-to-br from-blue-50 to-indigo-100" />
      </motion.div>
      
      {/* Animated orbs */}
      {Array.from({ length: 8 }).map((_, i) => {
        const size = Math.random() * 300 + 200;
        const xPos = Math.random() * 100;
        const yPos = Math.random() * 100;
        const delay = i * 0.7;
        
        const colors = [
          "rgba(59, 130, 246, 0.1)",
          "rgba(99, 102, 241, 0.1)",
          "rgba(139, 92, 246, 0.1)",
          "rgba(79, 70, 229, 0.1)"
        ];
        
        const color = colors[i % colors.length];
        
        return (
          <motion.div
            key={`orb-${i}`}
            className="absolute rounded-full"
            style={{
              width: size,
              height: size,
              left: `${xPos}%`,
              top: `${yPos}%`,
              background: `radial-gradient(circle, ${color} 0%, rgba(255,255,255,0) 70%)`,
            }}
            animate={{
              scale: [1, 1.2, 1],
              x: [0, Math.random() * 30 - 15, 0],
              y: [0, Math.random() * 30 - 15, 0],
              opacity: [0.3, 0.6, 0.3],
            }}
            transition={{
              duration: Math.random() * 10 + 20,
              repeat: Infinity,
              repeatType: "reverse",
              ease: "easeInOut",
              delay,
            }}
          />
        );
      })}
      
      {/* Grid pattern overlay */}
      <motion.div
        className="absolute inset-0 opacity-5"
        style={{
          backgroundImage: "url('/images/grid-pattern.svg')",
          backgroundSize: "30px 30px",
          y: useTransform(scrollYProgress, [0, 1], [0, 100]),
          opacity: useTransform(scrollYProgress, [0, 0.5, 1], [0.05, 0.1, 0.05]),
        }}
      />
      
      {/* Floating particles */}
      {Array.from({ length: 25 }).map((_, i) => {
        const size = Math.random() * 5 + 2;
        const xPos = Math.random() * 100;
        const yPos = Math.random() * 100;
        
        return (
          <motion.div
            key={`particle-${i}`}
            className="absolute rounded-full bg-indigo-500/20"
            style={{
              width: size,
              height: size,
              left: `${xPos}%`,
              top: `${yPos}%`,
            }}
            animate={{
              y: [0, -100],
              x: [0, Math.random() * 50 - 25],
              opacity: [0.2, 0],
            }}
            transition={{
              duration: Math.random() * 10 + 10,
              repeat: Infinity,
              repeatType: "loop",
              ease: "easeInOut",
              delay: Math.random() * 5,
            }}
          />
        );
      })}
    </div>
  );
}