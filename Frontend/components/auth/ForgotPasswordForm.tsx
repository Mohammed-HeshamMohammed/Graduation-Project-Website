// src/components/auth/ForgotPasswordForm.tsx
import React, { useState } from "react";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import * as z from "zod";
import { Form, FormControl, FormField, FormItem, FormLabel, FormMessage } from "@/components/ui/form";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { useToast } from "@/components/ui/use-toast";
import { Mail, Loader2, ArrowLeft } from "lucide-react";
import { API_BASE_URL } from "./constants";
import { handleApiError } from "./utils";
import { motion } from "framer-motion";

// Schema for forgot password
const forgotPasswordSchema = z.object({
  email: z.string().email({ message: "Please enter a valid email address" }),
});

type ForgotPasswordFormValues = z.infer<typeof forgotPasswordSchema>;

interface ForgotPasswordFormProps {
  onBack: () => void;
}

export function ForgotPasswordForm({ onBack }: ForgotPasswordFormProps) {
  const [isLoading, setIsLoading] = useState(false);
  const [emailSent, setEmailSent] = useState(false);
  const { toast } = useToast();

  const form = useForm<ForgotPasswordFormValues>({
    resolver: zodResolver(forgotPasswordSchema),
    defaultValues: {
      email: "",
    },
  });
  
  async function onSubmit(data: ForgotPasswordFormValues) {
    setIsLoading(true);
    
    try {
      // Method 1: Send as query parameter
      const response = await fetch(`${API_BASE_URL}/forgot-password?email=${encodeURIComponent(data.email)}`, {
        method: "POST",
        headers: {
          "Content-Type": "application/x-www-form-urlencoded",
        },
      });
      
      // Alternative Method 2: Send as form data (uncomment if Method 1 doesn't work)
      /*
      const formData = new FormData();
      formData.append('email', data.email);
      
      const response = await fetch(`${API_BASE_URL}/forgot-password`, {
        method: "POST",
        body: formData,
      });
      */
      
      // Handle both JSON and non-JSON responses
      let responseData;
      const contentType = response.headers.get("content-type");
      if (contentType && contentType.includes("application/json")) {
        responseData = await response.json();
      } else {
        const text = await response.text();
        responseData = { message: text };
      }
      
      if (!response.ok) {
        throw new Error(responseData.detail || "Failed to process request");
      }
      
      setEmailSent(true);
      
      toast({
        title: "Password Reset Email Sent",
        description: "If an account exists with this email, you will receive password reset instructions.",
        duration: 5000,
      });
    } catch (error: any) {
      const errorMessage = handleApiError(error, "Failed to process password reset request");
      
      toast({
        title: "Request Failed",
        description: errorMessage,
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

  return (
    <motion.div variants={formVariants} initial="hidden" animate="visible" className="space-y-4">
      <div className="flex items-center mb-4">
        <Button 
          variant="ghost" 
          size="sm" 
          className="p-0 mr-2 hover:bg-transparent" 
          onClick={onBack}
        >
          <ArrowLeft className="h-5 w-5" />
        </Button>
        <h2 className="text-xl font-semibold">Reset Password</h2>
      </div>
      
      {emailSent ? (
        <div className="p-4 bg-green-50 border border-green-200 rounded-md">
          <p className="text-green-700">
            If an account exists with this email, you will receive instructions to reset your password.
            Please check your inbox and follow the instructions in the email.
          </p>
          <Button 
            variant="outline" 
            className="mt-4 w-full"
            onClick={onBack}
          >
            Return to Login
          </Button>
        </div>
      ) : (
        <Form {...form}>
          <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-4">
            <div className="mb-4">
              <p className="text-sm text-gray-600">
                Enter the email address associated with your account and we'll send you instructions to reset your password.
              </p>
            </div>
            
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
            
            <Button type="submit" className="w-full bg-blue-600 hover:bg-blue-700" disabled={isLoading}>
              {isLoading ? (
                <>
                  <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                  Sending...
                </>
              ) : (
                "Send Reset Instructions"
              )}
            </Button>
            
            <Button 
              type="button" 
              variant="ghost" 
              className="w-full text-gray-600 hover:text-gray-800"
              onClick={onBack}
              disabled={isLoading}
            >
              Cancel
            </Button>
          </form>
        </Form>
      )}
    </motion.div>
  );
}