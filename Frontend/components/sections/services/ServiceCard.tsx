"use client";

import React, { useState, useEffect, useCallback, useMemo } from "react";
import Image from "next/image";
import Link from "next/link";
import { Button } from "@/components/ui/button";
import { motion, AnimatePresence } from "framer-motion";
import { CheckCircle2, ChevronDown, Sparkles, Star, ArrowRight } from "lucide-react";
import { AuthModal } from "@/components/auth-modal";

// Define allowed color keys with better naming
type ThemeColor = "blue" | "green" | "yellow" | "purple" | "red";

export interface Service {
  id: string;
  title: string;
  description: string;
  icon: React.ElementType;
  image: string;
  features: string[];
  color: string;
  iconColor: string;
  gradient: string;
  featureColor: string;
  highlightColor: string;
}

interface ServiceCardProps {
  service: Service;
  index: number;
  activeService: string | null;
  setActiveService: (id: string | null) => void;
  hoveredService: string | null;
  setHoveredService: (id: string | null) => void;
  highlightedFeature: { serviceId: string; featureIndex: number } | null;
  setHighlightedFeature: (arg: { serviceId: string; featureIndex: number } | null) => void;
  sectionInView: boolean;
  layoutVariant?: "default" | "alternating";
}

// Animation variants with improved performance
const featureVariants = {
  initial: { opacity: 0, x: -5 },
  animate: (i: number) => ({
    opacity: 1,
    x: 0,
    transition: {
      duration: 0.25,
      delay: i * 0.03, // Reduced delay for faster appearance
      ease: "easeOut",
    },
  }),
  hover: {
    scale: 1.01,
    backgroundColor: "rgba(59, 130, 246, 0.1)",
    transition: { duration: 0.15, ease: "easeOut" },
  },
};

const imageVariants = {
  hover: {
    scale: 1.02,
    filter: "brightness(1.05)",
    transition: { duration: 0.3, ease: "easeOut" },
  },
  initial: {
    scale: 1,
    filter: "brightness(1)",
    transition: { duration: 0.3, ease: "easeOut" },
  },
  mobile: {
    scale: 1.01,
    filter: "brightness(1.02)",
    transition: { duration: 0.2, ease: "easeOut" },
  }
};

/**
 * FloatingParticles Component with performance optimizations
 */
const FloatingParticles = React.memo(({
  color = "blue",
  isParticleAnimationActive = true,
}: {
  color?: ThemeColor;
  isParticleAnimationActive?: boolean;
}) => {
  // Define color classes mapping
  const colorClasses: Record<ThemeColor, string> = {
    blue: "bg-blue-400",
    green: "bg-green-400",
    yellow: "bg-yellow-400",
    purple: "bg-purple-400",
    red: "bg-red-400",
  };

  // Calculate particles based on screen width
  const [particles, setParticles] = useState<React.ReactNode[]>([]);
  
  useEffect(() => {
    const handleResize = () => {
      // Adjust count based on screen width
      const count = window.innerWidth < 640 ? 3 : window.innerWidth < 1024 ? 6 : 8;
      
      // Generate particles only when needed
      const newParticles = Array.from({ length: count }).map((_, i) => {
        const size = Math.random() * 2 + 1.5;
        const initialX = Math.random() * 100;
        const initialY = Math.random() * 100;
        const xMovement = Math.random() * 4 - 2;
        const yMovement = Math.random() * 4 - 2;
        const duration = Math.random() * 3 + 4;

        return (
          <motion.div
            key={i}
            className={`absolute rounded-full ${colorClasses[color]} opacity-20`}
            initial={{ x: `${initialX}%`, y: `${initialY}%`, scale: 0.5, opacity: 0 }}
            animate={{
              x: isParticleAnimationActive ? [`${initialX}%`, `${initialX + xMovement}%`] : `${initialX}%`,
              y: isParticleAnimationActive ? [`${initialY}%`, `${initialY + yMovement}%`] : `${initialY}%`,
              scale: isParticleAnimationActive ? [0.5, 0.7, 0.5] : 0.5,
              opacity: isParticleAnimationActive ? [0, 0.3, 0] : 0,
            }}
            transition={{
              duration,
              repeat: Infinity,
              repeatType: "mirror",
              ease: "easeInOut",
            }}
            style={{ width: size, height: size }}
          />
        );
      });
      
      setParticles(newParticles);
    };
    
    handleResize();
    window.addEventListener("resize", handleResize);
    return () => window.removeEventListener("resize", handleResize);
  }, [color, isParticleAnimationActive]);

  return <>{particles}</>;
});

