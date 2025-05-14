// components/auth/VerificationSuccess.tsx
import { Card, CardContent } from "@/components/ui/card";
import { CheckCircle } from "lucide-react";

export default function SuccessState() {
  return (
    <Card className="w-full border-t-4 border-t-green-500 shadow-lg">
      <CardContent className="pt-6 pb-6">
        <div className="text-center py-6">
          <CheckCircle className="w-16 h-16 text-green-500 mx-auto mb-4" />
          <p className="text-green-600 font-medium text-xl">Email verified successfully!</p>
          <p className="text-sm text-gray-500 mt-2">Redirecting you to dashboard...</p>
        </div>
      </CardContent>
    </Card>
  );
}