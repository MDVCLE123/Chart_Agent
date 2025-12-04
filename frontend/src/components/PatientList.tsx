/**
 * Patient List Component
 * Displays the provider's daily patient list with FHIR source selector and practitioner filter
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
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  SelectChangeEvent,
  TextField,
  InputAdornment,
  Divider,
} from '@mui/material';
import SearchIcon from '@mui/icons-material/Search';
import StorageIcon from '@mui/icons-material/Storage';
import { apiService } from '../services/api';
import { PatientBasic, PractitionerBasic, FHIRSource } from '../types';

interface PatientListProps {
  onPatientSelect: (patientId: string) => void;
  selectedPatientId?: string;
  fhirSource: FHIRSource;
  onFhirSourceChange: (source: FHIRSource) => void;
}

// FHIR source options with display info
const FHIR_SOURCE_OPTIONS = [
  { id: 'healthlake' as FHIRSource, name: 'AWS HealthLake', icon: '☁️' },
  { id: 'epic' as FHIRSource, name: 'Epic Sandbox', icon: '🏥' },
  { id: 'athena' as FHIRSource, name: 'athenahealth Sandbox', icon: '💚' },
];

export const PatientList: React.FC<PatientListProps> = ({
  onPatientSelect,
  selectedPatientId,
  fhirSource,
  onFhirSourceChange,
}) => {
  const [patients, setPatients] = useState<PatientBasic[]>([]);
  const [practitioners, setPractitioners] = useState<PractitionerBasic[]>([]);
  const [selectedPractitioner, setSelectedPractitioner] = useState<string>('');
  const [searchTerm, setSearchTerm] = useState<string>('');
  const [loading, setLoading] = useState(true);
  const [loadingPractitioners, setLoadingPractitioners] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Filter patients by search term
  const filteredPatients = patients.filter((patient) =>
    patient.name.toLowerCase().includes(searchTerm.toLowerCase())
  );

  // Load data when fhirSource changes
  useEffect(() => {
    setSelectedPractitioner('');
    setSearchTerm('');
    loadPractitioners();
    loadPatients();
  }, [fhirSource]);

  useEffect(() => {
    loadPatients(selectedPractitioner || undefined);
  }, [selectedPractitioner]);

  const loadPractitioners = async () => {
    try {
      setLoadingPractitioners(true);
      const data = await apiService.getPractitioners(100, fhirSource);
      setPractitioners(data);
    } catch (err: any) {
      console.error('Failed to load practitioners:', err);
      setPractitioners([]);
    } finally {
      setLoadingPractitioners(false);
    }
  };

  const loadPatients = async (practitionerId?: string) => {
    try {
      setLoading(true);
      setError(null);
      const data = await apiService.getPatients(50, practitionerId, fhirSource);
      setPatients(data);
    } catch (err: any) {
      setError(err.message || 'Failed to load patients');
    } finally {
      setLoading(false);
    }
  };

  const handleFhirSourceChange = (event: SelectChangeEvent) => {
    onFhirSourceChange(event.target.value as FHIRSource);
  };

  const handlePractitionerChange = (event: SelectChangeEvent) => {
    setSelectedPractitioner(event.target.value);
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
        {/* FHIR Data Source Selector */}
        <FormControl fullWidth size="small" sx={{ mb: 2 }}>
          <InputLabel id="fhir-source-label">Data Source</InputLabel>
          <Select
            labelId="fhir-source-label"
            id="fhir-source-select"
            value={fhirSource}
            label="Data Source"
            onChange={handleFhirSourceChange}
            startAdornment={
              <InputAdornment position="start">
                <StorageIcon fontSize="small" />
              </InputAdornment>
            }
          >
            {FHIR_SOURCE_OPTIONS.map((option) => (
              <MenuItem key={option.id} value={option.id}>
                {option.icon} {option.name}
              </MenuItem>
            ))}
          </Select>
        </FormControl>

        <Divider sx={{ my: 2 }} />

        {/* Practitioner Dropdown */}
        <FormControl fullWidth size="small" sx={{ mb: 2 }}>
          <InputLabel id="practitioner-select-label">Filter by Practitioner</InputLabel>
          <Select
            labelId="practitioner-select-label"
            id="practitioner-select"
            value={selectedPractitioner}
            label="Filter by Practitioner"
            onChange={handlePractitionerChange}
            disabled={loadingPractitioners}
          >
            <MenuItem value="">
              <em>All Practitioners</em>
            </MenuItem>
            {practitioners.map((practitioner) => (
              <MenuItem key={practitioner.id} value={practitioner.id}>
                {practitioner.prefix ? `${practitioner.prefix} ` : ''}{practitioner.name}
                {practitioner.specialty && ` (${practitioner.specialty})`}
              </MenuItem>
            ))}
          </Select>
        </FormControl>

        {/* Patient Search Box */}
        <TextField
          fullWidth
          size="small"
          placeholder="Search patients by name..."
          value={searchTerm}
          onChange={(e) => setSearchTerm(e.target.value)}
          sx={{ mb: 2 }}
          InputProps={{
            startAdornment: (
              <InputAdornment position="start">
                <SearchIcon color="action" />
              </InputAdornment>
            ),
          }}
        />

        <Box display="flex" justifyContent="space-between" alignItems="center" mb={2}>
          <Typography variant="h6">Today's Patients</Typography>
          <Chip 
            label={searchTerm ? `${filteredPatients.length} of ${patients.length}` : `${patients.length} patients`} 
            color="primary" 
            size="small" 
          />
        </Box>

        {loading ? (
          <Box display="flex" justifyContent="center" alignItems="center" minHeight={100}>
            <CircularProgress size={24} />
          </Box>
        ) : filteredPatients.length === 0 ? (
          <Typography color="text.secondary" align="center">
            {searchTerm
              ? `No patients matching "${searchTerm}"`
              : selectedPractitioner 
                ? 'No patients attributed to this practitioner'
                : 'No patients scheduled for today'}
          </Typography>
        ) : (
          <List sx={{ maxHeight: 500, overflow: 'auto' }}>
            {filteredPatients.map((patient) => (
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

