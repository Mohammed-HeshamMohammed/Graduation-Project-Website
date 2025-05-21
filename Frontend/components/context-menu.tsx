"use client";

import React, { useRef, useEffect, useState } from 'react';
import { motion } from "framer-motion";
import { User, Settings, UsersRound, LogOut, LayoutDashboard } from "lucide-react";
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar";
import { Button } from "@/components/ui/button";
import { useRouter } from 'next/navigation';


interface ContextMenuProps {
  isLoggedIn: boolean;
  onLogout?: () => void;
  onNavigate?: (destination: string) => void;
  userName?: string;
  userEmail?: string;
  avatarSrc?: string;
  isScrolled?: boolean;
  className?: string;
}

export const ContextMenu = ({ 
  isLoggedIn,
  onLogout,
  onNavigate,
  userName = "User",
  userEmail = "user@example.com",
  avatarSrc = "/images/avatar-1.jpg",
  isScrolled = false,
  className
}: ContextMenuProps) => {
  const [isMenuOpen, setIsMenuOpen] = useState(false);
  const avatarButtonRef = useRef<HTMLButtonElement>(null);
  const menuRef = useRef<HTMLDivElement>(null);

  // Function to get first two names from full name
  const getShortName = (fullName: string) => {
    const nameParts = fullName.split(' ');
    return nameParts.length > 1 
      ? `${nameParts[0]} ${nameParts[1]}`
      : fullName;
  };

  const shortName = getShortName(userName);

  useEffect(() => {
    function handleClickOutside(event: MouseEvent) {
      if (
        menuRef.current && 
        !menuRef.current.contains(event.target as Node) &&
        avatarButtonRef.current && 
        !avatarButtonRef.current.contains(event.target as Node)
      ) {
        setIsMenuOpen(false);
      }
    }

    if (isMenuOpen) {
      document.addEventListener("mousedown", handleClickOutside);
    }
    return () => {
      document.removeEventListener("mousedown", handleClickOutside);
    };
  }, [isMenuOpen]);

  const handleAvatarClick = () => {
    setIsMenuOpen(!isMenuOpen);
  };
  
  // Improved position calculation based on avatar button
  const getMenuPosition = () => {
    if (!avatarButtonRef.current) return {};
    
    const rect = avatarButtonRef.current.getBoundingClientRect();
    const menuWidth = 240; // Width of our menu in pixels
    
    // Position the menu directly below the avatar and account for window edges
    const windowWidth = window.innerWidth;
    let left = rect.left + (rect.width / 2) - (menuWidth / 2);
    
    // Ensure menu doesn't go off screen on the left
    if (left < 10) left = 10;
    
    // Ensure menu doesn't go off screen on the right
    if (left + menuWidth > windowWidth - 10) {
      left = windowWidth - menuWidth - 10;
    }
    
    return {
      top: `${rect.bottom + 8}px`,
      left: `${left}px`,
      width: `${menuWidth}px`
    };
  };
  const router = useRouter();
  const handleMenuItemClick = (action: string) => {
    if (action === 'logout' && onLogout) {
      onLogout();
      router.push('/'); // redirect to home
    } else if (onNavigate) {
      onNavigate(action);
    }
    setIsMenuOpen(false);
  };

  if (!isLoggedIn) return null;

  return (
    <div className={className}>
      {/* Avatar Button - Kept the same as requested */}
      <Button 
        ref={avatarButtonRef}
        variant="ghost" 
        className={`relative rounded-full p-0 h-10 w-10 border-2 ${
          isScrolled ? "border-blue-600" : "border-yellow-400"
        }`}
        onClick={handleAvatarClick}
      >
        <Avatar className="h-full w-full">
          <AvatarImage src={avatarSrc} alt={shortName} />
          <AvatarFallback className={isScrolled ? "bg-blue-100 text-blue-600" : "bg-yellow-400/20 text-white"}>
            {shortName.charAt(0)}
          </AvatarFallback>
        </Avatar>
      </Button>
      
      {/* Context Menu - Updated to match auth form styling */}
      {isMenuOpen && (
        <div className="fixed inset-0 z-50 pointer-events-none">
          <motion.div 
            ref={menuRef}
            className="absolute bg-white rounded-lg shadow-xl pointer-events-auto"
            style={getMenuPosition()}
            initial={{ opacity: 0, y: -10 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -10 }}
            transition={{ duration: 0.2 }}
          >
            {/* Avatar header section - Styled to match auth modal header */}
            <div className="flex flex-col items-center justify-center pt-6 pb-4 px-4 border-b border-gray-200 bg-gradient-to-br from-blue-500 to-blue-600">
              <Avatar className="h-16 w-16 mb-3 ring-2 ring-white/70 ring-offset-2 ring-offset-blue-600">
                <AvatarImage src={avatarSrc} alt={shortName} />
                <AvatarFallback className="bg-gradient-to-br from-blue-500 to-indigo-600 text-white text-lg">
                  {shortName.charAt(0)}
                </AvatarFallback>
              </Avatar>
              <div className="text-center">
                <p className="text-white font-semibold">{shortName}</p>
                <p className="text-blue-100 text-sm">{userEmail}</p>
              </div>
            </div>
            
            <div className="py-3 flex flex-col gap-2">
              <ul className="list-none flex flex-col gap-1 px-2">
                <li 
                  className="flex items-center text-gray-600 gap-2 px-3 py-2 rounded-md hover:bg-blue-600 hover:text-white hover:translate-x-0.5 hover:-translate-y-0.5 transition-all cursor-pointer"
                  onClick={() => handleMenuItemClick('profile')}
                >
                  <User size={18} />
                  <p className="font-semibold text-sm">Profile</p>
                </li>
                <li 
                  className="flex items-center text-gray-600 gap-2 px-3 py-2 rounded-md hover:bg-blue-600 hover:text-white hover:translate-x-0.5 hover:-translate-y-0.5 transition-all cursor-pointer"
                  onClick={() => handleMenuItemClick('dashboard')}
                >
                  <LayoutDashboard size={18} />
                  <p className="font-semibold text-sm">Dashboard</p>
                </li>
              </ul>
              
              <div className="border-t border-gray-200"></div>
              
              <ul className="list-none flex flex-col gap-1 px-2">
                <li 
                  className="flex items-center text-gray-600 gap-2 px-3 py-2 rounded-md hover:bg-blue-600 hover:text-white hover:translate-x-0.5 hover:-translate-y-0.5 transition-all cursor-pointer"
                  onClick={() => handleMenuItemClick('settings')}
                >
                  <Settings size={18} />
                  <p className="font-semibold text-sm">Settings</p>
                </li>
                <li 
                  className="flex items-center text-blue-600 gap-2 px-3 py-2 rounded-md hover:bg-blue-50 hover:text-blue-700 hover:translate-x-0.5 hover:-translate-y-0.5 transition-all cursor-pointer"
                  onClick={() => handleMenuItemClick('team-access')}
                >
                  <UsersRound size={18} className="stroke-blue-600" />
                  <p className="font-semibold text-sm">Team Access</p>
                </li>
              </ul>
              
              <div className="border-t border-gray-200"></div>
              
              <ul className="list-none flex flex-col gap-1 px-2 pb-2">
                <li 
                  className="flex items-center text-red-500 gap-2 px-3 py-2 rounded-md hover:bg-red-500/10 hover:text-red-600 hover:translate-x-0.5 hover:-translate-y-0.5 transition-all cursor-pointer"
                  onClick={() => handleMenuItemClick('logout')}
                >
                  <LogOut size={18} className="stroke-red-500" />
                  <p className="font-semibold text-sm">Log out</p>
                </li>
              </ul>
            </div>
            
            {/* Footer with security note to match auth form */}
            <div className="border-t border-gray-200 py-2 px-3">
              <div className="flex items-center justify-center gap-2 text-xs text-gray-500">
                <div className="w-2 h-2 rounded-full bg-blue-500"></div>
                Secured by Trucking™ Technology
              </div>
            </div>
          </motion.div>
        </div>
      )}
    </div>
  );
}