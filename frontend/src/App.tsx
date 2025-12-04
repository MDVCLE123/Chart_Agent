/**
 * Main App Component
 */
import React, { useState } from 'react';
import {
  Box,
  Container,
  CssBaseline,
  ThemeProvider,
  createTheme,
  AppBar,
  Toolbar,
  Typography,
  Grid,
  IconButton,
  Tooltip,
  Chip,
  CircularProgress,
} from '@mui/material';
import { LocalHospital, Logout, Person } from '@mui/icons-material';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { PatientList } from './components/PatientList';
import { PatientSummary } from './components/PatientSummary';
import { ChatInterface } from './components/ChatInterface';
import { LoginScreen } from './components/LoginScreen';
import { AuthProvider, useAuth } from './context/AuthContext';
import { FHIRSource } from './types';

// Create MUI theme with DM Sans font
const theme = createTheme({
  palette: {
    primary: {
      main: '#1976d2',
    },
    secondary: {
      main: '#dc004e',
    },
  },
  typography: {
    fontFamily: [
      '"DM Sans"',
      '-apple-system',
      'BlinkMacSystemFont',
      '"Segoe UI"',
      'Roboto',
      '"Helvetica Neue"',
      'Arial',
      'sans-serif',
    ].join(','),
  },
});

// Create React Query client
const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      refetchOnWindowFocus: false,
      retry: 1,
    },
  },
});

// Main app content (shown when authenticated)
const AppContent: React.FC = () => {
  const { user, logout } = useAuth();
  const [selectedPatientId, setSelectedPatientId] = useState<string | null>(null);
  const [selectedPatientName, setSelectedPatientName] = useState<string>('');
  const [fhirSource, setFhirSource] = useState<FHIRSource>('healthlake');

  const handlePatientSelect = (patientId: string, patientName?: string) => {
    setSelectedPatientId(patientId);
    setSelectedPatientName(patientName || '');
  };

  const handleFhirSourceChange = (source: FHIRSource) => {
    setFhirSource(source);
    // Clear patient selection when source changes
    setSelectedPatientId(null);
    setSelectedPatientName('');
  };

  return (
    <Box sx={{ flexGrow: 1 }}>
      {/* App Bar */}
      <AppBar position="static">
        <Toolbar>
          <LocalHospital sx={{ mr: 2 }} />
          <Typography variant="h6" component="div" sx={{ flexGrow: 1 }}>
            Chart Preparation Agent
          </Typography>
          
          {/* User Info */}
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
            <Chip
              icon={<Person sx={{ fontSize: 18 }} />}
              label={user?.full_name || user?.username}
              size="small"
              sx={{
                backgroundColor: 'rgba(255, 255, 255, 0.15)',
                color: 'white',
                '& .MuiChip-icon': { color: 'white' },
              }}
            />
            <Typography variant="body2" sx={{ opacity: 0.9 }}>
              AI-Powered Healthcare Documentation
            </Typography>
            <Tooltip title="Sign Out">
              <IconButton
                color="inherit"
                onClick={logout}
                sx={{
                  ml: 1,
                  '&:hover': {
                    backgroundColor: 'rgba(255, 255, 255, 0.1)',
                  },
                }}
              >
                <Logout />
              </IconButton>
            </Tooltip>
          </Box>
        </Toolbar>
      </AppBar>

      {/* Main Content */}
      <Container maxWidth="xl" sx={{ mt: 4, mb: 4 }}>
        <Grid container spacing={3}>
          {/* Patient List - Left Sidebar */}
          <Grid item xs={12} md={3}>
            <PatientList
              onPatientSelect={(id) => {
                handlePatientSelect(id, 'Selected Patient');
              }}
              selectedPatientId={selectedPatientId || undefined}
              fhirSource={fhirSource}
              onFhirSourceChange={handleFhirSourceChange}
            />
          </Grid>

          {/* Patient Summary & Chat - Main Area */}
          <Grid item xs={12} md={9}>
            {selectedPatientId ? (
              <Box>
                <PatientSummary patientId={selectedPatientId} fhirSource={fhirSource} />
                <Box mt={3}>
                  <ChatInterface
                    patientId={selectedPatientId}
                    patientName={selectedPatientName}
                    fhirSource={fhirSource}
                  />
                </Box>
              </Box>
            ) : (
              <Box
                display="flex"
                justifyContent="center"
                alignItems="center"
                minHeight={400}
              >
                <Typography variant="h6" color="text.secondary">
                  Select a patient from the list to view their chart
                </Typography>
              </Box>
            )}
          </Grid>
        </Grid>
      </Container>
    </Box>
  );
};

// Auth wrapper component
const AuthWrapper: React.FC = () => {
  const { isAuthenticated, isLoading } = useAuth();

  if (isLoading) {
    return (
      <Box
        sx={{
          minHeight: '100vh',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          background: 'linear-gradient(135deg, #0f172a 0%, #1e293b 50%, #0f172a 100%)',
        }}
      >
        <CircularProgress sx={{ color: '#3b82f6' }} />
      </Box>
    );
  }

  return isAuthenticated ? <AppContent /> : <LoginScreen />;
};

function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <ThemeProvider theme={theme}>
        <CssBaseline />
        <AuthProvider>
          <AuthWrapper />
        </AuthProvider>
      </ThemeProvider>
    </QueryClientProvider>
  );
}

export default App;
