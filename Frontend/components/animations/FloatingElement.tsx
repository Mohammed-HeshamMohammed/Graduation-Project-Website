// components/animations/FloatingElement.tsx
"use client";

import { motion } from "framer-motion";

interface FloatingElementProps {
  children: React.ReactNode;
  duration?: number;
  delay?: number;
}

export function FloatingElement({ children, duration = 4, delay = 0 }: FloatingElementProps) {
  return (
    <motion.div
      animate={{ 
        y: [0, -15, 0],
        rotate: [-1, 1, -1],
      }}
      transition={{ 
        repeat: Infinity, 
        repeatType: "reverse", 
        duration, 
        delay,
        ease: "easeInOut",
      }}
    >
      {children}
    </motion.div>
  );
}
