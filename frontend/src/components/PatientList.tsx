/**
 * Patient List Component
 * Displays the provider's daily patient list
 */
import React, { useState, useEffect } from 'react';
import {
  Box,
  Card,
  CardContent,
  Typography,
  List,
  ListItem,
  ListItemButton,
  ListItemText,
  CircularProgress,
  Alert,
  Chip,
} from '@mui/material';
import { apiService } from '../services/api';
import { PatientBasic } from '../types';

interface PatientListProps {
  onPatientSelect: (patientId: string) => void;
  selectedPatientId?: string;
}

export const PatientList: React.FC<PatientListProps> = ({
  onPatientSelect,
  selectedPatientId,
}) => {
  const [patients, setPatients] = useState<PatientBasic[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    loadPatients();
  }, []);

  const loadPatients = async () => {
    try {
      setLoading(true);
      setError(null);
      const data = await apiService.getPatients(50);
      setPatients(data);
    } catch (err: any) {
      setError(err.message || 'Failed to load patients');
    } finally {
      setLoading(false);
    }
  };

  const formatDOB = (dob?: string) => {
    if (!dob) return 'DOB: Unknown';
    const date = new Date(dob);
    return `DOB: ${date.toLocaleDateString()}`;
  };

  if (loading) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight={200}>
        <CircularProgress />
      </Box>
    );
  }

  if (error) {
    return (
      <Alert severity="error" onClose={() => setError(null)}>
        {error}
      </Alert>
    );
  }

  return (
    <Card>
      <CardContent>
        <Box display="flex" justifyContent="space-between" alignItems="center" mb={2}>
          <Typography variant="h6">Today's Patients</Typography>
          <Chip label={`${patients.length} patients`} color="primary" size="small" />
        </Box>

        {patients.length === 0 ? (
          <Typography color="text.secondary" align="center">
            No patients scheduled for today
          </Typography>
        ) : (
          <List>
            {patients.map((patient) => (
              <ListItem key={patient.id} disablePadding>
                <ListItemButton
                  selected={patient.id === selectedPatientId}
                  onClick={() => onPatientSelect(patient.id)}
                >
                  <ListItemText
                    primary={
                      <Typography variant="subtitle1" fontWeight="medium">
                        {patient.name}
                      </Typography>
                    }
                    secondary={
                      <Box>
                        <Typography variant="body2" color="text.secondary">
                          {formatDOB(patient.dob)} • {patient.gender || 'Gender unknown'}
                        </Typography>
                        {patient.mrn && (
                          <Typography variant="body2" color="text.secondary">
                            MRN: {patient.mrn}
                          </Typography>
                        )}
                      </Box>
                    }
                  />
                </ListItemButton>
              </ListItem>
            ))}
          </List>
        )}
      </CardContent>
    </Card>
  );
};

