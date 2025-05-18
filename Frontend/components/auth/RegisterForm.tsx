// src/components/auth/RegisterForm.tsx
import React, { useState } from "react";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { Form, FormControl, FormField, FormItem, FormLabel, FormMessage } from "@/components/ui/form";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { useToast } from "@/components/ui/use-toast";
import { Eye, EyeOff, Mail, User, Building, MapPin, Lock, Loader2, AlertCircle } from "lucide-react";
import { RegisterFormValues, registerSchema } from "./schemas";
import { REGISTER_URL } from "./constants";
import { handleApiError } from "./utils";
import { PasswordStrengthIndicator } from "./PasswordStrengthIndicator";
import { motion } from "framer-motion";
import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert";

interface RegisterFormProps {
  onSuccess: (email: string) => void;
}

export function RegisterForm({ onSuccess }: RegisterFormProps) {
  const [showPassword, setShowPassword] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [verificationSent, setVerificationSent] = useState(false);
  const [emailVerificationInfo, setEmailVerificationInfo] = useState<string | null>(null);
  const [companyError, setCompanyError] = useState<string | null>(null);
  const { toast } = useToast();

  const form = useForm<RegisterFormValues>({
    resolver: zodResolver(registerSchema),
    defaultValues: {
      full_name: "",
      email: "",
      password: "",
      company_name: "",
      company_address: "",
    },
  });

  // Watch the password field to update the strength indicator
  const passwordValue = form.watch("password");
  const emailValue = form.watch("email");
  const companyNameValue = form.watch("company_name");

  // Clear company error when company name changes
  React.useEffect(() => {
    if (companyError) {
      setCompanyError(null);
    }
  }, [companyNameValue]);

  async function onSubmit(data: RegisterFormValues) {
    setIsLoading(true);
    setVerificationSent(false);
    setEmailVerificationInfo(null);
    setCompanyError(null);
    
    try {
      const response = await fetch(REGISTER_URL, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(data),
      });
      
      const responseData = await response.json();
      
      // Handle different response cases
      if (response.status === 409) {
        // Email already registered and verified
        toast({
          title: "Email already registered",
          description: "This email address is already in use. Please log in instead.",
          variant: "destructive",
          duration: 5000,
        });
        return;
      }

      // Handle company already registered case (403 Forbidden)
      if (response.status === 403) {
        setCompanyError(responseData.detail || "This company is already registered.");
        toast({
          title: "Company already registered",
          description: responseData.detail || "This company is already registered. New users must be added by an existing team member.",
          variant: "destructive",
          duration: 5000,
        });
        return;
      }
      
      if (!response.ok) {
        throw new Error(responseData.detail || "Registration failed");
      }
      
      // Check if this is a resend verification situation
      if (responseData.message?.includes("Verification email resent")) {
        setVerificationSent(true);
        setEmailVerificationInfo(data.email);
        toast({
          title: "Verification Email Resent",
          description: `We've sent another verification email to ${data.email}. Please check your inbox.`,
          duration: 5000,
        });
        return;
      }
      
      // Normal successful registration
      toast({
        title: "Registration successful",
        description: "Please check your email to verify your account before logging in.",
        duration: 5000,
      });
      
      // Set verification status for UI feedback
      setVerificationSent(true);
      setEmailVerificationInfo(data.email);
      
      // Reset the register form
      form.reset();
      
      // Return the email to pre-fill the login form
      onSuccess(data.email);
    } catch (error: any) {
      const errorMessage = handleApiError(error, "Please check your information and try again");
      
      toast({
        title: "Registration failed",
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
    <motion.div variants={formVariants} initial="hidden" animate="visible">
      {verificationSent && emailVerificationInfo && (
        <Alert className="mb-6 bg-white border-blue-700">
          <AlertCircle className="h-4 w-4 text-blue-700" />
          <AlertTitle className="text-blue-600">Verification Email Sent</AlertTitle>
          <AlertDescription className="text-blue-700">
            We've sent a verification email to <strong>{emailVerificationInfo}</strong>. 
            Please check your inbox and click the verification link to complete your registration.
          </AlertDescription>
        </Alert>
      )}
      
      {companyError && (
        <Alert className="mb-6 bg-red-600/50 border-amber-700">
          <AlertCircle className="h-4 w-4 text-amber-700" />
          <AlertTitle className="text-amber-600">Company Registration Restricted</AlertTitle>
          <AlertDescription className="text-amber-700">
            {companyError} Please contact your company administrator to add you as a team member.
          </AlertDescription>
        </Alert>
      )}
      
      <Form {...form}>
        <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-4">
          <div className="grid grid-cols-1 gap-4">
            <FormField
              control={form.control}
              name="full_name"
              render={({ field }) => (
                <FormItem>
                  <FormLabel>Full Name</FormLabel>
                  <FormControl>
                    <div className="relative">
                      <User className="absolute left-3 top-2.5 h-5 w-5 text-gray-400" />
                      <Input placeholder="John Doe" className="pl-10" {...field} />
                    </div>
                  </FormControl>
                  <FormMessage />
                </FormItem>
              )}
            />
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
                  <PasswordStrengthIndicator password={passwordValue} />
                </FormItem>
              )}
            />
            <FormField
              control={form.control}
              name="company_name"
              render={({ field }) => (
                <FormItem>
                  <FormLabel>Company Name</FormLabel>
                  <FormControl>
                    <div className="relative">
                      <Building className="absolute left-3 top-2.5 h-5 w-5 text-gray-400" />
                      <Input placeholder="Acme Inc." className="pl-10" {...field} />
                    </div>
                  </FormControl>
                  <FormMessage />
                  {companyError && (
                    <p className="text-xs text-amber-600 mt-1">
                      This company already has an account. New users must be added by an existing team member.
                    </p>
                  )}
                </FormItem>
              )}
            />
            <FormField
              control={form.control}
              name="company_address"
              render={({ field }) => (
                <FormItem>
                  <FormLabel>Company Address</FormLabel>
                  <FormControl>
                    <div className="relative">
                      <MapPin className="absolute left-3 top-2.5 h-5 w-5 text-gray-400" />
                      <Input placeholder="123 Main St, City, Country" className="pl-10" {...field} />
                    </div>
                  </FormControl>
                  <FormMessage />
                </FormItem>
              )}
            />
          </div>
          <Button type="submit" className="w-full bg-blue-600 hover:bg-blue-700 mt-2" disabled={isLoading}>
            {isLoading ? (
              <>
                <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                Creating account...
              </>
            ) : (
              "Register"
            )}
          </Button>
        </form>
      </Form>
    </motion.div>
  );
}