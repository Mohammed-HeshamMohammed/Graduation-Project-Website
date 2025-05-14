// components/animations/FadeInView.tsx
"use client";

import { motion } from "framer-motion";

interface FadeInViewProps {
  children: React.ReactNode;
  delay?: number;
}

export function FadeInView({ children, delay = 0 }: FadeInViewProps) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 30 }}
      whileInView={{ opacity: 1, y: 0 }}
      viewport={{ once: true, margin: "-100px" }}
      transition={{ duration: 0.7, delay }}
    >
      {children}
    </motion.div>
  );
}
