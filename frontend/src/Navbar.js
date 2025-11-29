import React from 'react';
import { Link, useLocation } from 'react-router-dom';
import { SignedIn, SignedOut, SignInButton, UserButton } from '@clerk/clerk-react';

const Navbar = () => {
  const location = useLocation();

  const isActive = (path) => {
    return location.pathname === path;
  };

  return (
    <nav className="bg-white shadow-lg border-b border-secondary-200">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between h-16">
          {/* Left: Logo */}
          <div className="flex items-center">
            <Link to="/" className="flex items-center space-x-3">
              <div className="w-10 h-10 bg-gradient-to-br from-blue-600 to-purple-600 rounded-xl flex items-center justify-center shadow-lg">
                <span className="text-white font-bold text-lg">AW</span>
              </div>
              <div className="flex flex-col">
                <span className="text-xl font-bold text-secondary-800 leading-tight">
                  AdmitWise AI
                </span>
                <span className="text-xs text-secondary-500 -mt-1">
                  College Admission Assistant
                </span>
              </div>
            </Link>
          </div>

          {/* Right: Navigation Links + Auth */}
          <div className="flex items-center space-x-8">
            <Link
              to="/"
              className={`px-3 py-2 rounded-md text-sm font-medium transition-colors ${
                isActive('/')
                  ? 'text-primary-600 bg-primary-50'
                  : 'text-secondary-600 hover:text-secondary-900 hover:bg-secondary-50'
              }`}
            >
              Upload
            </Link>
          <SignedIn>
            <Link
              to="/form"
              className={`px-3 py-2 rounded-md text-sm font-medium transition-colors ${
                isActive('/form')
                  ? 'text-primary-600 bg-primary-50'
                  : 'text-secondary-600 hover:text-secondary-900 hover:bg-secondary-50'
              }`}
            >
              Preferences
            </Link>
            <Link
              to="/results"
              className={`px-3 py-2 rounded-md text-sm font-medium transition-colors ${
                isActive('/results')
                  ? 'text-primary-600 bg-primary-50'
                  : 'text-secondary-600 hover:text-secondary-900 hover:bg-secondary-50'
              }`}
            >
              Results
            </Link>
          </SignedIn>
            {/* Clerk Authentication */}
            <SignedOut>
              <SignInButton mode="modal">
                <button className="px-4 py-2 bg-primary-600 text-white rounded-md hover:bg-primary-700 transition">
                  Sign In
                </button>
              </SignInButton>
            </SignedOut>

            <SignedIn>
              <UserButton afterSignOutUrl="/" />
            </SignedIn>
          </div>
        </div>
      </div>
    </nav>
  );
};

export default Navbar;
