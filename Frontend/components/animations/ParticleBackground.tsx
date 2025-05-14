// components/animations/ParticleBackground.tsx
"use client";

import { motion } from "framer-motion";

interface ParticleBackgroundProps {
  count?: number;
  color?: string;
}

export function ParticleBackground({ count = 50, color = "blue" }: ParticleBackgroundProps) {
  return (
    <div className="absolute inset-0 overflow-hidden pointer-events-none">
      {Array.from({ length: count }).map((_, i) => {
        const size = Math.random() * 10 + 5;
        const initialX = Math.random() * 100;
        const initialY = Math.random() * 100;
        
        const colorClass =
          color === "blue"
            ? "bg-blue-400/20"
            : color === "indigo"
            ? "bg-indigo-400/20"
            : "bg-purple-400/20";
        
        return (
          <motion.div
            key={`particle-${i}`}
            className={`absolute rounded-full ${colorClass}`}
            style={{
              width: size,
              height: size,
              left: `${initialX}%`,
              top: `${initialY}%`,
            }}
            animate={{
              x: [0, Math.random() * 50 - 25],
              y: [0, Math.random() * 50 - 25],
              opacity: [0.3, 0.6, 0.3],
              scale: [1, Math.random() * 0.5 + 0.8, 1],
            }}
            transition={{
              duration: Math.random() * 10 + 10,
              repeat: Infinity,
              repeatType: "reverse",
              ease: "easeInOut",
              delay: Math.random() * 5,
            }}
          />
        );
      })}
    </div>
  );
}
