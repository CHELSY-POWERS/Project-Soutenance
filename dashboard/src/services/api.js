// src/services/api.js
// API service for communicating with Flask backend

import axios from 'axios';

// Base API URL - change this if your backend runs on a different port/host
const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:5000/api';

// Create axios instance with default config
const apiClient = axios.create({
  baseURL: API_BASE_URL,
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// API service object
const api = {
  // Health check
  healthCheck: async () => {
    try {
      const response = await apiClient.get('/health');
      return response.data;
    } catch (error) {
      console.error('Health check failed:', error);
      throw error;
    }
  },

  // Get model information
  getModelInfo: async () => {
    try {
      const response = await apiClient.get('/model/info');
      return response.data;
    } catch (error) {
      console.error('Failed to get model info:', error);
      throw error;
    }
  },

  // Get statistics for dashboard
  getStatistics: async () => {
    try {
      const response = await apiClient.get('/statistics');
      return response.data;
    } catch (error) {
      console.error('Failed to get statistics:', error);
      throw error;
    }
  },

  // Get evaluation metrics
  getMetrics: async () => {
    try {
      const response = await apiClient.get('/metrics');
      return response.data;
    } catch (error) {
      console.error('Failed to get metrics:', error);
      throw error;
    }
  },

  // Get detection results with pagination and filtering
  getDetectionResults: async (page = 1, perPage = 20, filter = 'all') => {
    try {
      const response = await apiClient.get('/detection/results', {
        params: { page, per_page: perPage, filter },
      });
      return response.data;
    } catch (error) {
      console.error('Failed to get detection results:', error);
      throw error;
    }
  },

  // Get dashboard summary (all data in one call)
  getDashboardSummary: async () => {
    try {
      const response = await apiClient.get('/dashboard/summary');
      return response.data;
    } catch (error) {
      console.error('Failed to get dashboard summary:', error);
      throw error;
    }
  },

  // Predict on new data
  predict: async (features) => {
    try {
      const response = await apiClient.post('/predict', { features });
      return response.data;
    } catch (error) {
      console.error('Prediction failed:', error);
      throw error;
    }
  },
};

export default api;