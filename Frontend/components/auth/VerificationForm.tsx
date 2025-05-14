// components/auth/VerificationForm.tsx
"use client";

import { useEffect } from "react";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { z } from "zod";
import { Button } from "@/components/ui/button";
import { Form, FormControl, FormField, FormItem, FormLabel, FormMessage } from "@/components/ui/form";
import { Input } from "@/components/ui/input";
import { useToast } from "@/components/ui/use-toast";
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from "@/components/ui/card";
import { Loader2, Mail, KeyRound } from "lucide-react";
import { Dispatch, SetStateAction } from "react";

// Schema for verification form
const verifySchema = z.object({
  email: z.string().email({ message: "Please enter a valid email address" }),
  code: z.string().min(6, { message: "Verification code must be 6 digits" }).max(6, { message: "Verification code must be 6 digits" }),
});

type VerifyFormValues = z.infer<typeof verifySchema>;

interface VerificationFormProps {
  initialEmail: string;
  loading: boolean;
  resendLoading: boolean;
  countdown: number;
  onSubmit: (data: VerifyFormValues) => Promise<void>;
  onResendCode: (email: string) => Promise<void>;
  setCountdown: Dispatch<SetStateAction<number>>;
}

export default function VerificationForm({ 
  initialEmail, 
  loading, 
  resendLoading, 
  countdown, 
  onSubmit, 
  onResendCode,
  setCountdown
}: VerificationFormProps) {
  const { toast } = useToast();

  const form = useForm<VerifyFormValues>({
    resolver: zodResolver(verifySchema),
    defaultValues: {
      email: initialEmail || "",
      code: "",
    },
  });

  // Handle countdown for resend button
  useEffect(() => {
    if (countdown > 0) {
      const timer = setTimeout(() => setCountdown(countdown - 1), 1000);
      return () => clearTimeout(timer);
    }
  }, [countdown, setCountdown]);

  function handleResend() {
    const email = form.getValues("email");
    if (!email) {
      toast({
        title: "Error",
        description: "Please enter your email address first",
        variant: "destructive",
        duration: 3000
      });
      return;
    }
    onResendCode(email);
  }

  return (
    <Card className="w-full border-t-4 border-t-blue-600 shadow-lg">
      <CardHeader className="space-y-1">
        <CardTitle className="text-2xl font-bold text-center">Verify Your Email</CardTitle>
        <CardDescription className="text-center">
          Enter the 6-digit code sent to your email address
        </CardDescription>
      </CardHeader>
      <CardContent>
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
                      <Input 
                        type="email" 
                        placeholder="email@example.com" 
                        className="pl-10" 
                        {...field} 
                      />
                    </div>
                  </FormControl>
                  <FormMessage />
                </FormItem>
              )}
            />
            <FormField
              control={form.control}
              name="code"
              render={({ field }) => (
                <FormItem>
                  <FormLabel>Verification Code</FormLabel>
                  <FormControl>
                    <div className="relative">
                      <KeyRound className="absolute left-3 top-2.5 h-5 w-5 text-gray-400" />
                      <Input 
                        type="text" 
                        inputMode="numeric" 
                        pattern="[0-9]*" 
                        maxLength={6} 
                        placeholder="123456" 
                        className="pl-10" 
                        {...field} 
                      />
                    </div>
                  </FormControl>
                  <FormMessage />
                </FormItem>
              )}
            />
            <Button 
              type="submit" 
              className="w-full bg-blue-600 hover:bg-blue-700 transition-colors" 
              disabled={loading}
            >
              {loading ? (
                <>
                  <Loader2 className="mr-2 h-4 w-4 animate-spin" /> 
                  Verifying...
                </>
              ) : "Verify Email"}
            </Button>
          </form>
        </Form>
      </CardContent>
      <CardFooter className="flex flex-col space-y-2 pb-6">
        <div className="text-sm text-center text-gray-500">
          Didn't receive the code?
        </div>
        <Button 
          variant="outline" 
          size="sm" 
          onClick={handleResend} 
          disabled={resendLoading || countdown > 0}
          className="text-sm"
        >
          {resendLoading ? (
            <>
              <Loader2 className="mr-2 h-3 w-3 animate-spin" /> 
              Sending...
            </>
          ) : countdown > 0 ? (
            `Resend code in ${countdown}s`
          ) : (
            "Resend verification code"
          )}
        </Button>
      </CardFooter>
    </Card>
  );
}