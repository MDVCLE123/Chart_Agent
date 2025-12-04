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
  allowed_data_sources: string[];
  practitioner_id: string | null;
  practitioner_name: string | null;
}

export interface LoginResponse {
  access_token: string;
  token_type: string;
  expires_in: number;
  user: AuthUser;
}

export interface UserCreate {
  username: string;
  password: string;
  email?: string;
  full_name?: string;
  role: string;
  allowed_data_sources: string[];
  practitioner_id?: string;
  practitioner_name?: string;
}

export interface UserUpdate {
  email?: string;
  full_name?: string;
  password?: string;
  disabled?: boolean;
  role?: string;
  allowed_data_sources?: string[];
  practitioner_id?: string;
  practitioner_name?: string;
}

export interface UserResponse {
  username: string;
  email: string | null;
  full_name: string | null;
  disabled: boolean;
  role: string;
  allowed_data_sources: string[];
  practitioner_id: string | null;
  practitioner_name: string | null;
}

export interface DataSourceOption {
  id: string;
  name: string;
  icon: string;
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

  // ============== Admin User Management ==============

  /**
   * Get all users (admin only)
   */
  async getAllUsers(): Promise<UserResponse[]> {
    const response = await authApi.get('/api/admin/users');
    return response.data;
  },

  /**
   * Create a new user (admin only)
   */
  async createUser(userData: UserCreate): Promise<UserResponse> {
    const response = await authApi.post('/api/admin/users', userData);
    return response.data;
  },

  /**
   * Update a user (admin only)
   */
  async updateUser(username: string, userData: UserUpdate): Promise<UserResponse> {
    const response = await authApi.put(`/api/admin/users/${username}`, userData);
    return response.data;
  },

  /**
   * Delete a user (admin only)
   */
  async deleteUser(username: string): Promise<void> {
    await authApi.delete(`/api/admin/users/${username}`);
  },

  /**
   * Get available data sources (admin only)
   */
  async getAvailableDataSources(): Promise<{ sources: DataSourceOption[] }> {
    const response = await authApi.get('/api/admin/data-sources');
    return response.data;
  },
};

