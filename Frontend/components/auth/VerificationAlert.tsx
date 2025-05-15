// src/components/auth/VerificationAlert.tsx
import React from "react";

interface VerificationAlertProps {
  show: boolean;
}

export function VerificationAlert({ show }: VerificationAlertProps) {
  if (!show) return null;

  return (
    <div className="mb-4 p-3 bg-blue-50 border border-blue-200 rounded-md text-blue-700 text-sm">
      A verification email has been sent. Please check your inbox and verify your account before logging in.
    </div>
  );
}