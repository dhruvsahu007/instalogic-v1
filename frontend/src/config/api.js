/**
 * API Configuration
 * Reads from environment variables set during build time
 */

// Get API base URL based on environment
// In production, use relative URLs (handled by Nginx proxy)
// In development, use localhost
export const API_BASE_URL = import.meta.env.DEV 
  ? 'http://localhost:8000'
  : '';  // Empty string means use relative URLs in production

// Helper function to construct full API URLs
export const getApiUrl = (endpoint) => {
  // Remove leading slash if present to avoid double slashes
  const cleanEndpoint = endpoint.startsWith('/') ? endpoint.slice(1) : endpoint;
  
  // If API_BASE_URL is empty (production), use relative URLs
  if (!API_BASE_URL) {
    return `/${cleanEndpoint}`;
  }
  
  return `${API_BASE_URL}/${cleanEndpoint}`;
};

// Export for easy use
export default {
  API_BASE_URL,
  getApiUrl
};

