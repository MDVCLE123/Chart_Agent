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
} from '@mui/material';
import { LocalHospital } from '@mui/icons-material';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { PatientList } from './components/PatientList';
import { PatientSummary } from './components/PatientSummary';
import { ChatInterface } from './components/ChatInterface';

// Create MUI theme
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

function App() {
  const [selectedPatientId, setSelectedPatientId] = useState<string | null>(null);
  const [selectedPatientName, setSelectedPatientName] = useState<string>('');

  const handlePatientSelect = (patientId: string, patientName?: string) => {
    setSelectedPatientId(patientId);
    setSelectedPatientName(patientName || '');
  };

  return (
    <QueryClientProvider client={queryClient}>
      <ThemeProvider theme={theme}>
        <CssBaseline />
        <Box sx={{ flexGrow: 1 }}>
          {/* App Bar */}
          <AppBar position="static">
            <Toolbar>
              <LocalHospital sx={{ mr: 2 }} />
              <Typography variant="h6" component="div" sx={{ flexGrow: 1 }}>
                Chart Preparation Agent
              </Typography>
              <Typography variant="body2">
                AI-Powered Healthcare Documentation
              </Typography>
            </Toolbar>
          </AppBar>

          {/* Main Content */}
          <Container maxWidth="xl" sx={{ mt: 4, mb: 4 }}>
            <Grid container spacing={3}>
              {/* Patient List - Left Sidebar */}
              <Grid item xs={12} md={3}>
                <PatientList
                  onPatientSelect={(id) => {
                    // In a real app, we'd fetch the patient name here
                    handlePatientSelect(id, 'Selected Patient');
                  }}
                  selectedPatientId={selectedPatientId || undefined}
                />
              </Grid>

              {/* Patient Summary & Chat - Main Area */}
              <Grid item xs={12} md={9}>
                {selectedPatientId ? (
                  <Box>
                    <PatientSummary patientId={selectedPatientId} />
                    <Box mt={3}>
                      <ChatInterface
                        patientId={selectedPatientId}
                        patientName={selectedPatientName}
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
      </ThemeProvider>
    </QueryClientProvider>
  );
}

export default App;

