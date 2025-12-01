/**
 * API service for backend communication
 */
import axios from 'axios';
import { config } from '../config';
import { PatientBasic, PatientData, SummaryResponse, ChatMessage, ChatResponse } from '../types';

const api = axios.create({
  baseURL: config.apiUrl,
  timeout: config.apiTimeout,
  headers: {
    'Content-Type': 'application/json',
  },
});

export const apiService = {
  /**
   * Get list of patients
   */
  async getPatients(count: number = 50): Promise<PatientBasic[]> {
    const response = await api.get(`/api/patients?count=${count}`);
    return response.data.patients;
  },

  /**
   * Get patient data
   */
  async getPatientData(patientId: string): Promise<PatientData> {
    const response = await api.get(`/api/patients/${patientId}`);
    return response.data;
  },

  /**
   * Generate summary for patient
   */
  async generateSummary(patientId: string): Promise<SummaryResponse> {
    const response = await api.post(`/api/patients/${patientId}/summary`);
    return response.data;
  },

  /**
   * Ask question about patient
   */
  async askQuestion(
    patientId: string,
    question: string,
    conversationHistory: ChatMessage[] = []
  ): Promise<ChatResponse> {
    const response = await api.post(`/api/patients/${patientId}/chat`, {
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

