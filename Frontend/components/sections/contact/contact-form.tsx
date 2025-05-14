"use client"

import { useState } from "react"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { useToast } from "@/components/ui/use-toast"
import { motion } from "framer-motion"
import { SendIcon } from "lucide-react"
import { ContactFormFields } from "./ContactFormFields"

export function ContactForm() {
  const [isSubmitting, setIsSubmitting] = useState(false)
  const [formState, setFormState] = useState({
    firstName: "",
    lastName: "",
    email: "",
    phone: "",
    company: "",
    message: ""
  })
  const { toast } = useToast()

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>) => {
    const { id, value } = e.target
    setFormState(prev => ({
      ...prev,
      [id]: value
    }))
  }

  const handleSubmit = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault()
    setIsSubmitting(true)

    await new Promise((resolve) => setTimeout(resolve, 1500))

    toast({
      title: "Message sent successfully!",
      description: "We'll get back to you as soon as possible.",
      className: "bg-gradient-to-r from-blue-600 to-indigo-600 text-white"
    })

    setIsSubmitting(false)
    setFormState({
      firstName: "",
      lastName: "",
      email: "",
      phone: "",
      company: "",
      message: ""
    })
  }

  return (
    <motion.div initial={{ opacity: 0, y: 15 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.4 }}>
      <Card className="bg-white shadow-lg border-none overflow-hidden">
        <div className="absolute h-2 w-full bg-gradient-to-r from-blue-500 via-indigo-500 to-purple-500 top-0"></div>
        <CardHeader className="pb-6">
          <CardTitle className="text-xl md:text-2xl font-bold bg-gradient-to-r from-blue-700 via-indigo-600 to-purple-700 bg-clip-text text-transparent">
            Send us a message
          </CardTitle>
          <CardDescription className="mt-2">
            Fill out the form below and we'll get back to you as soon as possible.
          </CardDescription>
        </CardHeader>
        <CardContent>
          <motion.form className="space-y-4" onSubmit={handleSubmit}>
            <ContactFormFields formState={formState} handleChange={handleChange} />
            <Button type="submit" className="w-full h-12" disabled={isSubmitting}>
              {isSubmitting ? "Sending..." : "Send Message"}
              <SendIcon className="h-4 w-4 ml-2" />
            </Button>
          </motion.form>
        </CardContent>
      </Card>
    </motion.div>
  )
}
