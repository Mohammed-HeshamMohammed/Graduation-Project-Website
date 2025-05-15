// src/components/auth/utils.ts
import { passwordRegex } from "./constants";

export function calculatePasswordStrength(password: string): { label: string; color: string; strength: number } {
  let score = 0;
  if (password.length >= 8) score++;
  if (passwordRegex.uppercase.test(password)) score++;
  if (passwordRegex.lowercase.test(password)) score++;
  if (passwordRegex.number.test(password)) score++;
  if (passwordRegex.special.test(password)) score++;

  if (score <= 2) return { label: "Weak", color: "text-red-600", strength: score };
  if (score <= 4) return { label: "Medium", color: "text-yellow-600", strength: score };
  return { label: "Strong", color: "text-green-600", strength: score };
}

export const handleApiError = (error: any, defaultMessage: string) => {
  let errorMessage = defaultMessage;
  
  if (error.message && typeof error.message === 'string') {
    errorMessage = error.message;
  } else if (error.detail && typeof error.detail === 'string') {
    errorMessage = error.detail;
  }
  
  return errorMessage;
};