// src/components/auth/auth-form.tsx
"use client";

import React, { useState, useEffect } from "react";
import { useToast } from "@/components/ui/use-toast";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Loader2 } from "lucide-react";
import { STATUS_URL } from "./auth/constants";
import { LoginForm } from "./auth/LoginForm";
import { RegisterForm } from "./auth/RegisterForm";

interface AuthFormProps {
  onSuccess: (userData: any) => void;
  defaultTab?: "login" | "register";
}

export function AuthForm({ onSuccess, defaultTab = "login" }: AuthFormProps) {
  const [activeTab, setActiveTab] = useState<string>(defaultTab);
  const [isCheckingStatus, setIsCheckingStatus] = useState(true);
  const [loginEmail, setLoginEmail] = useState("");
  const { toast } = useToast();

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

  // Handle successful registration
  const handleRegisterSuccess = (email: string) => {
    setLoginEmail(email);
    setActiveTab("login");
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
          <LoginForm onSuccess={onSuccess} />
        </TabsContent>

        <TabsContent value="register">
          <RegisterForm onSuccess={handleRegisterSuccess} />
        </TabsContent>
      </Tabs>

      <div className="text-center text-sm text-gray-500">
        By continuing, you agree to our Terms of Service and Privacy Policy
      </div>
    </div>
  );
}