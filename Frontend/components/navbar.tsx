"use client"

import { useState, useEffect } from "react"
import Link from "next/link"
import { useRouter, usePathname } from "next/navigation"
import { Button } from "@/components/ui/button"
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar"
import { Sheet, SheetContent, SheetTrigger } from "@/components/ui/sheet"
import { Truck, Menu, Home, Info, Mail, BarChart } from "lucide-react"
import { AuthModal } from "./auth-modal"
import { ContextMenu } from "./context-menu"

const navItems = [
  { label: "HOME", href: "/", icon: <Home className="h-4 w-4" /> },
  { label: "ABOUT", href: "/about", icon: <Info className="h-4 w-4" /> },
  { label: "SERVICES", href: "/services", icon: <Truck className="h-4 w-4" /> },
  { label: "CONTACT", href: "/contact", icon: <Mail className="h-4 w-4" /> },
  { label: "DEMO", href: "/demo-dashboard", icon: <BarChart className="h-4 w-4" /> },
]

// Create a custom event for login state changes
export const LOGIN_STATE_CHANGED = "loginStateChanged"

export default function Navbar() {
  const [isScrolled, setIsScrolled] = useState(false)
  const [isLoggedIn, setIsLoggedIn] = useState(false)
  const [user, setUser] = useState<{ name: string; email: string } | null>(null)
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false)
  const [isMobileView, setIsMobileView] = useState(false)
  const [isContextMenuOpen, setIsContextMenuOpen] = useState(false)
  const pathname = usePathname()
  const router = useRouter()

  // Function to check and update login state
  const checkLoginState = () => {
    const token = localStorage.getItem("token")
    const userData = localStorage.getItem("user")

    if (token && userData) {
      setIsLoggedIn(true)
      setUser(JSON.parse(userData))
    } else {
      setIsLoggedIn(false)
      setUser(null)
    }
  }

  useEffect(() => {
    const handleScroll = () => {
      setIsScrolled(window.scrollY > 20)
    }

    const handleResize = () => {
      setIsMobileView(window.innerWidth < 768)
    }

    // Handle login state changes
    const handleLoginStateChange = () => {
      checkLoginState()
    }

    // Initialize
    checkLoginState()
    handleResize()

    // Add event listeners
    window.addEventListener("scroll", handleScroll)
    window.addEventListener("resize", handleResize)
    window.addEventListener(LOGIN_STATE_CHANGED, handleLoginStateChange)
    
    // Check for login state changes periodically (as a fallback)
    const loginCheckInterval = setInterval(checkLoginState, 2000)
    
    return () => {
      window.removeEventListener("scroll", handleScroll)
      window.removeEventListener("resize", handleResize)
      window.removeEventListener(LOGIN_STATE_CHANGED, handleLoginStateChange)
      clearInterval(loginCheckInterval)
    }
  }, [])

  const handleLogout = () => {
    localStorage.removeItem("token")
    localStorage.removeItem("user")
    setIsLoggedIn(false)
    setUser(null)
    
    // Dispatch event to notify other components
    window.dispatchEvent(new Event(LOGIN_STATE_CHANGED))
    
    router.push("/")
  }

  // Desktop Navbar Component
  const DesktopNavbar = () => (
    <header
      className={`fixed top-0 left-0 right-0 z-50 ${
        isScrolled 
          ? "bg-white/95 backdrop-blur-sm shadow-lg py-2" 
          : "bg-gradient-to-b from-black/50 to-transparent py-4"
      }`}
    >
      <div className="container mx-auto px-4">
        <div className="flex items-center justify-between">
          <Link href="/" className="flex items-center space-x-3 min-w-[160px] group">
            <div className={`p-2 rounded-lg ${
              isScrolled ? "bg-blue-100/80" : "bg-white/10"
            }`}>
              <Truck className={`h-7 w-7 ${
                isScrolled ? "text-blue-600" : "text-white group-hover:text-yellow-400"
              }`} />
            </div>
            <span className={`text-2xl font-bold tracking-tight ${
              isScrolled ? "text-gray-900" : "text-white group-hover:text-yellow-400"
            }`}>TRUCKING</span>
          </Link>

          <nav className="hidden md:flex items-center space-x-1 min-w-[500px] justify-center">
            {navItems.map((item) => (
              <Link
                key={item.href}
                href={item.href}
                className={`px-4 py-2 rounded-md text-sm font-medium ${
                  pathname === item.href
                    ? isScrolled
                      ? "text-blue-600 bg-blue-50/80"
                      : "text-yellow-400 bg-white/10"
                    : isScrolled
                      ? "text-gray-700 hover:text-blue-600 hover:bg-blue-50/80"
                      : "text-white/90 hover:text-yellow-400 hover:bg-white/10"
                }`}
              >
                {item.label}
              </Link>
            ))}
          </nav>

          <div className="flex items-center space-x-4 min-w-[160px] justify-end">
            {isLoggedIn ? (
              <>
                {/* Avatar Button that opens Context Menu */}
                <Button 
                  variant="ghost" 
                  className={`relative rounded-full p-0 h-10 w-10 border-2 ${
                    isScrolled ? "border-blue-600" : "border-yellow-400"
                  }`}
                  onClick={() => setIsContextMenuOpen(true)}
                >
                  <Avatar className="h-full w-full">
                    <AvatarImage src="/images/avatar-1.jpg" alt={user?.name || "User"} />
                    <AvatarFallback className={isScrolled ? "bg-blue-100 text-blue-600" : "bg-yellow-400/20 text-white"}>
                      {user?.name?.charAt(0) || "U"}
                    </AvatarFallback>
                  </Avatar>
                </Button>
                
                {/* Context Menu */}
                <ContextMenu 
                  isOpen={isContextMenuOpen} 
                  onClose={() => setIsContextMenuOpen(false)} 
                />
              </>
            ) : (
              <AuthModal 
                useAvatar={true}
                defaultTab="login"
              />
            )}
            
            <Sheet open={mobileMenuOpen} onOpenChange={setMobileMenuOpen}>
              <SheetTrigger asChild>
                <Button 
                  variant="ghost" 
                  size="icon" 
                  className={`md:hidden ${
                    isScrolled ? "text-blue-600 hover:bg-blue-50" : "text-white hover:bg-white/10"
                  }`}
                >
                  <Menu className="h-5 w-5" />
                </Button>
              </SheetTrigger>
              <SheetContent side="right" className="w-[80%] sm:w-[350px] p-0">
                <div className="flex flex-col h-full">
                  <div className="p-6 border-b">
                    <div className="flex items-center space-x-3">
                      <div className="p-2 rounded-lg bg-blue-100">
                        <Truck className="h-6 w-6 text-blue-600" />
                      </div>
                      <span className="text-xl font-bold text-gray-900">TRUCKING</span>
                    </div>
                  </div>
                  
                  <div className="flex-1 overflow-auto py-2">
                    <nav className="flex flex-col">
                      {navItems.map((item) => (
                        <Link
                          key={item.href}
                          href={item.href}
                          onClick={() => setMobileMenuOpen(false)}
                          className={`flex items-center justify-between px-6 py-4 border-b border-gray-100 ${
                            pathname === item.href
                              ? "bg-blue-50 text-blue-600"
                              : "text-gray-700 hover:bg-gray-50"
                          }`}
                        >
                          <div className="flex items-center space-x-3">
                            {item.icon}
                            <span className="font-medium">{item.label}</span>
                          </div>
                        </Link>
                      ))}
                    </nav>
                  </div>
                  
                </div>
              </SheetContent>
            </Sheet>
          </div>
        </div>
      </div>
    </header>
  )

  // Mobile Bottom Navbar Component
  const MobileBottomNavbar = () => (
    <div
      className={`md:hidden fixed bottom-0 left-0 right-0 z-40 bg-white border-t shadow-lg`}
    >
      <div className="grid grid-cols-5 h-16">
        {navItems.map((item) => (
          <Link
            key={item.href}
            href={item.href}
            className={`flex flex-col items-center justify-center space-y-1 ${
              pathname === item.href
                ? "text-blue-600"
                : "text-gray-600 hover:text-blue-600"
            }`}
          >
            <div className={`p-1 rounded-md ${pathname === item.href ? "bg-blue-100" : ""}`}>
              {item.icon}
            </div>
            <span className="text-xs font-medium">{item.label}</span>
          </Link>
        ))}
      </div>
    </div>
  )

  return (
    <>
      {/* Always render desktop navbar for larger screens */}
      <DesktopNavbar />
      
      {/* Render mobile bottom navbar only on mobile view */}
      {isMobileView && <MobileBottomNavbar />}
      
      {/* Add padding to bottom of page when mobile navbar is visible */}
      {isMobileView && <div className="h-16" />}
    </>
  )
}