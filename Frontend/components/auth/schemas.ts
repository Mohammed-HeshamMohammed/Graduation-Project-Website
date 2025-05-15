// src/components/auth/schemas.ts
import * as z from "zod";
import { passwordRegex } from "./constants";

export const loginSchema = z.object({
  email: z.string().email({ message: "Please enter a valid email address" }),
  password: z.string().min(8, { message: "Password must be at least 8 characters" }),
});

export const registerSchema = z.object({
  full_name: z.string().min(2, { message: "Name must be at least 2 characters" }),
  email: z.string().email({ message: "Please enter a valid email address" }),
  password: z
    .string()
    .min(8, { message: "Password must be at least 8 characters" })
    .refine((value) => passwordRegex.uppercase.test(value), {
      message: "Password must include at least one uppercase letter",
    })
    .refine((value) => passwordRegex.lowercase.test(value), {
      message: "Password must include at least one lowercase letter",
    })
    .refine((value) => passwordRegex.number.test(value), {
      message: "Password must include at least one number",
    })
    .refine((value) => passwordRegex.special.test(value), {
      message: "Password must include at least one special character",
    }),
  company_name: z.string().min(2, { message: "Company name must be at least 2 characters" }),
  company_address: z.string().min(5, { message: "Address must be at least 5 characters" }),
});

export type LoginFormValues = z.infer<typeof loginSchema>;
export type RegisterFormValues = z.infer<typeof registerSchema>;
