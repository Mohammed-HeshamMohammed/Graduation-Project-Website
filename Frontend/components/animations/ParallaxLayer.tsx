// components/animations/ParallaxLayer.tsx
"use client";

import { motion, useScroll, useTransform } from "framer-motion";
import { useRef, useEffect, useState } from "react";

interface ParallaxLayerProps {
  children: React.ReactNode;
  depth?: number;
}

export function ParallaxLayer({ children, depth = 0.5 }: ParallaxLayerProps) {
  const ref = useRef<HTMLDivElement>(null);
  const [elementTop, setElementTop] = useState(0);
  const [clientHeight, setClientHeight] = useState(0);
  
  useEffect(() => {
    if (!ref.current) return;
    const setValues = () => {
      setElementTop(ref.current!.offsetTop);
      setClientHeight(window.innerHeight);
    };
    
    setValues();
    window.addEventListener("resize", setValues);
    return () => window.removeEventListener("resize", setValues);
  }, []);
  
  const { scrollY } = useScroll();
  const y = useTransform(
    scrollY, 
    [elementTop - clientHeight, elementTop + clientHeight], 
    [`${-depth * 100}px`, `${depth * 100}px`]
  );
  
  return (
    <motion.div ref={ref} style={{ y }} className="relative">
      {children}
    </motion.div>
  );
}
