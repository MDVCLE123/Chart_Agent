/**
 * Authentication Service
 * Handles login, logout, and token management
 */
import axios from 'axios';
import { config } from '../config';

export interface AuthUser {
  username: string;
  full_name: string | null;
  email: string | null;
  role: string;
}

export interface LoginResponse {
  access_token: string;
  token_type: string;
  expires_in: number;
  user: AuthUser;
}

const authApi = axios.create({
  baseURL: config.apiUrl,
  timeout: config.apiTimeout,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Add auth header interceptor
authApi.interceptors.request.use((config) => {
  const token = localStorage.getItem('auth_token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

export const authService = {
  /**
   * Login with username and password
   */
  async login(username: string, password: string): Promise<LoginResponse> {
    const response = await authApi.post('/api/auth/login', { username, password });
    return response.data;
  },

  /**
   * Verify current token is valid
   */
  async verifyToken(): Promise<{ valid: boolean; username: string }> {
    const response = await authApi.post('/api/auth/verify');
    return response.data;
  },

  /**
   * Get current user info
   */
  async getCurrentUser(): Promise<AuthUser> {
    const response = await authApi.get('/api/auth/me');
    return response.data;
  },
};

