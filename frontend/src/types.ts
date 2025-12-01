/**
 * TypeScript type definitions
 */

export interface PatientBasic {
  id: string;
  name: string;
  mrn?: string;
  dob?: string;
  gender?: string;
  appointment_time?: string;
}

export interface Condition {
  code: string;
  display: string;
  clinical_status?: string;
  onset_date?: string;
}

export interface Medication {
  code: string;
  display: string;
  status?: string;
  dosage?: string;
}

export interface Observation {
  code: string;
  display: string;
  value?: string;
  unit?: string;
  date?: string;
  abnormal?: boolean;
}

export interface Allergy {
  code: string;
  display: string;
  criticality?: string;
  reaction?: string;
}

export interface Encounter {
  id: string;
  type?: string;
  date?: string;
  reason?: string;
  provider?: string;
}

export interface PatientData {
  patient: PatientBasic;
  conditions: Condition[];
  medications: Medication[];
  observations: Observation[];
  allergies: Allergy[];
  encounters: Encounter[];
}

export interface SummaryResponse {
  patient_id: string;
  summary: string;
  generated_at: string;
}

export interface ChatMessage {
  role: 'user' | 'assistant';
  content: string;
}

export interface ChatResponse {
  patient_id: string;
  answer: string;
  conversation_history: ChatMessage[];
}

