import axios from 'axios';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://127.0.0.1:8080/api';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Lab-related API calls
export const fetchLabs = async (params?: { 
  limit?: number; 
  offset?: number; 
  country?: string; 
  focus_area?: string; 
}) => {
  const response = await api.get('/labs', { params });
  return response.data.data || response.data;
};

export const fetchLabById = async (id: number) => {
  const response = await api.get(`/labs/${id}`);
  return response.data;
};

// Paper-related API calls
export const fetchPapers = async (params?: { 
  limit?: number; 
  offset?: number; 
  lab_id?: number; 
  year?: number; 
}) => {
  const response = await api.get('/papers', { params });
  return response.data.data || response.data;
};

// Trend-related API calls
export const fetchTrends = async (params?: { 
  limit?: number; 
  timeframe?: string; 
}) => {
  const response = await api.get('/trends', { params });
  return response.data.data || response.data;
};

// Statistics API calls
export const fetchLabStats = async () => {
  const response = await api.get('/labs/stats');
  return response.data;
};

export const fetchPaperStats = async () => {
  const response = await api.get('/papers/stats');
  return response.data;
};

// Error handling wrapper
export const handleApiError = (error: any) => {
  if (error.response) {
    // Server responded with error
    console.error('API Error:', error.response.data);
    throw new Error(error.response.data.message || 'API request failed');
  } else if (error.request) {
    // Network error
    console.error('Network Error:', error.request);
    throw new Error('Network error - please check your connection');
  } else {
    // Other error
    console.error('Error:', error.message);
    throw new Error(error.message);
  }
};

export default api;