/**
 * Settings Page Component
 * Admin panel for user management and data source permissions
 */
import React, { useState, useEffect } from 'react';
import {
  Box,
  Paper,
  Typography,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Button,
  IconButton,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Checkbox,
  FormGroup,
  FormControlLabel,
  Chip,
  Alert,
  CircularProgress,
  Autocomplete,
  Tooltip,
  Divider,
} from '@mui/material';
import {
  Add,
  Edit,
  Delete,
  ArrowBack,
  Person,
  AdminPanelSettings,
  Storage,
} from '@mui/icons-material';
import { authService, UserResponse, UserCreate, UserUpdate, DataSourceOption } from '../services/auth';
import { apiService } from '../services/api';
import { PractitionerBasic } from '../types';

interface SettingsPageProps {
  onBack: () => void;
}

const DATA_SOURCES: DataSourceOption[] = [
  { id: 'healthlake', name: 'AWS HealthLake', icon: '☁️' },
  { id: 'epic', name: 'Epic Sandbox', icon: '🏥' },
  { id: 'athena', name: 'athenahealth', icon: '💚' },
];

// Admin user identifier - matches backend protection
const ADMIN_EMAIL = 'admin@chartagent.local';

export const SettingsPage: React.FC<SettingsPageProps> = ({ onBack }) => {
  const [users, setUsers] = useState<UserResponse[]>([]);
  const [practitioners, setPractitioners] = useState<PractitionerBasic[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);

  // Dialog state
  const [dialogOpen, setDialogOpen] = useState(false);
  const [editingUser, setEditingUser] = useState<UserResponse | null>(null);
  const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
  const [userToDelete, setUserToDelete] = useState<string | null>(null);

  // Form state
  const [formData, setFormData] = useState<{
    email: string;
    password: string;
    first_name: string;
    last_name: string;
    role: string;
    allowed_data_sources: string[];
    practitioner_id: string;
    practitioner_name: string;
  }>({
    email: '',
    password: '',
    first_name: '',
    last_name: '',
    role: 'user',
    allowed_data_sources: ['healthlake'],
    practitioner_id: '',
    practitioner_name: '',
  });

  // Load users and practitioners
  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    setLoading(true);
    setError(null);
    try {
      const [usersData, practitionersData] = await Promise.all([
        authService.getAllUsers(),
        apiService.getPractitioners(100, 'healthlake'),
      ]);
      setUsers(usersData);
      setPractitioners(practitionersData);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to load data');
    } finally {
      setLoading(false);
    }
  };

  const handleOpenCreate = () => {
    setEditingUser(null);
    setFormData({
      email: '',
      password: '',
      first_name: '',
      last_name: '',
      role: 'user',
      allowed_data_sources: ['healthlake'],
      practitioner_id: '',
      practitioner_name: '',
    });
    setDialogOpen(true);
  };

  const handleOpenEdit = (user: UserResponse) => {
    setEditingUser(user);
    setFormData({
      email: user.email || user.username || '',
      password: '',
      first_name: user.first_name || '',
      last_name: user.last_name || '',
      role: user.role,
      allowed_data_sources: user.allowed_data_sources,
      practitioner_id: user.practitioner_id || '',
      practitioner_name: user.practitioner_name || '',
    });
    setDialogOpen(true);
  };

  const handleCloseDialog = () => {
    setDialogOpen(false);
    setEditingUser(null);
  };

  const handleSave = async () => {
    setError(null);
    try {
      if (editingUser) {
        // Update existing user
        const updateData: UserUpdate = {
          email: formData.email || undefined,
          first_name: formData.first_name || undefined,
          last_name: formData.last_name || undefined,
          role: formData.role,
          allowed_data_sources: formData.allowed_data_sources,
          practitioner_id: formData.practitioner_id || undefined,
          practitioner_name: formData.practitioner_name || undefined,
        };
        if (formData.password) {
          updateData.password = formData.password;
        }
        await authService.updateUser(editingUser.username, updateData);
        setSuccess(`User "${formData.email}" updated successfully`);
      } else {
        // Create new user
        if (!formData.email || !formData.password) {
          setError('Email and password are required');
          return;
        }
        const createData: UserCreate = {
          email: formData.email,
          password: formData.password,
          first_name: formData.first_name || undefined,
          last_name: formData.last_name || undefined,
          role: formData.role,
          allowed_data_sources: formData.allowed_data_sources,
          practitioner_id: formData.practitioner_id || undefined,
          practitioner_name: formData.practitioner_name || undefined,
        };
        await authService.createUser(createData);
        setSuccess(`User "${formData.email}" created successfully`);
      }
      handleCloseDialog();
      loadData();
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to save user');
    }
  };

  const handleDeleteConfirm = async () => {
    if (!userToDelete) return;
    try {
      await authService.deleteUser(userToDelete);
      setSuccess(`User "${userToDelete}" deleted successfully`);
      setDeleteDialogOpen(false);
      setUserToDelete(null);
      loadData();
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to delete user');
    }
  };

  const handleDataSourceToggle = (sourceId: string) => {
    setFormData((prev) => ({
      ...prev,
      allowed_data_sources: prev.allowed_data_sources.includes(sourceId)
        ? prev.allowed_data_sources.filter((s) => s !== sourceId)
        : [...prev.allowed_data_sources, sourceId],
    }));
  };

  const handlePractitionerSelect = (practitioner: PractitionerBasic | null) => {
    setFormData((prev) => ({
      ...prev,
      practitioner_id: practitioner?.id || '',
      practitioner_name: practitioner?.name || '',
    }));
  };

  if (loading) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight={400}>
        <CircularProgress />
      </Box>
    );
  }

  return (
    <Box>
      {/* Header */}
      <Box display="flex" alignItems="center" mb={3}>
        <IconButton onClick={onBack} sx={{ mr: 2 }}>
          <ArrowBack />
        </IconButton>
        <Typography variant="h5" fontWeight={600}>
          Settings
        </Typography>
      </Box>

      {/* Alerts */}
      {error && (
        <Alert severity="error" sx={{ mb: 2 }} onClose={() => setError(null)}>
          {error}
        </Alert>
      )}
      {success && (
        <Alert severity="success" sx={{ mb: 2 }} onClose={() => setSuccess(null)}>
          {success}
        </Alert>
      )}

      {/* User Management Section */}
      <Paper sx={{ p: 3 }}>
        <Box display="flex" justifyContent="space-between" alignItems="center" mb={3}>
          <Box display="flex" alignItems="center" gap={1}>
            <AdminPanelSettings color="primary" />
            <Typography variant="h6">User Management</Typography>
          </Box>
          <Button
            variant="contained"
            startIcon={<Add />}
            onClick={handleOpenCreate}
          >
            Add User
          </Button>
        </Box>

        <TableContainer>
          <Table>
            <TableHead>
              <TableRow>
                <TableCell>Username</TableCell>
                <TableCell>Full Name</TableCell>
                <TableCell>Email</TableCell>
                <TableCell>Role</TableCell>
                <TableCell>Data Sources</TableCell>
                <TableCell>Linked Practitioner</TableCell>
                <TableCell>Status</TableCell>
                <TableCell align="right">Actions</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {users.map((user) => (
                <TableRow key={user.username}>
                  <TableCell>
                    <Box display="flex" alignItems="center" gap={1}>
                      <Person fontSize="small" color="action" />
                      {user.email || user.username}
                    </Box>
                  </TableCell>
                  <TableCell>
                    {user.first_name || user.last_name
                      ? `${user.first_name || ''} ${user.last_name || ''}`.trim()
                      : '-'}
                  </TableCell>
                  <TableCell>{user.email || '-'}</TableCell>
                  <TableCell>
                    <Chip
                      label={user.role}
                      size="small"
                      color={user.role === 'admin' ? 'primary' : 'default'}
                    />
                  </TableCell>
                  <TableCell>
                    <Box display="flex" gap={0.5} flexWrap="wrap">
                      {user.allowed_data_sources.map((source) => {
                        const ds = DATA_SOURCES.find((d) => d.id === source);
                        return (
                          <Chip
                            key={source}
                            label={`${ds?.icon || ''} ${ds?.name || source}`}
                            size="small"
                            variant="outlined"
                          />
                        );
                      })}
                    </Box>
                  </TableCell>
                  <TableCell>
                    {user.practitioner_name ? (
                      <Chip
                        label={user.practitioner_name}
                        size="small"
                        color="secondary"
                        variant="outlined"
                      />
                    ) : (
                      '-'
                    )}
                  </TableCell>
                  <TableCell>
                    <Chip
                      label={user.disabled ? 'Disabled' : 'Active'}
                      size="small"
                      color={user.disabled ? 'error' : 'success'}
                    />
                  </TableCell>
                  <TableCell align="right">
                    <Tooltip title="Edit">
                      <IconButton onClick={() => handleOpenEdit(user)} size="small">
                        <Edit fontSize="small" />
                      </IconButton>
                    </Tooltip>
                    {(user.email !== ADMIN_EMAIL && user.username !== ADMIN_EMAIL) && (
                      <Tooltip title="Delete">
                        <IconButton
                          onClick={() => {
                            setUserToDelete(user.username);
                            setDeleteDialogOpen(true);
                          }}
                          size="small"
                          color="error"
                        >
                          <Delete fontSize="small" />
                        </IconButton>
                      </Tooltip>
                    )}
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </TableContainer>
      </Paper>

      {/* Create/Edit User Dialog */}
      <Dialog open={dialogOpen} onClose={handleCloseDialog} maxWidth="sm" fullWidth>
        <DialogTitle>
          {editingUser ? `Edit User: ${editingUser.email || editingUser.username}` : 'Create New User'}
        </DialogTitle>
        <DialogContent>
          <Box sx={{ pt: 1, display: 'flex', flexDirection: 'column', gap: 2 }}>
            {/* Email (Username) */}
            <TextField
              label="Email (Username)"
              type="email"
              value={formData.email}
              onChange={(e) => setFormData({ ...formData, email: e.target.value })}
              required
              fullWidth
              disabled={editingUser?.role === 'admin' && editingUser?.email === ADMIN_EMAIL}
              helperText={
                editingUser?.role === 'admin' && editingUser?.email === ADMIN_EMAIL
                  ? 'Admin email cannot be changed'
                  : 'Email address is used as the username for login'
              }
            />

            {/* Password */}
            <TextField
              label={editingUser ? 'New Password (leave blank to keep current)' : 'Password'}
              type="password"
              value={formData.password}
              onChange={(e) => setFormData({ ...formData, password: e.target.value })}
              required={!editingUser}
              fullWidth
            />

            {/* First Name */}
            <TextField
              label="First Name"
              value={formData.first_name}
              onChange={(e) => setFormData({ ...formData, first_name: e.target.value })}
              fullWidth
            />

            {/* Last Name */}
            <TextField
              label="Last Name"
              value={formData.last_name}
              onChange={(e) => setFormData({ ...formData, last_name: e.target.value })}
              fullWidth
            />

            {/* Role */}
            <FormControl fullWidth>
              <InputLabel>Role</InputLabel>
              <Select
                value={formData.role}
                label="Role"
                onChange={(e) => setFormData({ ...formData, role: e.target.value })}
              >
                <MenuItem value="user">User</MenuItem>
                <MenuItem value="admin">Admin</MenuItem>
              </Select>
            </FormControl>

            <Divider sx={{ my: 1 }} />

            {/* Data Source Permissions */}
            <Box>
              <Typography variant="subtitle2" color="text.secondary" gutterBottom>
                <Storage fontSize="small" sx={{ verticalAlign: 'middle', mr: 1 }} />
                Data Source Access
              </Typography>
              <FormGroup row>
                {DATA_SOURCES.map((source) => (
                  <FormControlLabel
                    key={source.id}
                    control={
                      <Checkbox
                        checked={formData.allowed_data_sources.includes(source.id)}
                        onChange={() => handleDataSourceToggle(source.id)}
                      />
                    }
                    label={`${source.icon} ${source.name}`}
                  />
                ))}
              </FormGroup>
            </Box>

            <Divider sx={{ my: 1 }} />

            {/* Practitioner Link */}
            <Box>
              <Typography variant="subtitle2" color="text.secondary" gutterBottom>
                <Person fontSize="small" sx={{ verticalAlign: 'middle', mr: 1 }} />
                Link to Practitioner (Optional)
              </Typography>
              <Typography variant="caption" color="text.secondary" display="block" mb={1}>
                When linked, this user's practitioner filter will default to this practitioner.
              </Typography>
              <Autocomplete
                options={practitioners}
                getOptionLabel={(option) => option.name}
                value={practitioners.find((p) => p.id === formData.practitioner_id) || null}
                onChange={(_, value) => handlePractitionerSelect(value)}
                renderInput={(params) => (
                  <TextField {...params} label="Select Practitioner" />
                )}
                isOptionEqualToValue={(option, value) => option.id === value.id}
              />
            </Box>
          </Box>
        </DialogContent>
        <DialogActions>
          <Button onClick={handleCloseDialog}>Cancel</Button>
          <Button onClick={handleSave} variant="contained">
            {editingUser ? 'Save Changes' : 'Create User'}
          </Button>
        </DialogActions>
      </Dialog>

      {/* Delete Confirmation Dialog */}
      <Dialog open={deleteDialogOpen} onClose={() => setDeleteDialogOpen(false)}>
        <DialogTitle>Confirm Delete</DialogTitle>
        <DialogContent>
          <Typography>
            Are you sure you want to delete user "{userToDelete}"? This action cannot be undone.
          </Typography>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setDeleteDialogOpen(false)}>Cancel</Button>
          <Button onClick={handleDeleteConfirm} color="error" variant="contained">
            Delete
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

