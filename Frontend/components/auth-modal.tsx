"use client";

import { useState } from "react";
import { Sheet, SheetContent, SheetDescription, SheetHeader, SheetTitle, SheetTrigger } from "@/components/ui/sheet";
import { Button, type ButtonProps } from "@/components/ui/button";
import { AuthForm } from "@/components/auth-form";
import { useRouter } from "next/navigation";
import { Avatar, AvatarFallback } from "@/components/ui/avatar";
import { User, LogIn } from "lucide-react";
import { motion } from "framer-motion";

interface AuthModalProps {
  triggerVariant?: ButtonProps["variant"];
  triggerText?: string;
  defaultTab?: "login" | "register";
  className?: string;
  useAvatar?: boolean;
}

export function AuthModal({
  triggerVariant = "default",
  triggerText = "Login",
  defaultTab = "login",
  className,
  useAvatar = false,
}: AuthModalProps) {
  const [isOpen, setIsOpen] = useState(false);
  const router = useRouter();

  return (
    <Sheet open={isOpen} onOpenChange={setIsOpen}>
      <SheetTrigger asChild>
        {useAvatar ? (
          <motion.div whileHover={{ scale: 1.05 }} whileTap={{ scale: 0.95 }}>
            <Avatar className={`cursor-pointer h-10 w-10 ring-2 ring-white/20 hover:ring-yellow-400/70 transition-all ${className}`}>
              <AvatarFallback className="bg-gradient-to-br from-blue-500 to-indigo-600 text-white">
                <User className="h-5 w-5" />
              </AvatarFallback>
            </Avatar>
          </motion.div>
        ) : (
          <motion.div whileHover={{ scale: 1.05 }} whileTap={{ scale: 0.95 }}>
            <Button variant={triggerVariant} className={`flex items-center gap-2 ${className}`}>
              <LogIn className="h-4 w-4" />
              {triggerText}
            </Button>
          </motion.div>
        )}
      </SheetTrigger>
      <SheetContent className="sm:max-w-md">
        <SheetHeader className="space-y-2 mb-6">
          <SheetTitle className="text-2xl font-bold text-blue-600">Welcome Back</SheetTitle>
          <SheetDescription className="text-gray-600">
            Login or create an account to access the fleet management dashboard
          </SheetDescription>
        </SheetHeader>
        <div className="py-4 overflow-y-auto max-h-[calc(100vh-12rem)]">
          <AuthForm
            defaultTab={defaultTab}
            onSuccess={(userData) => {
              setIsOpen(false);
              // Redirect or update state as needed:
              // router.push("/dashboard")
            }}
          />
        </div>
        <div className="absolute bottom-4 left-6 right-6">
          <div className="flex items-center justify-center gap-2 text-xs text-gray-500">
            <div className="w-2 h-2 rounded-full bg-blue-500"></div>
            Secured by TruckTrust™ Technology
          </div>
        </div>
      </SheetContent>
    </Sheet>
  );
}
