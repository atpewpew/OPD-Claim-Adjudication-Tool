import React from "react";
import { NavLink, Link } from "react-router-dom";
import { Stethoscope } from "lucide-react";

interface LayoutProps {
  children: React.ReactNode;
}

export const Layout: React.FC<LayoutProps> = ({ children }) => {
  return (
    <div className="min-h-screen bg-slate-50 flex flex-col font-sans">
      {/* Sticky Top Navbar */}
      <header className="sticky top-0 z-50 w-full border-b border-slate-200/80 bg-white/90 backdrop-blur-md">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex h-14 items-center justify-between">
            {/* Logo area */}
            <div className="flex items-center">
              <Link
                to="/dashboard"
                className="flex items-center gap-2.5 group focus:outline-none"
              >
                <div className="p-1.5 rounded-lg bg-violet-100 text-violet-600 group-hover:bg-violet-600 group-hover:text-white transition-all duration-300 shadow-sm">
                  <Stethoscope className="h-5 w-5" />
                </div>
                <span className="text-lg font-bold tracking-tight text-slate-900 group-hover:text-violet-600 transition-colors duration-300">
                  Claim<span className="text-violet-600 group-hover:text-slate-900 transition-colors duration-300">IQ</span>
                </span>
              </Link>
            </div>

            {/* Navigation links */}
            <nav className="flex items-center space-x-1 sm:space-x-2">
              <NavLink
                to="/submit"
                className={({ isActive }) =>
                  `px-3 py-1.5 rounded-md text-sm font-medium transition-all duration-200 focus:outline-none focus:ring-2 focus:ring-violet-500/20 ${
                    isActive
                      ? "bg-violet-50 text-violet-700 font-semibold"
                      : "text-slate-600 hover:text-slate-900 hover:bg-slate-100"
                  }`
                }
              >
                Submit Claim
              </NavLink>
              <NavLink
                to="/dashboard"
                className={({ isActive }) =>
                  `px-3 py-1.5 rounded-md text-sm font-medium transition-all duration-200 focus:outline-none focus:ring-2 focus:ring-violet-500/20 ${
                    isActive
                      ? "bg-violet-50 text-violet-700 font-semibold"
                      : "text-slate-600 hover:text-slate-900 hover:bg-slate-100"
                  }`
                }
              >
                Dashboard
              </NavLink>
            </nav>
          </div>
        </div>
      </header>

      {/* Main Content Area */}
      <main className="flex-1 w-full max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6 md:py-8 animate-fadeIn">
        {children}
      </main>
    </div>
  );
};

export default Layout;
