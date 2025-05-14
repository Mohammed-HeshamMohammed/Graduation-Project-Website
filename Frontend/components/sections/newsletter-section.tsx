import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"

export function NewsletterSection() {
  return (
    <section className="py-20 bg-gray-900 text-white">
      <div className="container mx-auto px-4">
        <div className="max-w-2xl mx-auto text-center">
          <h2 className="text-3xl font-bold mb-4">NEWSLETTER SUBSCRIBE</h2>
          <p className="mb-8">
            Subscribe to our newsletter and we will inform you about newest projects and promotions.
          </p>
          <div className="flex gap-4">
            <Input type="email" placeholder="Enter your email" className="bg-white" />
            <Button className="bg-yellow-500 hover:bg-yellow-600 text-black">SUBSCRIBE</Button>
          </div>
        </div>
      </div>
    </section>
  )
}

