// src/components/auth/PasswordStrengthIndicator.tsx
import React from "react";
import { calculatePasswordStrength } from "./utils";
import { passwordRegex } from "./constants";

interface PasswordStrengthIndicatorProps {
  password: string;
}

export function PasswordStrengthIndicator({ password }: PasswordStrengthIndicatorProps) {
  const strength = calculatePasswordStrength(password);

  if (!password) return null;

  return (
    <div>
      <div className={`mt-1 text-sm ${strength.color}`}>
        Password strength: {strength.label}
      </div>
      <div className="mt-2 flex gap-1 h-1">
        {[1, 2, 3, 4, 5].map((index) => (
          <div 
            key={index}
            className={`h-full flex-1 rounded-full ${
              index <= strength.strength 
                ? index <= 2 
                  ? "bg-red-500" 
                  : index <= 4 
                    ? "bg-yellow-500" 
                    : "bg-green-500"
                : "bg-gray-200"
            }`}
          />
        ))}
      </div>
      <ul className="text-xs mt-2 text-gray-600 space-y-1">
        <li className={password.length >= 8 ? "text-green-600" : ""}>
          ✓ At least 8 characters
        </li>
        <li className={passwordRegex.uppercase.test(password) ? "text-green-600" : ""}>
          ✓ At least one uppercase letter
        </li>
        <li className={passwordRegex.lowercase.test(password) ? "text-green-600" : ""}>
          ✓ At least one lowercase letter
        </li>
        <li className={passwordRegex.number.test(password) ? "text-green-600" : ""}>
          ✓ At least one number
        </li>
        <li className={passwordRegex.special.test(password) ? "text-green-600" : ""}>
          ✓ At least one special character
        </li>
      </ul>
    </div>
  );
}