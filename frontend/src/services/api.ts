/**
 * API service for backend communication
 */
import axios from 'axios';
import { config } from '../config';
import { PatientBasic, PatientData, SummaryResponse, ChatMessage, ChatResponse, PractitionerBasic, FHIRSource, FHIRSourceOption } from '../types';

const api = axios.create({
  baseURL: config.apiUrl,
  timeout: config.apiTimeout,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Add auth token interceptor - includes JWT in all requests
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('auth_token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Handle 401 responses - redirect to login if token is invalid
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      // Clear stored auth data and reload to trigger login
      localStorage.removeItem('auth_token');
      localStorage.removeItem('auth_user');
      window.location.reload();
    }
    return Promise.reject(error);
  }
);

// Helper to add fhir_source to URL params
const addFhirSource = (url: string, fhirSource?: FHIRSource): string => {
  if (fhirSource) {
    const separator = url.includes('?') ? '&' : '?';
    return `${url}${separator}fhir_source=${fhirSource}`;
  }
  return url;
};

export const apiService = {
  /**
   * Get available FHIR sources
   */
  async getFhirSources(): Promise<{ sources: FHIRSourceOption[]; default: FHIRSource }> {
    const response = await api.get('/api/fhir-sources');
    return response.data;
  },

  /**
   * Get list of practitioners
   */
  async getPractitioners(count: number = 50, fhirSource?: FHIRSource): Promise<PractitionerBasic[]> {
    const url = addFhirSource(`/api/practitioners?count=${count}`, fhirSource);
    const response = await api.get(url);
    return response.data.practitioners;
  },

  /**
   * Get list of patients, optionally filtered by practitioner
   */
  async getPatients(count: number = 50, practitionerId?: string, fhirSource?: FHIRSource): Promise<PatientBasic[]> {
    let url = `/api/patients?count=${count}`;
    if (practitionerId) {
      url += `&practitioner_id=${practitionerId}`;
    }
    url = addFhirSource(url, fhirSource);
    const response = await api.get(url);
    return response.data.patients;
  },

  /**
   * Get patient data
   */
  async getPatientData(patientId: string, fhirSource?: FHIRSource): Promise<PatientData> {
    const url = addFhirSource(`/api/patients/${patientId}`, fhirSource);
    const response = await api.get(url);
    return response.data;
  },

  /**
   * Generate summary for patient
   */
  async generateSummary(patientId: string, fhirSource?: FHIRSource): Promise<SummaryResponse> {
    const url = addFhirSource(`/api/patients/${patientId}/summary`, fhirSource);
    const response = await api.post(url);
    return response.data;
  },

  /**
   * Ask question about patient
   */
  async askQuestion(
    patientId: string,
    question: string,
    conversationHistory: ChatMessage[] = [],
    fhirSource?: FHIRSource
  ): Promise<ChatResponse> {
    const url = addFhirSource(`/api/patients/${patientId}/chat`, fhirSource);
    const response = await api.post(url, {
      patient_id: patientId,
      question,
      conversation_history: conversationHistory,
    });
    return response.data;
  },

  /**
   * Health check
   */
  async healthCheck(): Promise<any> {
    const response = await api.get('/api/health');
    return response.data;
  },
};

