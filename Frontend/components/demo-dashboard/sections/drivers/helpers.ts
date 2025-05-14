import React, { ReactNode } from "react";
import { Badge } from "@/components/ui/badge";
import { AlertTriangle, CheckCircle, Clock } from "lucide-react";

/**
 * Returns a status badge UI element based on driver status
 */
export function getStatusBadge(status: 'active' | 'inactive'): ReactNode {
  return React.createElement(
    Badge,
    { variant: "outline", className: status === 'active' 
      ? "bg-green-100 text-green-800 border-green-200" 
      : "bg-gray-100 text-gray-800 border-gray-200" 
    },
    status === 'active' ? [
      React.createElement(CheckCircle, { className: "mr-1 h-3 w-3", key: "icon" }),
      " Active"
    ] : "Inactive"
  );
}

/**
 * Returns a badge UI element with license expiration status
 */
export function getLicenseStatus(expirationDate: string): ReactNode {
  const today = new Date();
  const expiration = new Date(expirationDate);
  const daysUntilExpiration = Math.ceil(
    (expiration.getTime() - today.getTime()) / (1000 * 60 * 60 * 24)
  );

  if (daysUntilExpiration < 0) {
    return React.createElement(
      Badge,
      { variant: "outline", className: "bg-red-100 text-red-800 border-red-200" },
      [
        React.createElement(AlertTriangle, { className: "mr-1 h-3 w-3", key: "icon" }),
        " Expired"
      ]
    );
  } else if (daysUntilExpiration < 30) {
    return React.createElement(
      Badge,
      { variant: "outline", className: "bg-amber-100 text-amber-800 border-amber-200" },
      [
        React.createElement(Clock, { className: "mr-1 h-3 w-3", key: "icon" }),
        ` Expires in ${daysUntilExpiration} days`
      ]
    );
  } else {
    return React.createElement(
      Badge,
      { variant: "outline", className: "bg-green-100 text-green-800 border-green-200" },
      [
        React.createElement(CheckCircle, { className: "mr-1 h-3 w-3", key: "icon" }),
        " Valid"
      ]
    );
  }
}

/**
 * Returns a badge UI element for the safety score with appropriate color coding
 */
export function getSafetyScoreBadge(score: number): ReactNode {
  let badgeClass = "";
  
  if (score >= 90) {
    badgeClass = "bg-green-100 text-green-800 border-green-200";
  } else if (score >= 80) {
    badgeClass = "bg-blue-100 text-blue-800 border-blue-200";
  } else if (score >= 70) {
    badgeClass = "bg-amber-100 text-amber-800 border-amber-200";
  } else {
    badgeClass = "bg-red-100 text-red-800 border-red-200";
  }
  
  return React.createElement(
    Badge,
    { variant: "outline", className: badgeClass },
    `${score}/100`
  );
}