// components/ServiceCTA.tsx
"use client";

import { motion } from "framer-motion";
import { Button } from "@/components/ui/button";
import Link from "next/link";
import { AuthModal } from "@/components/auth-modal";

export function ServiceCTA() {
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      whileInView={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.7, ease: "easeOut" }}
      viewport={{ once: true, margin: "-80px" }}
      className="py-12 px-4 sm:py-16 rounded-2xl shadow-md bg-gradient-to-r from-blue-600 to-indigo-600 text-white text-center relative overflow-hidden"
    >
      {/* Animated Background Bubbles */}
      <div className="absolute inset-0 overflow-hidden pointer-events-none">
        {Array.from({ length: 20 }).map((_, i: number) => (
          <motion.div
            key={i}
            className="absolute rounded-full bg-white opacity-10"
            style={{
              width: `${Math.random() * 40 + 20}px`,
              height: `${Math.random() * 40 + 20}px`,
              left: `${Math.random() * 100}%`,
              top: `${Math.random() * 100}%`,
            }}
            animate={{
              y: [0, -Math.random() * 100 - 30],
              x: [0, Math.random() * 20 - 10],
              opacity: [0.1, 0],
              scale: [1, Math.random() * 0.3 + 0.5],
            }}
            transition={{
              duration: Math.random() * 6 + 4,
              repeat: Infinity,
              repeatType: "loop",
              ease: "easeInOut",
              delay: Math.random() * 3,
            }}
          />
        ))}
      </div>

      <div className="max-w-3xl mx-auto relative z-10">
        <motion.h2
          initial={{ y: 15, opacity: 0 }}
          whileInView={{ y: 0, opacity: 1 }}
          transition={{ duration: 0.65, delay: 0.1, ease: "easeOut" }}
          viewport={{ once: true }}
          className="text-2xl sm:text-3xl font-bold mb-3"
        >
          Ready to transform your fleet operations?
        </motion.h2>

        <motion.p
          initial={{ y: 15, opacity: 0 }}
          whileInView={{ y: 0, opacity: 1 }}
          transition={{ duration: 0.65, delay: 0.2, ease: "easeOut" }}
          viewport={{ once: true }}
          className="text-base sm:text-lg text-blue-100 mb-6"
        >
          Join thousands of companies that trust our platform for their fleet management needs.
        </motion.p>

        <motion.div
          initial={{ y: 15, opacity: 0 }}
          whileInView={{ y: 0, opacity: 1 }}
          transition={{ duration: 0.65, delay: 0.3, ease: "easeOut" }}
          viewport={{ once: true }}
          className="flex flex-col sm:flex-row gap-4 justify-center"
        >
          <motion.div whileHover={{ scale: 1.05 }} whileTap={{ scale: 0.97 }} transition={{ duration: 0.25, ease: "easeOut" }}>
            <AuthModal
              triggerText="Sign Up Now"
              defaultTab="register"
              className="bg-white text-blue-600 hover:bg-blue-50 font-semibold shadow-md rounded-md text-xs sm:text-sm"
            />
          </motion.div>

          <motion.div whileHover={{ scale: 1.05 }} whileTap={{ scale: 0.97 }} transition={{ duration: 0.25, ease: "easeOut" }}>
            <Link href="/contact">
              <Button variant="outline" className="border-white text-white hover:bg-white/10 rounded-md text-xs sm:text-sm">
                Contact Sales
              </Button>
            </Link>
          </motion.div>
        </motion.div>
      </div>
    </motion.div>
  );
}
