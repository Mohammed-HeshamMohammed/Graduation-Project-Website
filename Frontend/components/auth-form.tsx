"use client";

import { useState, useEffect } from "react";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import * as z from "zod";
import { Button } from "@/components/ui/button";
import { Form, FormControl, FormField, FormItem, FormLabel, FormMessage } from "@/components/ui/form";
import { Input } from "@/components/ui/input";
import { useToast } from "@/components/ui/use-toast";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Eye, EyeOff, Mail, User, Building, MapPin, Lock, Loader2 } from "lucide-react";
import { motion } from "framer-motion";

// Define API URLs dynamically based on environment
const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api";
const LOGIN_URL = `${API_BASE_URL}/login`;
const REGISTER_URL = `${API_BASE_URL}/register`;
const STATUS_URL = `${API_BASE_URL}/status`;
const LOGOUT_URL = `${API_BASE_URL}/logout`;

// Password validation - match backend requirements
const passwordRegex = {
  uppercase: /[A-Z]/,
  lowercase: /[a-z]/,
  number: /[0-9]/,
  special: /[!@#$%^&*(),.?":{}|<>]/,
};

// Define form schemas - matching backend requirements
const loginSchema = z.object({
  email: z.string().email({ message: "Please enter a valid email address" }),
  password: z.string().min(8, { message: "Password must be at least 8 characters" }),
});

const registerSchema = z.object({
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

type LoginFormValues = z.infer<typeof loginSchema>;
type RegisterFormValues = z.infer<typeof registerSchema>;

interface AuthFormProps {
  onSuccess: (userData: any) => void;
  defaultTab?: "login" | "register";
}

// Helper function to calculate password strength
function calculatePasswordStrength(password: string): { label: string; color: string; strength: number } {
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

export function AuthForm({ onSuccess, defaultTab = "login" }: AuthFormProps) {
  const [activeTab, setActiveTab] = useState<string>(defaultTab);
  const [showPassword, setShowPassword] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [isCheckingStatus, setIsCheckingStatus] = useState(true);
  const [verificationSent, setVerificationSent] = useState(false);
  const { toast } = useToast();

  // Login form
  const loginForm = useForm<LoginFormValues>({
    resolver: zodResolver(loginSchema),
    defaultValues: {
      email: "",
      password: "",
    },
  });

  // Register form
  const registerForm = useForm<RegisterFormValues>({
    resolver: zodResolver(registerSchema),
    defaultValues: {
      full_name: "",
      email: "",
      password: "",
      company_name: "",
      company_address: "",
    },
  });

  // Check if user is already logged in on component mount
  useEffect(() => {
    const checkLoginStatus = async () => {
      try {
        const token = localStorage.getItem("authToken");
        if (!token) {
          setIsCheckingStatus(false);
          return;
        }

        const response = await fetch(`${STATUS_URL}?token=${token}`);
        const data = await response.json();

        if (data.is_logged_in) {
          // Pass user data to parent component to update the UI
          onSuccess({
            email: data.email,
            name: data.full_name,
            token: token,
            verified: true,
          });
          
          // Dispatch event to notify other components about login state change
          window.dispatchEvent(new Event("loginStateChanged"));
        }
      } catch (error) {
        console.error("Error checking login status:", error);
        // Clear potentially invalid token
        localStorage.removeItem("authToken");
      } finally {
        setIsCheckingStatus(false);
      }
    };

    checkLoginStatus();
  }, [onSuccess]);

  // Watch the password field to update the strength indicator
  const passwordValue = registerForm.watch("password");
  const strength = calculatePasswordStrength(passwordValue || "");

  // Helper function to handle API errors
  const handleApiError = (error: any, defaultMessage: string) => {
    let errorMessage = defaultMessage;
    
    if (error.message && typeof error.message === 'string') {
      errorMessage = error.message;
    } else if (error.detail && typeof error.detail === 'string') {
      errorMessage = error.detail;
    }
    
    return errorMessage;
  };

  // Login function
  async function onLoginSubmit(data: LoginFormValues) {
    setIsLoading(true);
    setVerificationSent(false);
    
    try {
      const response = await fetch(LOGIN_URL, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(data),
      });
      
      const responseData = await response.json();
      
      if (!response.ok) {
        // Special case for unverified email
        if (response.status === 401 && responseData.detail?.includes("not verified")) {
          setVerificationSent(true);
          throw new Error("Email not verified. A new verification email has been sent.");
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
      });
      
      // Dispatch event to notify other components about login state change
      window.dispatchEvent(new Event("loginStateChanged"));
    } catch (error: any) {
      const errorMessage = handleApiError(error, "Please check your credentials and try again");
      
      toast({
        title: "Login failed",
        description: errorMessage,
        variant: "destructive",
        duration: 5000,
      });
    } finally {
      setIsLoading(false);
    }
  }

  // Registration function
  async function onRegisterSubmit(data: RegisterFormValues) {
    setIsLoading(true);
    
    try {
      const response = await fetch(REGISTER_URL, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(data),
      });
      
      const responseData = await response.json();
      
      if (!response.ok) {
        // Check for specific error cases
        if (response.status === 409) {
          throw new Error("This email is already registered. Please log in instead.");
        }
        throw new Error(responseData.detail || "Registration failed");
      }
      
      toast({
        title: "Registration successful",
        description: "Please check your email to verify your account before logging in.",
        duration: 5000,
      });
      
      // Reset the register form
      registerForm.reset();
      
      // Pre-fill login email for convenience
      loginForm.setValue("email", data.email);
      
      // Switch to login tab after successful registration
      setActiveTab("login");
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

  if (isCheckingStatus) {
    return (
      <div className="flex justify-center items-center p-8">
        <Loader2 className="h-8 w-8 animate-spin text-blue-600" />
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <Tabs value={activeTab} onValueChange={setActiveTab} className="w-full">
        <TabsList className="grid grid-cols-2 w-full mb-6">
          <TabsTrigger value="login" className="data-[state=active]:bg-blue-600 data-[state=active]:text-white">
            Login
          </TabsTrigger>
          <TabsTrigger value="register" className="data-[state=active]:bg-blue-600 data-[state=active]:text-white">
            Register
          </TabsTrigger>
        </TabsList>

        <TabsContent value="login">
          <motion.div variants={formVariants} initial="hidden" animate="visible">
            {verificationSent && (
              <div className="mb-4 p-3 bg-blue-50 border border-blue-200 rounded-md text-blue-700 text-sm">
                A verification email has been sent. Please check your inbox and verify your account before logging in.
              </div>
            )}
            
            <Form {...loginForm}>
              <form onSubmit={loginForm.handleSubmit(onLoginSubmit)} className="space-y-4">
                <FormField
                  control={loginForm.control}
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
                  control={loginForm.control}
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
                    onClick={() => {
                      toast({
                        title: "Reset Password",
                        description: "Password reset functionality will be implemented soon. Please contact support for assistance.",
                        duration: 5000,
                      });
                    }}
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
        </TabsContent>

        <TabsContent value="register">
          <motion.div variants={formVariants} initial="hidden" animate="visible">
            <Form {...registerForm}>
              <form onSubmit={registerForm.handleSubmit(onRegisterSubmit)} className="space-y-4">
                <div className="grid grid-cols-1 gap-4">
                  <FormField
                    control={registerForm.control}
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
                    control={registerForm.control}
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
                    control={registerForm.control}
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
                        {passwordValue && (
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
                              <li className={passwordValue.length >= 8 ? "text-green-600" : ""}>
                                ✓ At least 8 characters
                              </li>
                              <li className={passwordRegex.uppercase.test(passwordValue) ? "text-green-600" : ""}>
                                ✓ At least one uppercase letter
                              </li>
                              <li className={passwordRegex.lowercase.test(passwordValue) ? "text-green-600" : ""}>
                                ✓ At least one lowercase letter
                              </li>
                              <li className={passwordRegex.number.test(passwordValue) ? "text-green-600" : ""}>
                                ✓ At least one number
                              </li>
                              <li className={passwordRegex.special.test(passwordValue) ? "text-green-600" : ""}>
                                ✓ At least one special character
                              </li>
                            </ul>
                          </div>
                        )}
                      </FormItem>
                    )}
                  />
                  <FormField
                    control={registerForm.control}
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
                      </FormItem>
                    )}
                  />
                  <FormField
                    control={registerForm.control}
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
        </TabsContent>
      </Tabs>

      <div className="text-center text-sm text-gray-500">
        By continuing, you agree to our Terms of Service and Privacy Policy
      </div>
    </div>
  );
}