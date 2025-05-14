// File: progress-bar.tsx
"use client";

import { FC, useId } from "react";
import styles from "../charts/progress-bar.module.css"; // Make sure this path is correct

interface ProgressBarProps {
  value: number;
  max: number;
  color?: string;
  height?: string; // Tailwind height class (e.g., "h-2")
  showLabel?: boolean;
  label?: string;
}

export const ProgressBar: FC<ProgressBarProps> = ({
  value,
  max,
  color = "#3b82f6",
  height = "h-2",
  showLabel = false,
  label,
}) => {
  const percentage = (value / max) * 100;
  const uniqueId = useId();
  const cssVarId = uniqueId.replace(/:/g, "");
  
  // Dynamically inject CSS variables using a style tag
  return (
    <>
      <style>
        {`
          .progress-container-${cssVarId} .${styles.progressBar} {
            width: ${percentage}%;
            background-color: ${color};
          }
        `}
      </style>
      <div className="space-y-1">
        {showLabel && label && (
          <div className="flex justify-between text-xs">
            <span>{label}</span>
            <span>{Math.round(percentage)}%</span>
          </div>
        )}
        <div 
          className={`w-full ${height} ${styles.progressBarContainer} progress-container-${cssVarId}`}
        >
          <div className={styles.progressBar} />
        </div>
      </div>
    </>
  );
};