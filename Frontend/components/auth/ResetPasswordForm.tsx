// src/components/auth/ResetPasswordForm.tsx
import React, { useState, useEffect } from "react";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import * as z from "zod";
import { Form, FormControl, FormField, FormItem, FormLabel, FormMessage } from "@/components/ui/form";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { useToast } from "@/components/ui/use-toast";
import { Eye, EyeOff, Lock, CheckCircle, Loader2 } from "lucide-react";
import { API_BASE_URL, passwordRegex } from "./constants";
import { handleApiError } from "./utils";
import { PasswordStrengthIndicator } from "./PasswordStrengthIndicator";
import { motion } from "framer-motion";

// Schema for reset password
const resetPasswordSchema = z.object({
  new_password: z
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
  confirm_password: z.string(),
}).refine((data) => data.new_password === data.confirm_password, {
  message: "Passwords do not match",
  path: ["confirm_password"],
});

type ResetPasswordFormValues = z.infer<typeof resetPasswordSchema>;

interface ResetPasswordFormProps {
  token: string;
  onSuccess: () => void;
}

export function ResetPasswordForm({ token, onSuccess }: ResetPasswordFormProps) {
  const [showPassword, setShowPassword] = useState(false);
  const [showConfirmPassword, setShowConfirmPassword] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [isSuccess, setIsSuccess] = useState(false);
  const [isValidToken, setIsValidToken] = useState(true);
  const { toast } = useToast();

  const form = useForm<ResetPasswordFormValues>({
    resolver: zodResolver(resetPasswordSchema),
    defaultValues: {
      new_password: "",
      confirm_password: "",
    },
  });

  // Watch the password field to update the strength indicator
  const passwordValue = form.watch("new_password");

  // Verify token on component mount
  useEffect(() => {
    const verifyToken = async () => {
      try {
        const response = await fetch(`${API_BASE_URL}/reset-password?token=${token}`, {
          method: "GET",
        });
        
        if (!response.ok) {
          setIsValidToken(false);
          toast({
            title: "Invalid or Expired Token",
            description: "The password reset link is invalid or has expired. Please request a new password reset.",
            variant: "destructive",
            duration: 5000,
          });
        }
      } catch (error) {
        setIsValidToken(false);
        toast({
          title: "Verification Failed",
          description: "Unable to verify the reset token. Please try again later.",
          variant: "destructive",
          duration: 5000,
        });
      }
    };

    if (token) {
      verifyToken();
    } else {
      setIsValidToken(false);
    }
  }, [token, toast]);

  async function onSubmit(data: ResetPasswordFormValues) {
    setIsLoading(true);
    
    try {
      // Create form data to match backend expectations
      const formData = new FormData();
      formData.append("token", token);
      formData.append("new_password", data.new_password);
      formData.append("confirm_password", data.confirm_password);
      
      const response = await fetch(`${API_BASE_URL}/reset-password-confirm`, {
        method: "POST",
        body: formData,
      });
      
      // Check if HTML response or JSON
      const contentType = response.headers.get("content-type");
      if (contentType && contentType.includes("text/html")) {
        // Success is likely a redirect or HTML response
        const htmlResponse = await response.text();
        
        // Check if the response suggests success
        if (response.ok && (htmlResponse.includes("Password Reset Successful") || 
                           htmlResponse.includes("success"))) {
          setIsSuccess(true);
          
          toast({
            title: "Password Reset Successful",
            description: "Your password has been successfully reset. You can now log in with your new password.",
            duration: 5000,
          });
          
          // Wait a bit before redirecting to login
          setTimeout(() => {
            onSuccess();
          }, 2000);
        } else {
          // Parse error message from HTML if possible
          let errorMsg = "Failed to reset password";
          const errorMatch = htmlResponse.match(/<h1>(.*?)<\/h1>/);
          if (errorMatch) {
            errorMsg = errorMatch[1];
          }
          throw new Error(errorMsg);
        }
      } else {
        // Attempt to parse as JSON if not HTML
        let responseData;
        try {
          responseData = await response.json();
        } catch (e) {
          if (!response.ok) {
            throw new Error("Failed to reset password");
          }
        }
        
        if (!response.ok) {
          throw new Error(responseData?.detail || "Failed to reset password");
        }
        
        setIsSuccess(true);
        
        toast({
          title: "Password Reset Successful",
          description: "Your password has been successfully reset. You can now log in with your new password.",
          duration: 5000,
        });
        
        // Wait a bit before redirecting to login
        setTimeout(() => {
          onSuccess();
        }, 2000);
      }
    } catch (error: any) {
      const errorMessage = handleApiError(error, "Failed to reset password");
      
      toast({
        title: "Reset Failed",
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

  if (!isValidToken) {
    return (
      <motion.div variants={formVariants} initial="hidden" animate="visible" className="space-y-4">
        <div className="p-4 bg-red-50 border border-red-200 rounded-md">
          <p className="text-red-700">
            The password reset link is invalid or has expired. Please request a new password reset.
          </p>
          <Button 
            variant="outline" 
            className="mt-4 w-full"
            onClick={onSuccess} // Return to login page
          >
            Return to Login
          </Button>
        </div>
      </motion.div>
    );
  }

  if (isSuccess) {
    return (
      <motion.div variants={formVariants} initial="hidden" animate="visible" className="space-y-4">
        <div className="p-4 bg-green-50 border border-green-200 rounded-md flex flex-col items-center text-center">
          <CheckCircle className="h-16 w-16 text-green-500 mb-4" />
          <h3 className="text-xl font-semibold text-green-700 mb-2">Password Reset Successful</h3>
          <p className="text-green-700">
            Your password has been successfully reset. You can now log in with your new password.
          </p>
          <Button 
            variant="outline" 
            className="mt-4 w-full max-w-xs"
            onClick={onSuccess}
          >
            Go to Login
          </Button>
        </div>
      </motion.div>
    );
  }

  return (
    <motion.div variants={formVariants} initial="hidden" animate="visible" className="space-y-4">
      <h2 className="text-xl font-semibold mb-4">Reset Your Password</h2>
      
      <Form {...form}>
        <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-4">
          <FormField
            control={form.control}
            name="new_password"
            render={({ field }) => (
              <FormItem>
                <FormLabel>New Password</FormLabel>
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
                <PasswordStrengthIndicator password={passwordValue} />
              </FormItem>
            )}
          />
          
          <FormField
            control={form.control}
            name="confirm_password"
            render={({ field }) => (
              <FormItem>
                <FormLabel>Confirm Password</FormLabel>
                <FormControl>
                  <div className="relative">
                    <Lock className="absolute left-3 top-2.5 h-5 w-5 text-gray-400" />
                    <Input type={showConfirmPassword ? "text" : "password"} placeholder="••••••••" className="pl-10" {...field} />
                    <Button
                      type="button"
                      variant="ghost"
                      size="icon"
                      className="absolute right-0 top-0 h-full aspect-square text-gray-400 hover:text-gray-600"
                      onClick={() => setShowConfirmPassword(!showConfirmPassword)}
                    >
                      {showConfirmPassword ? <EyeOff size={16} /> : <Eye size={16} />}
                    </Button>
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
                Resetting Password...
              </>
            ) : (
              "Reset Password"
            )}
          </Button>
        </form>
      </Form>
    </motion.div>
  );
}