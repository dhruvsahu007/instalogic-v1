import React from 'react';
import { Link } from 'react-router-dom';

const AdminNav = () => {
  return (
    <nav className="bg-white border-b border-gray-200 shadow-sm">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between items-center h-16">
          <div className="flex items-center space-x-4">
            <Link to="/" className="flex items-center space-x-2">
              <span className="text-xl font-bold text-gray-900">InstaLogic</span>
            </Link>
            <span className="text-sm text-gray-500 px-3 py-1 bg-gray-100 rounded-full">
              Admin Panel
            </span>
          </div>
          <div className="flex items-center space-x-4">
            <Link 
              to="/admin/leads" 
              className="text-gray-700 hover:text-gray-900 px-3 py-2 text-sm font-medium"
            >
              Leads
            </Link>
            <Link 
              to="/" 
              className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 transition-colors text-sm font-medium"
            >
              Back to Site
            </Link>
          </div>
        </div>
      </div>
    </nav>
  );
};

export default AdminNav;
