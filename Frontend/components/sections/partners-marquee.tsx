"use client";

import { useEffect, useRef } from "react";
import Image from "next/image";

const partners = [
  { name: "Health Partner", logo: "/images/partners/health.png" },
  { name: "Hexagon", logo: "/images/partners/hexagon.png" },
  { name: "Construction", logo: "/images/partners/construction.png" },
  { name: "Overseas Transport", logo: "/images/partners/overseas.png" },
  { name: "Plaininfinity", logo: "/images/partners/plaininfinity.png" }, // Fixed spelling
  { name: "Logistics", logo: "/images/partners/logistics.png" },
];

export function PartnersMarquee() {
  const marqueeRef = useRef<HTMLDivElement>(null);
  const itemsRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const marquee = marqueeRef.current;
    const items = itemsRef.current;
    if (!marquee || !items) return;

    let animationId: ReturnType<typeof setTimeout>; // Fix TypeScript issue
    let currentIndex = 0;
    const totalPartners = partners.length;

    const animate = () => {
      currentIndex = (currentIndex + 1) % totalPartners;

      // Create the new order of partners
      const reorderedPartners = [...partners.slice(currentIndex), ...partners.slice(0, currentIndex)];

      // Update the DOM
      if (items) {
        items.style.transform = `translateX(0)`;
        items.innerHTML = reorderedPartners
          .map(
            (partner) => `
          <div class="flex-shrink-0 w-32 h-16 relative grayscale hover:grayscale-0 transition-all duration-300">
            <img
              src="${partner.logo || "/placeholder.svg?height=64&width=128"}"
              alt="${partner.name}"
              class="object-contain w-full h-full"
            />
          </div>
        `
          )
          .join("");
      }

      animationId = setTimeout(animate, 2000); // Change partner every 2 seconds
    };

    animate();

    return () => {
      clearTimeout(animationId);
    };
  }, []);

  return (
    <section className="py-12 bg-gradient-to-r from-blue-50 to-indigo-50 overflow-hidden">
      <div className="container mx-auto px-4 mb-6">
        <h2 className="text-2xl font-bold text-center text-gray-800">Our Trusted Partners</h2>
      </div>

      <div ref={marqueeRef} className="relative w-full overflow-hidden">
        <div ref={itemsRef} className="flex items-center justify-center gap-12 py-4 transition-transform duration-1000">
          {partners.map((partner, index) => (
            <div
              key={`${partner.name}-${index}`}
              className="flex-shrink-0 w-32 h-16 relative grayscale hover:grayscale-0 transition-all duration-300"
            >
              <Image
                src={partner.logo || "/placeholder.svg?height=64&width=128"}
                alt={partner.name}
                fill
                className="object-contain"
              />
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}
