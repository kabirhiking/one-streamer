import axios from 'axios';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';
const VIDEO_API_BASE_URL = process.env.REACT_APP_VIDEO_API_URL || 'http://localhost:8001';

const api = axios.create({
  baseURL: API_BASE_URL,
});

const videoApi = axios.create({
  baseURL: VIDEO_API_BASE_URL,
});

// Add token to requests
const addAuthToken = (config) => {
  const token = localStorage.getItem('access_token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
};

api.interceptors.request.use(addAuthToken);
videoApi.interceptors.request.use(addAuthToken);

// Handle token refresh
const handleTokenRefresh = async (error) => {
  if (error.response?.status === 401) {
    const refreshToken = localStorage.getItem('refresh_token');
    if (refreshToken) {
      try {
        const response = await axios.post(`${API_BASE_URL}/api/auth/token/refresh/`, {
          refresh: refreshToken
        });
        localStorage.setItem('access_token', response.data.access);
        error.config.headers.Authorization = `Bearer ${response.data.access}`;
        return axios(error.config);
      } catch (refreshError) {
        localStorage.removeItem('access_token');
        localStorage.removeItem('refresh_token');
        window.location.href = '/login';
      }
    }
  }
  return Promise.reject(error);
};

api.interceptors.response.use(
  response => response,
  handleTokenRefresh
);

videoApi.interceptors.response.use(
  response => response,
  handleTokenRefresh
);

export { api, videoApi };
export default api;
