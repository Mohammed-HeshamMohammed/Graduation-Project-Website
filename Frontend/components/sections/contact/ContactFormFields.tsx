"use client"

import { Input } from "@/components/ui/input"
import { Textarea } from "@/components/ui/textarea"
import { User, Briefcase, MessageSquare, Phone, Mail } from "lucide-react"

interface ContactFormFieldsProps {
  formState: {
    firstName: string
    lastName: string
    email: string
    phone: string
    company: string
    message: string
  }
  handleChange: (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>) => void
}

export function ContactFormFields({ formState, handleChange }: ContactFormFieldsProps) {
  return (
    <>
      <div className="grid gap-3 sm:grid-cols-2">
        <div className="space-y-2">
          <label htmlFor="first-name" className="text-sm font-medium text-gray-700">
            First name
          </label>
          <div className="relative">
            <User className="h-4 w-4 text-gray-400 absolute top-3 left-3" />
            <Input id="firstName" placeholder="John" required className="pl-10 h-10 md:h-12" value={formState.firstName} onChange={handleChange} />
          </div>
        </div>
        <div className="space-y-2">
          <label htmlFor="last-name" className="text-sm font-medium text-gray-700">
            Last name
          </label>
          <div className="relative">
            <User className="h-4 w-4 text-gray-400 absolute top-3 left-3" />
            <Input id="lastName" placeholder="Doe" required className="pl-10 h-10 md:h-12" value={formState.lastName} onChange={handleChange} />
          </div>
        </div>
      </div>

      <div className="space-y-2">
        <label htmlFor="email" className="text-sm font-medium text-gray-700">
          Email
        </label>
        <div className="relative">
          <Mail className="h-4 w-4 text-gray-400 absolute top-3 left-3" />
          <Input id="email" placeholder="john.doe@example.com" type="email" required className="pl-10 h-10 md:h-12" value={formState.email} onChange={handleChange} />
        </div>
      </div>

      <div className="space-y-2">
        <label htmlFor="phone" className="text-sm font-medium text-gray-700">
          Phone
        </label>
        <div className="relative">
          <Phone className="h-4 w-4 text-gray-400 absolute top-3 left-3" />
          <Input id="phone" placeholder="+1 (555) 123-4567" type="tel" className="pl-10 h-10 md:h-12" value={formState.phone} onChange={handleChange} />
        </div>
      </div>

      <div className="space-y-2">
        <label htmlFor="company" className="text-sm font-medium text-gray-700">
          Company
        </label>
        <div className="relative">
          <Briefcase className="h-4 w-4 text-gray-400 absolute top-3 left-3" />
          <Input id="company" placeholder="Acme Inc." className="pl-10 h-10 md:h-12" value={formState.company} onChange={handleChange} />
        </div>
      </div>

      <div className="space-y-2">
        <label htmlFor="message" className="text-sm font-medium text-gray-700">
          Message
        </label>
        <div className="relative">
          <MessageSquare className="h-4 w-4 text-gray-400 absolute top-3 left-3" />
          <Textarea id="message" placeholder="How can we help you?" rows={4} required className="pl-10 resize-none" value={formState.message} onChange={handleChange} />
        </div>
      </div>
    </>
  )
}
