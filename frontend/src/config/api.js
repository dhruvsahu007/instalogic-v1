/**
 * API Configuration
 * Reads from environment variables set during build time
 */

// Get API base URL from environment variable
// Defaults to localhost for development if not set
export const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

// Helper function to construct full API URLs
export const getApiUrl = (endpoint) => {
  // Remove leading slash if present to avoid double slashes
  const cleanEndpoint = endpoint.startsWith('/') ? endpoint.slice(1) : endpoint;
  return `${API_BASE_URL}/${cleanEndpoint}`;
};

// Export for easy use
export default {
  API_BASE_URL,
  getApiUrl
};

