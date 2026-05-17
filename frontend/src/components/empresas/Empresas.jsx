import React, { useState, useEffect } from 'react';
import { useTranslation } from 'react-i18next';
import { useSelector } from 'react-redux';
import {
  Box,
  Typography,
  Button,
  Paper,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
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
  Switch,
  FormControlLabel,
  Chip,
  Avatar,
  Grid,
  Alert,
  LinearProgress,
  InputAdornment,
  Tabs,
  Tab,
  Divider,
} from '@mui/material';
import {
  Add,
  Edit,
  Delete,
  CloudUpload,
  Business,
  Search,
  Visibility,
} from '@mui/icons-material';
import api from '../../api/axiosConfig';

const Empresas = () => {
  const { t } = useTranslation();
  const { user } = useSelector((state) => state.auth);
  const [empresas, setEmpresas] = useState([]);
  const [loading, setLoading] = useState(false);
  const [open, setOpen] = useState(false);
  const [editingEmpresa, setEditingEmpresa] = useState(null);
  const [activeTab, setActiveTab] = useState(0);
  const [formData, setFormData] = useState({
    ruc: '',
    razon_social: '',
    nombre_comercial: '',
    direccion: '',
    telefono: '',
    email: '',
    obligado_contabilidad: false,
    ambiente: 'pruebas',
    logo: null,
    firma_electronica: null,
    clave_firma: '',
  });

  useEffect(() => {
    loadEmpresas();
  }, []);

  const loadEmpresas = async () => {
    setLoading(true);
    try {
      const response = await api.get('/empresas');
      setEmpresas(response.data);
    } catch (error) {
      console.error('Error cargando empresas:', error);
    }
    setLoading(false);
  };

  const handleOpen = (empresa = null) => {
    if (empresa) {
      setEditingEmpresa(empresa);
      setFormData({ ...empresa, clave_firma: '', logo: null, firma_electronica: null });
    } else {
      setEditingEmpresa(null);
      setFormData({
        ruc: '',
        razon_social: '',
        nombre_comercial: '',
        direccion: '',
        telefono: '',
        email: '',
        obligado_contabilidad: false,
        ambiente: 'pruebas',
        logo: null,
        firma_electronica: null,
        clave_firma: '',
      });
    }
    setActiveTab(0);
    setOpen(true);
  };

  const handleClose = () => {
    setOpen(false);
    setEditingEmpresa(null);
  };

  const handleSubmit = async () => {
    try {
      const data = new FormData();
      Object.keys(formData).forEach((key) => {
        if (formData[key] !== null && formData[key] !== '') {
          data.append(key, formData[key]);
        }
      });

      if (editingEmpresa) {
        await api.put(`/empresas/${editingEmpresa.id}`, data);
      } else {
        await api.post('/empresas', data);
      }
      loadEmpresas();
      handleClose();
    } catch (error) {
      console.error('Error guardando empresa:', error);
    }
  };

  const handleConsultarRUC = async () => {
    if (!formData.ruc || formData.ruc.length !== 13) return;
    try {
      const response = await api.post('/empresas/consultar-ruc', { ruc: formData.ruc });
      setFormData((prev) => ({
        ...prev,
        razon_social: response.data.razon_social || prev.razon_social,
        nombre_comercial: response.data.nombre_comercial || prev.nombre_comercial,
        direccion: response.data.direccion || prev.direccion,
      }));
    } catch (error) {
      console.error('Error consultando RUC:', error);
    }
  };

  return (
    <Box>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
        <Typography variant="h4" fontWeight="bold">
          {t('empresas.title')}
        </Typography>
        <Button
          variant="contained"
          startIcon={<Add />}
          onClick={() => handleOpen()}
        >
          {t('empresas.create')}
        </Button>
      </Box>

      {loading && <LinearProgress sx={{ mb: 2 }} />}

      <TableContainer component={Paper} elevation={2}>
        <Table>
          <TableHead>
            <TableRow>
              <TableCell>Logo</TableCell>
              <TableCell>RUC</TableCell>
              <TableCell>Razón Social</TableCell>
              <TableCell>Ambiente</TableCell>
              <TableCell>Estado</TableCell>
              <TableCell>Acciones</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {empresas.map((empresa) => (
              <TableRow key={empresa.id} hover>
                <TableCell>
                  <Avatar src={empresa.logo_url} alt={empresa.razon_social}>
                    <Business />
                  </Avatar>
                </TableCell>
                <TableCell>{empresa.ruc}</TableCell>
                <TableCell>{empresa.razon_social}</TableCell>
                <TableCell>
                  <Chip
                    label={empresa.ambiente === 'produccion' ? 'Producción' : 'Pruebas'}
                    color={empresa.ambiente === 'produccion' ? 'success' : 'info'}
                    size="small"
                  />
                </TableCell>
                <TableCell>
                  <Chip
                    label={empresa.activa ? 'Activa' : 'Inactiva'}
                    color={empresa.activa ? 'success' : 'default'}
                    size="small"
                  />
                </TableCell>
                <TableCell>
                  <IconButton onClick={() => handleOpen(empresa)} color="primary">
                    <Edit />
                  </IconButton>
                  <IconButton color="error">
                    <Delete />
                  </IconButton>
                </TableCell>
              </TableRow>
            ))}
            {empresas.length === 0 && (
              <TableRow>
                <TableCell colSpan={6} align="center">
                  <Typography color="text.secondary" sx={{ py: 3 }}>
                    {t('empresas.noEmpresas')}
                  </Typography>
                </TableCell>
              </TableRow>
            )}
          </TableBody>
        </Table>
      </TableContainer>

      {/* Dialogo de creación/edición */}
      <Dialog open={open} onClose={handleClose} maxWidth="md" fullWidth>
        <DialogTitle>
          {editingEmpresa ? t('empresas.edit') : t('empresas.create')}
        </DialogTitle>
        <DialogContent>
          <Tabs value={activeTab} onChange={(e, v) => setActiveTab(v)} sx={{ mb: 2 }}>
            <Tab label="Datos Básicos" />
            <Tab label="Firma Electrónica" />
            <Tab label="Configuración" />
          </Tabs>

          {activeTab === 0 && (
            <Grid container spacing={2}>
              <Grid item xs={12} sm={6}>
                <TextField
                  fullWidth
                  label="RUC"
                  value={formData.ruc}
                  onChange={(e) => setFormData({ ...formData, ruc: e.target.value })}
                  InputProps={{
                    endAdornment: (
                      <InputAdornment position="end">
                        <IconButton onClick={handleConsultarRUC} edge="end">
                          <Search />
                        </IconButton>
                      </InputAdornment>
                    ),
                  }}
                />
              </Grid>
              <Grid item xs={12} sm={6}>
                <TextField
                  fullWidth
                  label={t('empresas.razonSocial')}
                  value={formData.razon_social}
                  onChange={(e) => setFormData({ ...formData, razon_social: e.target.value })}
                />
              </Grid>
              <Grid item xs={12} sm={6}>
                <TextField
                  fullWidth
                  label={t('empresas.nombreComercial')}
                  value={formData.nombre_comercial}
                  onChange={(e) => setFormData({ ...formData, nombre_comercial: e.target.value })}
                />
              </Grid>
              <Grid item xs={12} sm={6}>
                <TextField
                  fullWidth
                  label={t('empresas.telefono')}
                  value={formData.telefono}
                  onChange={(e) => setFormData({ ...formData, telefono: e.target.value })}
                />
              </Grid>
              <Grid item xs={12}>
                <TextField
                  fullWidth
                  label={t('empresas.direccion')}
                  value={formData.direccion}
                  onChange={(e) => setFormData({ ...formData, direccion: e.target.value })}
                />
              </Grid>
              <Grid item xs={12} sm={6}>
                <TextField
                  fullWidth
                  label={t('empresas.email')}
                  type="email"
                  value={formData.email}
                  onChange={(e) => setFormData({ ...formData, email: e.target.value })}
                />
              </Grid>
              <Grid item xs={12} sm={6}>
                <FormControl fullWidth>
                  <InputLabel>Logotipo</InputLabel>
                  <Button
                    variant="outlined"
                    component="label"
                    startIcon={<CloudUpload />}
                  >
                    Subir Logo
                    <input
                      type="file"
                      accept="image/*"
                      hidden
                      onChange={(e) => setFormData({ ...formData, logo: e.target.files[0] })}
                    />
                  </Button>
                </FormControl>
              </Grid>
            </Grid>
          )}

          {activeTab === 1 && (
            <Grid container spacing={2}>
              <Grid item xs={12}>
                <Alert severity="info" sx={{ mb: 2 }}>
                  La firma electrónica y su clave se guardarán de forma segura en el sistema.
                </Alert>
              </Grid>
              <Grid item xs={12}>
                <Button
                  variant="outlined"
                  component="label"
                  startIcon={<CloudUpload />}
                  fullWidth
                >
                  Subir Firma Electrónica (.p12)
                  <input
                    type="file"
                    accept=".p12,.pfx"
                    hidden
                    onChange={(e) => setFormData({ ...formData, firma_electronica: e.target.files[0] })}
                  />
                </Button>
              </Grid>
              <Grid item xs={12}>
                <TextField
                  fullWidth
                  type="password"
                  label={t('empresas.claveFirma')}
                  value={formData.clave_firma}
                  onChange={(e) => setFormData({ ...formData, clave_firma: e.target.value })}
                />
              </Grid>
              <Grid item xs={12}>
                {formData.firma_electronica && (
                  <Alert severity="success">
                    Firma cargada. Validez: hasta 2025-12-31 (ejemplo)
                  </Alert>
                )}
              </Grid>
            </Grid>
          )}

          {activeTab === 2 && (
            <Grid container spacing={2}>
              <Grid item xs={12}>
                <FormControlLabel
                  control={
                    <Switch
                      checked={formData.obligado_contabilidad}
                      onChange={(e) =>
                        setFormData({ ...formData, obligado_contabilidad: e.target.checked })
                      }
                    />
                  }
                  label={t('empresas.obligadoContabilidad')}
                />
              </Grid>
              <Grid item xs={12}>
                <FormControl fullWidth>
                  <InputLabel>{t('empresas.ambiente')}</InputLabel>
                  <Select
                    value={formData.ambiente}
                    onChange={(e) => setFormData({ ...formData, ambiente: e.target.value })}
                  >
                    <MenuItem value="pruebas">{t('empresas.pruebas')}</MenuItem>
                    <MenuItem value="produccion">{t('empresas.produccion')}</MenuItem>
                  </Select>
                </FormControl>
              </Grid>
            </Grid>
          )}
        </DialogContent>
        <DialogActions>
          <Button onClick={handleClose}>{t('common.cancel')}</Button>
          <Button onClick={handleSubmit} variant="contained">
            {t('common.save')}
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default Empresas;
