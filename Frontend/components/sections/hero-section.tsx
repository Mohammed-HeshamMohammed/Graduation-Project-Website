import Image from "next/image"
import { Button } from "@/components/ui/button"

export function HeroSection() {
  return (
    <section className="relative h-screen flex items-center justify-center text-white overflow-hidden">
      {/* Ensure parent has relative positioning and height */}
      <div className="absolute inset-0 w-full h-full">
        <Image 
          src="/images/hero-truck.jpg" 
          alt="A truck representing fleet management solutions" 
          layout="fill" 
          objectFit="cover" 
          priority 
        />
      </div>
      {/* Gradient Overlay */}
      <div className="absolute inset-0 bg-gradient-to-r from-blue-900 to-indigo-900 opacity-30" />
      {/* Content */}
      <div className="relative z-10 container mx-auto px-4 text-center max-w-4xl">
        <h1 className="text-5xl md:text-7xl font-bold mb-6">FLEET MANAGEMENT SOLUTIONS</h1>
        <p className="text-xl md:text-2xl mb-8">Comprehensive Vehicle Fleet Management</p>
        <Button
          size="lg"
          className="bg-gradient-to-r from-yellow-500 to-yellow-400 hover:from-yellow-600 hover:to-yellow-500 text-black"
          aria-label="View fleet management details"
        >
          VIEW DETAILS
        </Button>
      </div>
    </section>
  )
}
