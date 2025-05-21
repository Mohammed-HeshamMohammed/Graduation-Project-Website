// src/components/auth/VerificationAlert.tsx
import React from "react";
import { AlertCircle } from "lucide-react";

interface VerificationAlertProps {
  show: boolean;
}

export function VerificationAlert({ show }: VerificationAlertProps) {
  if (!show) return null;

  return (
    <div className="mb-4 p-3 bg-blue-50 border border-blue-200 rounded-md flex items-start space-x-2">
      <AlertCircle className="h-5 w-5 text-blue-600 mt-0.5 flex-shrink-0" />
      <div className="text-sm text-blue-700">
        <p className="font-medium">Verification email sent</p>
        <p className="mt-1">
          Please check your inbox and click the verification link to complete your login.
          If you don't see the email, check your spam folder.
        </p>
      </div>
    </div>
  );
}