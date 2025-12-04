/**
 * Login Screen Component
 * Beautiful, modern login interface for Chart Preparation Agent
 */
import React, { useState } from 'react';
import {
  Box,
  Card,
  CardContent,
  TextField,
  Button,
  Typography,
  Alert,
  InputAdornment,
  IconButton,
  CircularProgress,
  Fade,
} from '@mui/material';
import {
  Visibility,
  VisibilityOff,
  LocalHospital,
  Person,
  Lock,
} from '@mui/icons-material';
import { useAuth } from '../context/AuthContext';

export const LoginScreen: React.FC = () => {
  const { login, isLoading, error } = useAuth();
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const [localError, setLocalError] = useState<string | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLocalError(null);

    if (!username.trim() || !password.trim()) {
      setLocalError('Please enter both username and password');
      return;
    }

    try {
      await login(username, password);
    } catch (err: any) {
      setLocalError(err.message);
    }
  };

  return (
    <Box
      sx={{
        minHeight: '100vh',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        background: 'linear-gradient(135deg, #0f172a 0%, #1e293b 50%, #0f172a 100%)',
        position: 'relative',
        overflow: 'hidden',
      }}
    >
      {/* Animated background elements */}
      <Box
        sx={{
          position: 'absolute',
          top: '10%',
          left: '5%',
          width: 300,
          height: 300,
          borderRadius: '50%',
          background: 'radial-gradient(circle, rgba(59, 130, 246, 0.15) 0%, transparent 70%)',
          filter: 'blur(40px)',
          animation: 'float 8s ease-in-out infinite',
          '@keyframes float': {
            '0%, 100%': { transform: 'translateY(0px) rotate(0deg)' },
            '50%': { transform: 'translateY(-20px) rotate(5deg)' },
          },
        }}
      />
      <Box
        sx={{
          position: 'absolute',
          bottom: '15%',
          right: '10%',
          width: 400,
          height: 400,
          borderRadius: '50%',
          background: 'radial-gradient(circle, rgba(16, 185, 129, 0.12) 0%, transparent 70%)',
          filter: 'blur(50px)',
          animation: 'float2 10s ease-in-out infinite',
          '@keyframes float2': {
            '0%, 100%': { transform: 'translateY(0px) rotate(0deg)' },
            '50%': { transform: 'translateY(30px) rotate(-5deg)' },
          },
        }}
      />

      {/* Grid pattern overlay */}
      <Box
        sx={{
          position: 'absolute',
          inset: 0,
          backgroundImage: `
            linear-gradient(rgba(59, 130, 246, 0.03) 1px, transparent 1px),
            linear-gradient(90deg, rgba(59, 130, 246, 0.03) 1px, transparent 1px)
          `,
          backgroundSize: '50px 50px',
        }}
      />

      <Fade in timeout={800}>
        <Card
          sx={{
            maxWidth: 420,
            width: '100%',
            mx: 2,
            background: 'rgba(30, 41, 59, 0.85)',
            backdropFilter: 'blur(20px)',
            border: '1px solid rgba(71, 85, 105, 0.5)',
            borderRadius: 3,
            boxShadow: '0 25px 50px -12px rgba(0, 0, 0, 0.5)',
          }}
        >
          <CardContent sx={{ p: 4 }}>
            {/* Logo and Title */}
            <Box sx={{ textAlign: 'center', mb: 4 }}>
              <Box
                sx={{
                  display: 'inline-flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  width: 64,
                  height: 64,
                  borderRadius: 2,
                  background: 'linear-gradient(135deg, #3b82f6 0%, #1d4ed8 100%)',
                  mb: 2,
                  boxShadow: '0 10px 30px rgba(59, 130, 246, 0.3)',
                }}
              >
                <LocalHospital sx={{ fontSize: 32, color: 'white' }} />
              </Box>
              <Typography
                variant="h4"
                sx={{
                  fontWeight: 700,
                  color: '#f1f5f9',
                  fontFamily: '"DM Sans", -apple-system, sans-serif',
                  letterSpacing: '-0.02em',
                }}
              >
                Chart Agent
              </Typography>
              <Typography
                variant="body2"
                sx={{
                  color: '#94a3b8',
                  mt: 1,
                  fontFamily: '"DM Sans", -apple-system, sans-serif',
                }}
              >
                AI-Powered Healthcare Documentation
              </Typography>
            </Box>

            {/* Error Alert */}
            {(localError || error) && (
              <Alert
                severity="error"
                sx={{
                  mb: 3,
                  backgroundColor: 'rgba(239, 68, 68, 0.1)',
                  border: '1px solid rgba(239, 68, 68, 0.3)',
                  color: '#fca5a5',
                  '& .MuiAlert-icon': { color: '#f87171' },
                }}
              >
                {localError || error}
              </Alert>
            )}

            {/* Login Form */}
            <form onSubmit={handleSubmit}>
              <TextField
                fullWidth
                label="Username"
                variant="outlined"
                value={username}
                onChange={(e) => setUsername(e.target.value)}
                disabled={isLoading}
                InputProps={{
                  startAdornment: (
                    <InputAdornment position="start">
                      <Person sx={{ color: '#64748b' }} />
                    </InputAdornment>
                  ),
                }}
                sx={{
                  mb: 2.5,
                  '& .MuiOutlinedInput-root': {
                    backgroundColor: 'rgba(15, 23, 42, 0.6)',
                    borderRadius: 2,
                    '& fieldset': {
                      borderColor: 'rgba(71, 85, 105, 0.5)',
                    },
                    '&:hover fieldset': {
                      borderColor: 'rgba(100, 116, 139, 0.7)',
                    },
                    '&.Mui-focused fieldset': {
                      borderColor: '#3b82f6',
                    },
                  },
                  '& .MuiInputLabel-root': {
                    color: '#64748b',
                    '&.Mui-focused': {
                      color: '#3b82f6',
                    },
                  },
                  '& .MuiInputBase-input': {
                    color: '#e2e8f0',
                  },
                }}
              />

              <TextField
                fullWidth
                label="Password"
                type={showPassword ? 'text' : 'password'}
                variant="outlined"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                disabled={isLoading}
                InputProps={{
                  startAdornment: (
                    <InputAdornment position="start">
                      <Lock sx={{ color: '#64748b' }} />
                    </InputAdornment>
                  ),
                  endAdornment: (
                    <InputAdornment position="end">
                      <IconButton
                        onClick={() => setShowPassword(!showPassword)}
                        edge="end"
                        sx={{ color: '#64748b' }}
                      >
                        {showPassword ? <VisibilityOff /> : <Visibility />}
                      </IconButton>
                    </InputAdornment>
                  ),
                }}
                sx={{
                  mb: 3,
                  '& .MuiOutlinedInput-root': {
                    backgroundColor: 'rgba(15, 23, 42, 0.6)',
                    borderRadius: 2,
                    '& fieldset': {
                      borderColor: 'rgba(71, 85, 105, 0.5)',
                    },
                    '&:hover fieldset': {
                      borderColor: 'rgba(100, 116, 139, 0.7)',
                    },
                    '&.Mui-focused fieldset': {
                      borderColor: '#3b82f6',
                    },
                  },
                  '& .MuiInputLabel-root': {
                    color: '#64748b',
                    '&.Mui-focused': {
                      color: '#3b82f6',
                    },
                  },
                  '& .MuiInputBase-input': {
                    color: '#e2e8f0',
                  },
                }}
              />

              <Button
                type="submit"
                fullWidth
                variant="contained"
                disabled={isLoading}
                sx={{
                  py: 1.5,
                  borderRadius: 2,
                  background: 'linear-gradient(135deg, #3b82f6 0%, #1d4ed8 100%)',
                  fontWeight: 600,
                  fontSize: '1rem',
                  textTransform: 'none',
                  fontFamily: '"DM Sans", -apple-system, sans-serif',
                  boxShadow: '0 10px 30px rgba(59, 130, 246, 0.3)',
                  '&:hover': {
                    background: 'linear-gradient(135deg, #2563eb 0%, #1e40af 100%)',
                    boxShadow: '0 15px 35px rgba(59, 130, 246, 0.4)',
                  },
                  '&.Mui-disabled': {
                    background: 'rgba(71, 85, 105, 0.5)',
                  },
                }}
              >
                {isLoading ? (
                  <CircularProgress size={24} sx={{ color: 'white' }} />
                ) : (
                  'Sign In'
                )}
              </Button>
            </form>

            {/* Footer */}
            <Box sx={{ mt: 4, textAlign: 'center' }}>
              <Typography
                variant="caption"
                sx={{
                  color: '#64748b',
                  display: 'block',
                  fontFamily: '"DM Sans", -apple-system, sans-serif',
                }}
              >
                Protected Health Information (PHI) Access
              </Typography>
              <Typography
                variant="caption"
                sx={{
                  color: '#475569',
                  display: 'block',
                  mt: 0.5,
                  fontFamily: '"DM Sans", -apple-system, sans-serif',
                }}
              >
                Authorized users only • Activity monitored
              </Typography>
            </Box>
          </CardContent>
        </Card>
      </Fade>
    </Box>
  );
};

