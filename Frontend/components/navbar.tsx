// Updated navbar.tsx file

"use client"

import { useState, useEffect } from "react"
import Link from "next/link"
import { useRouter, usePathname } from "next/navigation"
import { Button } from "@/components/ui/button"
import { Sheet, SheetContent, SheetTrigger } from "@/components/ui/sheet"
import { Truck, Menu, Home, Info, Mail, BarChart } from "lucide-react"
import { AuthModal } from "./auth-modal"
import { ContextMenu } from "./context-menu"
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar"

const navItems = [
  { label: "HOME", href: "/", icon: <Home className="h-4 w-4" /> },
  { label: "ABOUT", href: "/about", icon: <Info className="h-4 w-4" /> },
  { label: "SERVICES", href: "/services", icon: <Truck className="h-4 w-4" /> },
  { label: "CONTACT", href: "/contact", icon: <Mail className="h-4 w-4" /> },
  { label: "DEMO", href: "/demo-dashboard", icon: <BarChart className="h-4 w-4" /> },
]

// API endpoints
const API_BASE_URL = "http://localhost:8000/api";
const STATUS_URL = `${API_BASE_URL}/status`;
const LOGOUT_URL = `${API_BASE_URL}/logout`;

export default function Navbar() {
  const [isScrolled, setIsScrolled] = useState(false)
  const [isLoggedIn, setIsLoggedIn] = useState(false)
  const [user, setUser] = useState<{ name: string; email: string } | null>(null)
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false)
  const [isMobileView, setIsMobileView] = useState(false)
  const pathname = usePathname()
  const router = useRouter()

  // Function to get first two names from full name
  const getShortName = (fullName: string) => {
    if (!fullName) return "User";
    const nameParts = fullName.split(' ');
    return nameParts.length > 1 
      ? `${nameParts[0]} ${nameParts[1]}`
      : fullName;
  };

  // Function to check and update login state
  const checkLoginState = async () => {
    try {
      const token = localStorage.getItem("authToken");
      if (!token) {
        setIsLoggedIn(false);
        setUser(null);
        return;
      }

      const response = await fetch(`${STATUS_URL}?token=${token}`);
      const data = await response.json();

      if (data.is_logged_in) {
        setIsLoggedIn(true);
        setUser({
          name: data.full_name || "User",
          email: data.email
        });
      } else {
        // Token is invalid or expired
        localStorage.removeItem("authToken");
        setIsLoggedIn(false);
        setUser(null);
      }
    } catch (error) {
      console.error("Error checking login status:", error);
      setIsLoggedIn(false);
      setUser(null);
    }
  }

  // Handle successful login
  const handleLoginSuccess = () => {
    checkLoginState();
  }

  // Handle navigation from context menu
  const handleNavigation = (destination: string) => {
    switch(destination) {
      case 'profile':
        router.push('/profile');
        break;
      case 'dashboard':
        router.push('/demo-dashboard');
        break;
      case 'settings':
        router.push('/settings');
        break;
      case 'team-access':
        router.push('/team-access');
        break;
      default:
        break;
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
    window.addEventListener("loginStateChanged", handleLoginStateChange)
    
    return () => {
      window.removeEventListener("scroll", handleScroll)
      window.removeEventListener("resize", handleResize)
      window.removeEventListener("loginStateChanged", handleLoginStateChange)
    }
  }, [])

  const handleLogout = async () => {
    try {
      const token = localStorage.getItem("authToken");
      await fetch(LOGOUT_URL, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "Authorization": `Bearer ${token}`
        }
      });
      
      // Clear local storage
      localStorage.removeItem("authToken");
      
      // Update state
      setIsLoggedIn(false);
      setUser(null);
      setIsContextMenuOpen(false);
      
      // Dispatch event to notify other components
      window.dispatchEvent(new Event("loginStateChanged"));
      
      router.push("/");
    } catch (error) {
      console.error("Logout error:", error);
    }
  }

  // Get shortened user name for display
  const shortUserName = user ? getShortName(user.name) : "User";

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
              <ContextMenu 
                isLoggedIn={isLoggedIn}
                onLogout={handleLogout}
                onNavigate={handleNavigation}
                userName={user?.name || "User"}
                userEmail={user?.email || "user@example.com"}
                avatarSrc="/images/avatar-1.jpg"
                isScrolled={isScrolled}
              />
            ) : (
              <AuthModal 
                useAvatar={true}
                defaultTab="login"
                onLoginSuccess={handleLoginSuccess}
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
                  
                  {/* Add authentication options in mobile menu */}
                  <div className="p-4 border-t mt-auto">
                    {isLoggedIn ? (
                      <div className="flex flex-col space-y-2">
                        <div className="flex items-center gap-3 mb-2">
                          <Avatar className="h-10 w-10">
                            <AvatarImage src="/images/avatar-1.jpg" alt={user?.name} />
                            <AvatarFallback className="bg-blue-100 text-blue-600">
                              {user?.name?.charAt(0) || "U"}
                            </AvatarFallback>
                          </Avatar>
                          <div>
                            <div className="font-medium text-sm">
                              {user?.name ? user.name.split(' ').slice(0, 2).join(' ') : "User"}
                            </div>
                            <div className="text-xs text-gray-500">{user?.email}</div>
                          </div>
                        </div>
                        <Button variant="outline" className="w-full" onClick={handleLogout}>
                          Log Out
                        </Button>
                      </div>
                    ) : (
                      <AuthModal 
                        triggerVariant="default"
                        triggerText="Login / Register"
                        className="w-full"
                        onLoginSuccess={handleLoginSuccess}
                      />
                    )}
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

function setIsContextMenuOpen(arg0: boolean) {
  throw new Error("Function not implemented.")
}