FloatingParticles.displayName = "FloatingParticles";

/**
 * Optimized ServiceCard Component with increased sizes
 */
export function ServiceCard({
  service,
  index,
  activeService,
  setActiveService,
  hoveredService,
  setHoveredService,
  highlightedFeature,
  setHighlightedFeature,
  sectionInView,
  layoutVariant = "alternating",
}: ServiceCardProps) {
  const [isMobile, setIsMobile] = useState(false);
  const [isLowPerfDevice, setIsLowPerfDevice] = useState(false);
  const [hasMounted, setHasMounted] = useState(false);

  useEffect(() => {
    let timeoutId: NodeJS.Timeout;
    
    const checkDevice = () => {
      clearTimeout(timeoutId);
      timeoutId = setTimeout(() => {
        const isMobileView = window.innerWidth < 640;
        setIsMobile(isMobileView);
        const isLowPerf = 
          // Use a safer check that won't cause build errors
          (isMobileView && (navigator.userAgent.includes("Android") || /iPhone OS [78]_/.test(navigator.userAgent)));
        setIsLowPerfDevice(isLowPerf);
      }, 100);
    };
    
    checkDevice();
    setHasMounted(true);
    window.addEventListener("resize", checkDevice);
    return () => {
      clearTimeout(timeoutId);
      window.removeEventListener("resize", checkDevice);
    };
  }, []);

  const toggleService = useCallback((id: string) => {
    setActiveService(activeService === id ? null : id);
  }, [activeService, setActiveService]);

  const themeColor = useMemo((): ThemeColor => {
    const colors: ThemeColor[] = ["blue", "green", "yellow", "purple", "red"];
    return colors[index % colors.length];
  }, [index]);

  const imageAnimationState = useMemo(() => {
    if (isMobile) return "mobile";
    return (sectionInView || hoveredService === service.id) ? "hover" : "initial";
  }, [isMobile, sectionInView, hoveredService, service.id]);
  
  // Updated background gradient for a richer color
  const bgGradient = useMemo(() => {
    return index % 2 === 0
      ? "bg-gradient-to-r from-blue-100 to-indigo-100 border-blue-200/60"
      : "bg-gradient-to-r from-indigo-100 to-purple-100 border-indigo-200/60";
  }, [index]);

  const isImageOnRight = useMemo(() => {
    if (layoutVariant === "default") return false;
    return index % 2 !== 0;
  }, [layoutVariant, index]);

  const reducedMotionProps = useMemo(() => {
    if (isLowPerfDevice) {
      return {
        transition: { duration: 0.15 },
        animate: { opacity: 1, y: 0 },
      };
    }
    return {};
  }, [isLowPerfDevice]);

  const renderFeatures = useMemo(() => {
    return service.features.map((feature, i) => (
      <motion.div
        key={i}
        custom={i}
        variants={featureVariants}
        initial="initial"
        animate="animate"
        whileHover={!isLowPerfDevice ? "hover" : undefined}
        className={`flex items-start p-2 rounded transition-colors duration-150 ${
          highlightedFeature?.serviceId === service.id &&
          highlightedFeature?.featureIndex === i
            ? service.highlightColor
            : ""
        }`}
        onMouseEnter={() => !isMobile && setHighlightedFeature({ serviceId: service.id, featureIndex: i })}
        onMouseLeave={() => !isMobile && setHighlightedFeature(null)}
        onTouchStart={() => setHighlightedFeature({ serviceId: service.id, featureIndex: i })}
        onTouchEnd={() => setTimeout(() => setHighlightedFeature(null), 200)}
      >
        <CheckCircle2 className={`h-5 w-5 mr-2 flex-shrink-0 ${service.iconColor}`} />
        <span className="text-sm sm:text-base text-gray-700">{feature}</span>
      </motion.div>
    ));
  }, [service.features, service.id, service.iconColor, service.highlightColor, highlightedFeature, isLowPerfDevice, isMobile, setHighlightedFeature]);

  if (!hasMounted) {
    return null;
  }

  return (
    <motion.section
      id={service.id}
      initial={{ opacity: 0, y: 10 }}
      whileInView={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.4, ease: "easeOut" }}
      viewport={{ once: true, margin: "-20px" }}
      className={`py-8 sm:py-16 rounded-lg shadow-md border overflow-visible scroll-mt-16 relative ${bgGradient}`}
      onMouseEnter={() => !isMobile && setHoveredService(service.id)}
      onMouseLeave={() => !isMobile && setHoveredService(null)}
      onTouchStart={() => setHoveredService(service.id)}
      onTouchEnd={() => setTimeout(() => setHoveredService(null), 150)}
      {...reducedMotionProps}
    >
      {!isLowPerfDevice && (
        <div className="absolute inset-0 overflow-hidden opacity-20">
          <motion.div
            className="absolute inset-0"
            style={{ backgroundImage: "url('/images/pattern.svg')", backgroundSize: "14px 14px" }}
            initial={{ rotate: 0, scale: 1 }}
            animate={{ rotate: sectionInView ? 1 : 0, scale: sectionInView ? 1.02 : 1 }}
            transition={{ duration: 1.2, ease: "easeInOut" }}
          />
        </div>
      )}

      {!isLowPerfDevice && sectionInView && (
        <div className="absolute inset-0 overflow-hidden pointer-events-none">
          <FloatingParticles color={themeColor} isParticleAnimationActive={sectionInView && !isMobile} />
        </div>
      )}

      <div className="container mx-auto px-4 sm:px-6 relative z-10">
        <div className="grid sm:grid-cols-2 gap-6 sm:gap-8 items-center">
          <div className={`order-1 ${isImageOnRight ? 'sm:order-2' : 'sm:order-1'}`}>
            <motion.div
              initial={{ scale: 0.98, opacity: 0.9 }}
              whileInView={{ scale: 1, opacity: 1 }}
              transition={{ duration: 0.3, ease: "easeOut" }}
              viewport={{ once: true }}
              variants={imageVariants}
              animate={imageAnimationState}
              className="relative h-[220px] sm:h-[320px] md:h-[480px] rounded-lg overflow-hidden shadow-lg group will-change-transform"
              {...reducedMotionProps}
            >
              <Image
                src={service.image || "/placeholder.svg"}
                alt={service.title}
                fill
                sizes="(max-width: 640px) 100vw, (max-width: 768px) 50vw, 800px"
                className="object-cover"
                priority={index < 1}
                loading={index < 1 ? "eager" : "lazy"}
                quality={isMobile ? 75 : 85}
              />
              <div className={`absolute inset-0 bg-gradient-to-br ${service.gradient} rounded-lg opacity-40`} />
              <motion.div
                className="absolute bottom-0 left-0 right-0 bg-gradient-to-t from-black/80 to-transparent p-5 sm:p-6 rounded-b-lg"
                initial={{ y: 4, opacity: 0.95 }}
                animate={{ y: 0, opacity: 1 }}
                transition={{ duration: 0.3, ease: "easeOut" }}
              >
                <h3 className="text-white text-xl sm:text-2xl md:text-3xl font-bold">{service.title}</h3>
                <div className="flex items-center mt-2">
                  <p className="text-white/90 text-sm">Premium Service</p>
                  <div className="ml-2 flex">
                    {[1, 2, 3, 4, 5].map((star) => (
                      <Star key={star} className="h-4 w-4 sm:h-5 sm:w-5 text-yellow-400" />
                    ))}
                  </div>
                </div>
                <motion.div
                  className="flex mt-3 overflow-hidden rounded-md"
                  initial={{ opacity: 0, y: 5 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ duration: 0.2, delay: 0.1, ease: "easeOut" }}
                >
                  <Link href={`#${service.id}`} scroll={false}>
                    <Button size="sm" className="bg-white text-gray-800 hover:bg-white/90 group flex items-center rounded-md text-sm py-2 px-4 h-auto font-medium">
                      Learn More
                      <ArrowRight className="h-4 w-4 ml-1.5 transition-transform duration-200 group-hover:translate-x-1" />
                    </Button>
                  </Link>
                </motion.div>
              </motion.div>
            </motion.div>
          </div>
          <div className={`order-2 ${isImageOnRight ? 'sm:order-1' : 'sm:order-2'} mt-4 sm:mt-0`}>
            <motion.div
              initial={{ opacity: 0 }}
              whileInView={{ opacity: 1 }}
              transition={{ duration: 0.3, ease: "easeOut" }}
              viewport={{ once: true }}
              {...reducedMotionProps}
            >
              <motion.div
                whileHover={!isLowPerfDevice ? { scale: 1.02 } : undefined}
                transition={{ duration: 0.15, ease: "easeOut" }}
                className="inline-flex items-center space-x-2 px-4 py-1.5 rounded-full text-sm sm:text-base mb-3 shadow-sm bg-gradient-to-r from-blue-600 to-purple-600 text-white font-medium"
              >
                <service.icon className="h-5 w-5" />
                <span>{service.title}</span>
              </motion.div>
              <h2 className={`text-3xl sm:text-4xl md:text-5xl font-bold mb-3 bg-gradient-to-r ${service.gradient} bg-clip-text text-transparent flex items-center`}>
                {service.title}
                <Sparkles className="h-5 w-5 ml-2 text-yellow-400" />
              </h2>
              <p className="text-gray-700 mb-4 text-base sm:text-lg">
                {service.description}
              </p>
              <Button
                variant="outline"
                className={`mb-4 flex items-center gap-2 shadow-sm hover:shadow-md hover:bg-gradient-to-r ${service.gradient} hover:text-white transition-all duration-150 group rounded-md text-sm py-2 px-4 h-auto font-medium`}
                onClick={() => toggleService(service.id)}
              >
                {activeService === service.id ? "Show Less" : "Show Details"}
                <motion.div
                  animate={{ rotate: activeService === service.id ? 180 : 0 }}
                  transition={{ duration: 0.2, ease: "easeInOut" }}
                  className="ml-1"
                >
                  <ChevronDown className="h-4 w-4" />
                </motion.div>
              </Button>
              <AnimatePresence mode="wait">
                {activeService === service.id && (
                  <motion.div
                    initial={{ opacity: 0, height: 0 }}
                    animate={{ opacity: 1, height: "auto" }}
                    exit={{ opacity: 0, height: 0 }}
                    transition={{ duration: 0.25, ease: "easeOut" }}
                    className="overflow-hidden mb-4 rounded-md"
                  >
                    <div
                      className="space-y-2 bg-white p-4 rounded-md"
                      style={{ boxShadow: "0 3px 10px -3px rgba(0, 0, 0, 0.1)" }}
                    >
                      <h3 className={`font-semibold text-base mb-2 ${service.featureColor}`}>
                        Key Features:
                      </h3>
                      {renderFeatures}
                    </div>
                  </motion.div>
                )}
              </AnimatePresence>
              <div className="mt-4 mb-2 relative z-10">
                <AuthModal
                  triggerText={`Get Started with ${service.title}`}
                  defaultTab="register"
                  className={`bg-gradient-to-r ${service.gradient} text-white hover:shadow-lg transition-all duration-150 hover:-translate-y-0.5 rounded-md text-sm sm:text-base font-medium w-full sm:w-auto py-2.5 px-5 h-auto`}
                />
              </div>
            </motion.div>
          </div>
        </div>
      </div>
    </motion.section>
  );
};

export default ServiceCard;