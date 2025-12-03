/**
 * Patient Summary Component
 * Displays patient data and AI-generated summary
 */
import React, { useState, useEffect } from 'react';
import {
  Box,
  Card,
  CardContent,
  Typography,
  Button,
  CircularProgress,
  Alert,
  Chip,
  Divider,
  Grid,
  Paper,
} from '@mui/material';
import { AutoAwesome, Refresh } from '@mui/icons-material';
import { apiService } from '../services/api';
import { PatientData, SummaryResponse, FHIRSource } from '../types';

interface PatientSummaryProps {
  patientId: string;
  fhirSource?: FHIRSource;
}

export const PatientSummary: React.FC<PatientSummaryProps> = ({ patientId, fhirSource }) => {
  const [patientData, setPatientData] = useState<PatientData | null>(null);
  const [summary, setSummary] = useState<SummaryResponse | null>(null);
  const [loadingData, setLoadingData] = useState(false);
  const [loadingSummary, setLoadingSummary] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (patientId) {
      loadPatientData();
      setSummary(null); // Clear summary when patient or source changes
    }
  }, [patientId, fhirSource]);

  const loadPatientData = async () => {
    try {
      setLoadingData(true);
      setError(null);
      const data = await apiService.getPatientData(patientId, fhirSource);
      setPatientData(data);
    } catch (err: any) {
      setError(err.message || 'Failed to load patient data');
    } finally {
      setLoadingData(false);
    }
  };

  const generateSummary = async () => {
    try {
      setLoadingSummary(true);
      setError(null);
      const result = await apiService.generateSummary(patientId, fhirSource);
      setSummary(result);
    } catch (err: any) {
      setError(err.message || 'Failed to generate summary');
    } finally {
      setLoadingSummary(false);
    }
  };

  if (loadingData) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight={400}>
        <CircularProgress />
      </Box>
    );
  }

  if (error) {
    return <Alert severity="error">{error}</Alert>;
  }

  if (!patientData) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight={400}>
        <Typography color="text.secondary">Select a patient to view details</Typography>
      </Box>
    );
  }

  const { patient, conditions, medications, observations, allergies, encounters } = patientData;

  return (
    <Box>
      {/* Patient Header */}
      <Card sx={{ mb: 2 }}>
        <CardContent>
          <Typography variant="h5" gutterBottom>
            {patient.name}
          </Typography>
          <Box display="flex" gap={2} flexWrap="wrap">
            <Chip label={`DOB: ${patient.dob || 'Unknown'}`} size="small" />
            <Chip label={patient.gender || 'Gender unknown'} size="small" />
            {patient.mrn && <Chip label={`MRN: ${patient.mrn}`} size="small" />}
          </Box>
        </CardContent>
      </Card>

      {/* AI Summary */}
      <Card sx={{ mb: 2 }}>
        <CardContent>
          <Box display="flex" justifyContent="space-between" alignItems="center" mb={2}>
            <Typography variant="h6" display="flex" alignItems="center" gap={1}>
              <AutoAwesome color="primary" />
              AI-Generated Summary
            </Typography>
            <Button
              variant="contained"
              startIcon={loadingSummary ? <CircularProgress size={20} /> : <Refresh />}
              onClick={generateSummary}
              disabled={loadingSummary}
            >
              {summary ? 'Regenerate' : 'Generate Summary'}
            </Button>
          </Box>

          {summary ? (
            <Paper elevation={0} sx={{ p: 2, bgcolor: 'grey.50' }}>
              <Typography variant="body1" whiteSpace="pre-wrap">
                {summary.summary}
              </Typography>
            </Paper>
          ) : (
            <Typography color="text.secondary" align="center">
              Click "Generate Summary" to create an AI-powered chart summary
            </Typography>
          )}
        </CardContent>
      </Card>

      {/* Clinical Data */}
      <Grid container spacing={2}>
        {/* Conditions */}
        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Active Conditions
              </Typography>
              <Divider sx={{ mb: 2 }} />
              {conditions.length === 0 ? (
                <Typography color="text.secondary">No active conditions documented</Typography>
              ) : (
                conditions.map((condition, idx) => (
                  <Box key={idx} mb={1}>
                    <Typography variant="body2" fontWeight="medium">
                      {condition.display}
                    </Typography>
                    <Typography variant="caption" color="text.secondary">
                      Status: {condition.clinical_status || 'Unknown'}
                      {condition.onset_date && ` • Since: ${condition.onset_date.substring(0, 10)}`}
                    </Typography>
                  </Box>
                ))
              )}
            </CardContent>
          </Card>
        </Grid>

        {/* Medications */}
        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Current Medications
              </Typography>
              <Divider sx={{ mb: 2 }} />
              {medications.length === 0 ? (
                <Typography color="text.secondary">No medications documented</Typography>
              ) : (
                medications.map((med, idx) => (
                  <Box key={idx} mb={1}>
                    <Typography variant="body2" fontWeight="medium">
                      {med.display}
                    </Typography>
                    {med.dosage && (
                      <Typography variant="caption" color="text.secondary">
                        {med.dosage}
                      </Typography>
                    )}
                  </Box>
                ))
              )}
            </CardContent>
          </Card>
        </Grid>

        {/* Allergies */}
        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Allergies
              </Typography>
              <Divider sx={{ mb: 2 }} />
              {allergies.length === 0 ? (
                <Typography color="text.secondary">No known allergies</Typography>
              ) : (
                allergies.map((allergy, idx) => (
                  <Box key={idx} mb={1}>
                    <Typography variant="body2" fontWeight="medium" color="error">
                      {allergy.display}
                    </Typography>
                    <Typography variant="caption" color="text.secondary">
                      {allergy.criticality && `Criticality: ${allergy.criticality}`}
                      {allergy.reaction && ` • Reaction: ${allergy.reaction}`}
                    </Typography>
                  </Box>
                ))
              )}
            </CardContent>
          </Card>
        </Grid>

        {/* Recent Labs */}
        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Recent Labs
              </Typography>
              <Divider sx={{ mb: 2 }} />
              {observations.length === 0 ? (
                <Typography color="text.secondary">No recent labs</Typography>
              ) : (
                observations.slice(0, 10).map((obs, idx) => (
                  <Box key={idx} mb={1}>
                    <Typography
                      variant="body2"
                      fontWeight="medium"
                      color={obs.abnormal ? 'error' : 'inherit'}
                    >
                      {obs.display}
                    </Typography>
                    <Typography variant="caption" color="text.secondary">
                      {obs.value} {obs.unit}
                      {obs.date && ` • ${obs.date.substring(0, 10)}`}
                      {obs.abnormal && ' • ABNORMAL'}
                    </Typography>
                  </Box>
                ))
              )}
            </CardContent>
          </Card>
        </Grid>

        {/* Recent Encounters */}
        <Grid item xs={12}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Recent Visits
              </Typography>
              <Divider sx={{ mb: 2 }} />
              {encounters.length === 0 ? (
                <Typography color="text.secondary">No recent visits documented</Typography>
              ) : (
                encounters.slice(0, 5).map((encounter, idx) => (
                  <Box key={idx} mb={1}>
                    <Typography variant="body2" fontWeight="medium">
                      {encounter.date?.substring(0, 10) || 'Date unknown'} - {encounter.type || 'Visit'}
                    </Typography>
                    {encounter.reason && (
                      <Typography variant="caption" color="text.secondary">
                        Reason: {encounter.reason}
                      </Typography>
                    )}
                  </Box>
                ))
              )}
            </CardContent>
          </Card>
        </Grid>
      </Grid>
    </Box>
  );
};

