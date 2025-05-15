"use client";

import React from 'react';
import { motion } from "framer-motion";
import { Pencil, UserRoundPlus, Settings, Trash2, UsersRound, LogOut } from "lucide-react";

interface ContextMenuProps {
  isOpen: boolean;
  onClose: () => void;
}

export const ContextMenu = ({ isOpen, onClose }: ContextMenuProps) => {
  if (!isOpen) return null;
  
  // Close the menu when clicking outside
  const handleOutsideClick = (e: React.MouseEvent) => {
    if ((e.target as HTMLElement).classList.contains('context-menu-backdrop')) {
      onClose();
    }
  };

  return (
    <div 
      className="fixed inset-0 z-50 context-menu-backdrop" 
      onClick={handleOutsideClick}
    >
      <motion.div 
        className="absolute right-4 top-16 w-48 bg-[#242832] bg-gradient-to-br from-[#242832] to-[#251c28] rounded-lg shadow-xl"
        initial={{ opacity: 0, y: -10 }}
        animate={{ opacity: 1, y: 0 }}
        exit={{ opacity: 0, y: -10 }}
        transition={{ duration: 0.2 }}
      >
        <div className="py-3 flex flex-col gap-2">
          <ul className="list-none flex flex-col gap-1 px-2">
            <li className="flex items-center text-[#7e8590] gap-2 px-3 py-2 rounded-md hover:bg-[#5353ff] hover:text-white hover:translate-x-0.5 hover:-translate-y-0.5 transition-all cursor-pointer">
              <Pencil size={18} className="stroke-[#7e8590] group-hover:stroke-white" />
              <p className="font-semibold text-sm">Rename</p>
            </li>
            <li className="flex items-center text-[#7e8590] gap-2 px-3 py-2 rounded-md hover:bg-[#5353ff] hover:text-white hover:translate-x-0.5 hover:-translate-y-0.5 transition-all cursor-pointer">
              <UserRoundPlus size={18} className="stroke-[#7e8590]" />
              <p className="font-semibold text-sm">Add Member</p>
            </li>
          </ul>
          
          <div className="border-t border-[#42434a]"></div>
          
          <ul className="list-none flex flex-col gap-1 px-2">
            <li className="flex items-center text-[#7e8590] gap-2 px-3 py-2 rounded-md hover:bg-[#5353ff] hover:text-white hover:translate-x-0.5 hover:-translate-y-0.5 transition-all cursor-pointer">
              <Settings size={18} className="stroke-[#7e8590]" />
              <p className="font-semibold text-sm">Settings</p>
            </li>
            <li className="flex items-center text-[#7e8590] gap-2 px-3 py-2 rounded-md hover:bg-[#8e2a2a] hover:text-white hover:translate-x-0.5 hover:-translate-y-0.5 transition-all cursor-pointer">
              <Trash2 size={18} className="stroke-[#7e8590]" />
              <p className="font-semibold text-sm">Delete</p>
            </li>
          </ul>
          
          <div className="border-t border-[#42434a]"></div>
          
          <ul className="list-none flex flex-col gap-1 px-2">
            <li className="flex items-center text-[#bd89ff] gap-2 px-3 py-2 rounded-md hover:bg-[rgba(56,45,71,0.836)] hover:text-[#bd89ff] hover:translate-x-0.5 hover:-translate-y-0.5 transition-all cursor-pointer">
              <UsersRound size={18} className="stroke-[#bd89ff]" />
              <p className="font-semibold text-sm">Team Access</p>
            </li>
            <li className="flex items-center text-red-400 gap-2 px-3 py-2 rounded-md hover:bg-red-500/20 hover:text-red-300 hover:translate-x-0.5 hover:-translate-y-0.5 transition-all cursor-pointer">
              <LogOut size={18} className="stroke-red-400" />
              <p className="font-semibold text-sm">Log out</p>
            </li>
          </ul>
        </div>
      </motion.div>
    </div>
  );
};