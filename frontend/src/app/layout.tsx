import type { Metadata } from "next";
import "./globals.css";
import { AppProvider } from "../context/AppContext";
import Sidebar from "../components/Sidebar";
import Header from "../components/Header";

export const metadata: Metadata = {
  title: "AI Career CoPilot - Premium Job Application Matcher & Automation",
  description: "Automate your job discovery, calculate advanced matching scores against resumes, perform target company research, find decision-makers, and draft custom cold emails.",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body>
        <AppProvider>
          <div className="app-layout">
            <Sidebar />
            <main className="main-content">
              <Header />
              <div className="page-view animate-slideup">
                {children}
              </div>
            </main>
          </div>
        </AppProvider>
      </body>
    </html>
  );
}
