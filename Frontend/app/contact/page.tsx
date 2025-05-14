"use client"

import { motion } from "framer-motion"
import { ContactHeroSection } from "@/components/sections/contact/hero-section"
import { ContactInfo } from "@/components/sections/contact/contact-info"
import { ContactMap } from "@/components/sections/contact/contact-map"
import { ContactForm } from "@/components/sections/contact/contact-form"
import { ArrowUp } from "lucide-react"
import { useEffect, useState } from "react"

export default function ContactPage() {
  return (
    <>
      {/* Background decorations - reduced size on mobile */}
      <div className="fixed inset-0 -z-10 overflow-hidden">
        <div className="absolute top-10 left-5 w-40 h-40 md:w-96 md:h-96 rounded-full bg-blue-50 blur-3xl opacity-60" />
        <div className="absolute bottom-10 right-5 w-40 h-40 md:w-96 md:h-96 rounded-full bg-indigo-50 blur-3xl opacity-60" />
        <div className="absolute top-1/3 right-1/4 w-32 h-32 md:w-64 md:h-64 rounded-full bg-purple-50 blur-3xl opacity-50" />
      </div>
      
      <motion.div 
        className="container mx-auto px-4 py-4 md:py-16 min-h-screen"
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ duration: 0.5 }}
      >
        {/* Page Content - Adjusted margins for mobile */}
        <div className="mt-4 md:mt-16 mb-8 md:mb-24 max-w-7xl mx-auto">
          <div className="bg-white rounded-xl shadow-lg p-4 md:p-8 border border-gray-100">
            <div className="grid gap-6 md:gap-8 lg:grid-cols-2 lg:gap-16 items-start">
              <div className="space-y-4 md:space-y-8">
                <ContactHeroSection />
                <ContactInfo />
                <ContactMap />
              </div>
              <div className="lg:sticky lg:top-28">
                <ContactForm />
              </div>
            </div>
            
            {/* Section divider */}
            <div className="my-6 md:my-16 flex items-center justify-center">
              <div className="h-px bg-gradient-to-r from-transparent via-gray-300 to-transparent w-full"></div>
            </div>
            
            {/* FAQ section - simplified animation for mobile */}
            <motion.div 
              className="mb-4 md:mb-8"
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.3, duration: 0.4 }}
            >
              <h2 className="text-xl md:text-2xl font-bold text-center text-gray-800 mb-4 md:mb-8">Frequently Asked Questions</h2>
              <div className="grid gap-4 sm:grid-cols-1 md:grid-cols-2 lg:grid-cols-3">
                {[
                  {
                    q: "How quickly can I expect a response?",
                    a: "We typically respond to all inquiries within 24 hours during business days."
                  },
                  {
                    q: "Do you offer 24/7 support?",
                    a: "Yes, our emergency technical support is available 24/7 for critical issues."
                  },
                  {
                    q: "Can I request a product demo?",
                    a: "Absolutely! You can request a demo through our contact form or by calling us directly."
                  },
                ].map((faq, i) => (
                  <motion.div 
                    key={i}
                    className="bg-white p-4 md:p-6 rounded-lg shadow-sm border border-gray-100"
                    whileHover={{ y: -3, transition: { duration: 0.2 } }}
                    whileTap={{ y: 0, transition: { duration: 0.2 } }}
                  >
                    <h3 className="font-semibold text-base md:text-lg mb-2 text-gray-800">{faq.q}</h3>
                    <p className="text-sm md:text-base text-gray-600">{faq.a}</p>
                  </motion.div>
                ))}
              </div>
            </motion.div>
          </div>
        </div>
      </motion.div>

      {/* Contact CTA Banner - Above Footer */}
      <motion.div 
        className="bg-gradient-to-r from-blue-600 to-indigo-700 py-6 md:py-12 px-4 mt-6 md:mt-16"
        initial={{ opacity: 0, y: 10 }}
        whileInView={{ opacity: 1, y: 0 }}
        viewport={{ once: true, margin: "-50px" }}
        transition={{ duration: 0.4 }}
      >
        <div className="max-w-4xl mx-auto text-center">
          <h2 className="text-xl md:text-3xl font-bold text-white mb-2 md:mb-4">Ready to optimize your fleet?</h2>
          <p className="text-blue-100 mb-4 md:mb-6 max-w-2xl mx-auto text-sm md:text-base">
            Our team is ready to help you find the perfect solution for your business needs.
          </p>
          <motion.button 
            className="px-5 py-2 md:px-6 md:py-3 bg-white text-blue-700 font-medium rounded-lg hover:bg-blue-50 transition-colors text-sm md:text-base"
            whileHover={{ scale: 1.03 }}
            whileTap={{ scale: 0.98 }}
          >
            Get Started Today
          </motion.button>
        </div>
      </motion.div>
    </>
  )
}