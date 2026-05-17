import axios from 'axios';
import { toast } from 'react-toastify';

const API_URL = process.env.REACT_APP_API_URL || 'http://10.0.1.20:8000';

const api = axios.create({
  baseURL: API_URL,
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Interceptor para agregar token
api.interceptors.request.use(
  (config) => {
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

// Interceptor para manejar errores
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response) {
      switch (error.response.status) {
        case 401:
          localStorage.removeItem('token');
          window.location.href = '/login';
          toast.error('Sesión expirada. Por favor, inicia sesión nuevamente.');
          break;
        case 403:
          toast.error('No tienes permisos para realizar esta acción.');
          break;
        case 429:
          toast.error('Demasiadas solicitudes. Por favor, espera un momento.');
          break;
        case 500:
          toast.error('Error del servidor. Por favor, intenta más tarde.');
          break;
        default:
          const message = error.response.data?.detail || 'Ha ocurrido un error';
          toast.error(message);
      }
    } else if (error.request) {
      toast.error('No se pudo conectar con el servidor. Verifica tu conexión.');
    }
    return Promise.reject(error);
  }
);

export default api;
