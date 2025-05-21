// src/components/auth/LoginForm.tsx
import React, { useState } from "react";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { Form, FormControl, FormField, FormItem, FormLabel, FormMessage } from "@/components/ui/form";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { useToast } from "@/components/ui/use-toast";
import { Eye, EyeOff, Mail, Lock, Loader2, AlertTriangle } from "lucide-react";
import { LoginFormValues, loginSchema } from "./schemas";
import { LOGIN_URL } from "./constants";
import { handleApiError } from "./utils";
import { VerificationAlert } from "./VerificationAlert";
import { motion } from "framer-motion";
import { ForgotPasswordForm } from "./ForgotPasswordForm";

interface LoginFormProps {
  onSuccess: (userData: any) => void;
  initialEmail?: string;
}

export function LoginForm({ onSuccess, initialEmail = "" }: LoginFormProps) {
  const [showPassword, setShowPassword] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [verificationSent, setVerificationSent] = useState(false);
  const [showForgotPassword, setShowForgotPassword] = useState(false);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);
  const { toast } = useToast();

  const form = useForm<LoginFormValues>({
    resolver: zodResolver(loginSchema),
    defaultValues: {
      email: initialEmail,
      password: "",
    },
  });

  async function onSubmit(data: LoginFormValues) {
    setIsLoading(true);
    setVerificationSent(false);
    setErrorMessage(null);
    
    try {
      const response = await fetch(LOGIN_URL, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(data),
        credentials: "include", // Include cookies if the server uses them
      });
      
      const responseData = await response.json();
      
      if (!response.ok) {
        // Handle specific error cases
        if (response.status === 401) {
          if (responseData.detail?.includes("not verified")) {
            setVerificationSent(true);
            throw new Error("Email not verified. A new verification email has been sent.");
          } else if (responseData.detail?.includes("incorrect password")) {
            throw new Error("Incorrect password. Please try again.");
          } else if (responseData.detail?.includes("not found") || responseData.detail?.includes("does not exist")) {
            throw new Error("Email address not found. Please check your email or register for an account.");
          }
        }
        throw new Error(responseData.detail || "Login failed");
      }
      
      // Store token in localStorage
      if (responseData.token) {
        localStorage.setItem("authToken", responseData.token);
      }
      
      toast({
        title: "Login successful",
        description: responseData.message || "Welcome back!",
        duration: 3000,
      });
      
      // Pass user data to parent component
      onSuccess({
        email: responseData.email,
        name: responseData.full_name,
        token: responseData.token,
        verified: responseData.verified,
        company_name: responseData.company_name,
        company_id: responseData.company_id,
        privileges: responseData.privileges,
      });
      
      // Dispatch event to notify other components about login state change
      window.dispatchEvent(new Event("loginStateChanged"));
    } catch (error: any) {
      const errorMsg = handleApiError(error, "Please check your credentials and try again");
      setErrorMessage(errorMsg);
      
      toast({
        title: "Login failed",
        description: errorMsg,
        variant: "destructive",
        duration: 5000,
      });
    } finally {
      setIsLoading(false);
    }
  }

  const formVariants = {
    hidden: { opacity: 0, y: 20 },
    visible: { opacity: 1, y: 0, transition: { duration: 0.4 } },
  };

  if (showForgotPassword) {
    return <ForgotPasswordForm onBack={() => setShowForgotPassword(false)} />;
  }

  return (
    <motion.div variants={formVariants} initial="hidden" animate="visible">
      <VerificationAlert show={verificationSent} />
      
      {errorMessage && !verificationSent && (
        <div className="mb-4 p-3 bg-red-50 border border-red-200 rounded-md flex items-start space-x-2">
          <AlertTriangle className="h-5 w-5 text-red-600 mt-0.5 flex-shrink-0" />
          <span className="text-sm text-red-700">{errorMessage}</span>
        </div>
      )}
      
      <Form {...form}>
        <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-4">
          <FormField
            control={form.control}
            name="email"
            render={({ field }) => (
              <FormItem>
                <FormLabel>Email</FormLabel>
                <FormControl>
                  <div className="relative">
                    <Mail className="absolute left-3 top-2.5 h-5 w-5 text-gray-400" />
                    <Input placeholder="email@example.com" className="pl-10" {...field} />
                  </div>
                </FormControl>
                <FormMessage />
              </FormItem>
            )}
          />
          <FormField
            control={form.control}
            name="password"
            render={({ field }) => (
              <FormItem>
                <FormLabel>Password</FormLabel>
                <FormControl>
                  <div className="relative">
                    <Lock className="absolute left-3 top-2.5 h-5 w-5 text-gray-400" />
                    <Input type={showPassword ? "text" : "password"} placeholder="••••••••" className="pl-10" {...field} />
                    <Button
                      type="button"
                      variant="ghost"
                      size="icon"
                      className="absolute right-0 top-0 h-full aspect-square text-gray-400 hover:text-gray-600"
                      onClick={() => setShowPassword(!showPassword)}
                    >
                      {showPassword ? <EyeOff size={16} /> : <Eye size={16} />}
                    </Button>
                  </div>
                </FormControl>
                <FormMessage />
              </FormItem>
            )}
          />
          <div className="flex justify-end">
            <Button 
              variant="link" 
              className="text-xs text-blue-600 hover:text-blue-800 p-0 h-auto" 
              type="button"
              onClick={() => setShowForgotPassword(true)}
            >
              Forgot Password?
            </Button>
          </div>
          <Button type="submit" className="w-full bg-blue-600 hover:bg-blue-700" disabled={isLoading}>
            {isLoading ? (
              <>
                <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                Logging in...
              </>
            ) : (
              "Login"
            )}
          </Button>
        </form>
      </Form>
    </motion.div>
  );
}