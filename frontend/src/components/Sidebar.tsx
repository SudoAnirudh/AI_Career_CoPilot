"use client";

import React from "react";
import Link from "next/link";
import { usePathname } from "next/navigation";
import { 
  Briefcase, 
  Trophy, 
  BarChart3, 
  Mail, 
  LayoutDashboard, 
  Settings,
  Sparkles
} from "lucide-react";
import styles from "./Sidebar.module.css";

const Sidebar: React.FC = () => {
  const pathname = usePathname();

  const menuItems = [
    { name: "Dashboard", path: "/", icon: <LayoutDashboard size={20} /> },
    { name: "Opportunities", path: "/jobs", icon: <Briefcase size={20} /> },
    { name: "Kanban Board", path: "/kanban", icon: <Trophy size={20} /> },
    { name: "Outreach Center", path: "/outreach", icon: <Mail size={20} /> },
    { name: "Analytics", path: "/analytics", icon: <BarChart3 size={20} /> }
  ];

  return (
    <aside className={styles.sidebar}>
      <div className={styles.logoContainer}>
        <div className={styles.logoIcon}>
          <Sparkles size={24} className={styles.sparkle} />
        </div>
        <div className={styles.logoText}>
          <h2>CareerCoPilot</h2>
          <span>AI-Powered Success</span>
        </div>
      </div>

      <nav className={styles.nav}>
        {menuItems.map((item) => {
          const isActive = pathname === item.path;
          return (
            <Link 
              key={item.path} 
              href={item.path}
              className={`${styles.navItem} ${isActive ? styles.active : ""}`}
            >
              <span className={styles.icon}>{item.icon}</span>
              <span className={styles.label}>{item.name}</span>
            </Link>
          );
        })}
      </nav>

      <div className={styles.footer}>
        <Link 
          href="/settings" 
          className={`${styles.navItem} ${pathname === "/settings" ? styles.active : ""}`}
        >
          <span className={styles.icon}><Settings size={20} /></span>
          <span className={styles.label}>Settings</span>
        </Link>
      </div>
    </aside>
  );
};

export default Sidebar;
