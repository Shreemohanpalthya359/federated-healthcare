import axios from 'axios';

const API_BASE_URL = '/api/v1';

const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Add request interceptor for loading states
api.interceptors.request.use(
  (config) => {
    // Add auth token if exists
    const token = localStorage.getItem('token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Add response interceptor for error handling
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response) {
      // Server responded with error
      const { status, data } = error.response;
      
      if (status === 401) {
        // Handle unauthorized
        localStorage.removeItem('token');
        window.location.href = '/login';
      }
      
      throw {
        message: data.message || `HTTP Error ${status}`,
        status,
        data
      };
    } else if (error.request) {
      // Request made but no response
      throw {
        message: 'Network error. Please check your connection.',
        status: 0
      };
    } else {
      // Something else happened
      throw {
        message: error.message || 'An unexpected error occurred',
        status: 500
      };
    }
  }
);

export const healthApi = {
  checkHealth: () => api.get('/health'),
};

export const modelsApi = {
  listModels: () => api.get('/models'),
  getModelStatus: () => api.get('/model_status'),
};

export const predictApi = {
  makePrediction: (data) => api.post('/predict', data),
  batchPredict: (data) => api.post('/batch_predict', data),
};

export const driftApi = {
  getDriftHistory: (patientId) => api.get(`/drift/history/${patientId}`),
  getPatientCategory: (patientId) => api.get(`/drift/category/${patientId}`),
};

// Real-time WebSocket connection for live monitoring
export const createWebSocket = (patientId) => {
  const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
  const host = window.location.host;
  return new WebSocket(`${protocol}//${host}/ws/monitor/${patientId}`);
};

export default api;