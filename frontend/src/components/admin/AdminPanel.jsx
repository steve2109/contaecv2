import React, { useState, useEffect } from 'react';
import { useSelector } from 'react-redux';
import { useNavigate } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import {
  Box, Typography, Tabs, Tab, Paper, Table, TableBody, TableCell,
  TableContainer, TableHead, TableRow, Chip, Button, Dialog,
  DialogTitle, DialogContent, DialogActions, TextField, Grid,
  Card, CardContent, LinearProgress, Alert,
} from '@mui/material';
import {
  Security, People, Assignment, Storage, Warning,
} from '@mui/icons-material';
import { ResponsiveContainer, BarChart, Bar, XAxis, YAxis, Tooltip, CartesianGrid } from 'recharts';
import api from '../../api/axiosConfig';

const AdminPanel = () => {
  const { t } = useTranslation();
  const navigate = useNavigate();
  const { user } = useSelector((state) => state.auth);
  const [tab, setTab] = useState(0);
  const [usuarios, setUsuarios] = useState([]);
  const [estadisticas, setEstadisticas] = useState({});
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (user?.email !== 'steve.mejia@tymtechnology.shop') {
      navigate('/dashboard');
      return;
    }
    loadData();
  }, [user, navigate]);

  const loadData = async () => {
    setLoading(true);
    try {
      const [usersRes, statsRes] = await Promise.all([
        api.get('/admin/usuarios'),
        api.get('/admin/estadisticas'),
      ]);
      setUsuarios(usersRes.data);
      setEstadisticas(statsRes.data);
    } catch (error) { console.error('Error:', error); }
    setLoading(false);
  };

  const renovarLicencia = async (userId, tipoLicencia) => {
    try {
      await api.post('/admin/renovar-licencia', { user_id: userId, tipo_licencia: tipoLicencia });
      loadData();
    } catch (error) { console.error('Error:', error); }
  };

  const sampleChartData = [
    { mes: 'Ene', usuarios: 5, licencias: 3 },
    { mes: 'Feb', usuarios: 8, licencias: 6 },
    { mes: 'Mar', usuarios: 12, licencias: 9 },
    { mes: 'Abr', usuarios: 15, licencias: 12 },
    { mes: 'May', usuarios: 18, licencias: 15 },
    { mes: 'Jun', usuarios: 22, licencias: 18 },
  ];

  return (
    <Box>
      <Typography variant="h4" fontWeight="bold" gutterBottom>
        {t('admin.title')}
      </Typography>

      <Tabs value={tab} onChange={(e, v) => setTab(v)} sx={{ mb: 3 }}>
        <Tab label={t('admin.dashboard')} icon={<Storage />} iconPosition="start" />
        <Tab label={t('admin.salud')} icon={<Security />} iconPosition="start" />
        <Tab label={t('admin.usuarios')} icon={<People />} iconPosition="start" />
        <Tab label={t('admin.licencias')} icon={<Assignment />} iconPosition="start" />
        <Tab label={t('admin.seguridad')} icon={<Warning />} iconPosition="start" />
      </Tabs>

      {tab === 0 && (
        <Grid container spacing={3}>
          <Grid item xs={12} sm={6} md={3}>
            <Card>
              <CardContent>
                <Typography color="text.secondary" gutterBottom>{t('admin.totalUsuarios')}</Typography>
                <Typography variant="h3" fontWeight="bold">{estadisticas.total_usuarios || 0}</Typography>
              </CardContent>
            </Card>
          </Grid>
          <Grid item xs={12} sm={6} md={3}>
            <Card>
              <CardContent>
                <Typography color="text.secondary" gutterBottom>{t('admin.usuariosActivos')}</Typography>
                <Typography variant="h3" fontWeight="bold">{estadisticas.usuarios_activos || 0}</Typography>
              </CardContent>
            </Card>
          </Grid>
          <Grid item xs={12} sm={6} md={3}>
            <Card>
              <CardContent>
                <Typography color="text.secondary" gutterBottom>{t('admin.licenciasActivas')}</Typography>
                <Typography variant="h3" fontWeight="bold" color="success.main">{estadisticas.licencias_activas || 0}</Typography>
              </CardContent>
            </Card>
          </Grid>
          <Grid item xs={12} sm={6} md={3}>
            <Card>
              <CardContent>
                <Typography color="text.secondary" gutterBottom>{t('admin.licenciasVencidas')}</Typography>
                <Typography variant="h3" fontWeight="bold" color="error.main">{estadisticas.licencias_vencidas || 0}</Typography>
              </CardContent>
            </Card>
          </Grid>

          <Grid item xs={12} md={8}>
            <Paper elevation={2} sx={{ p: 3 }}>
              <Typography variant="h6" gutterBottom>Crecimiento Mensual</Typography>
              <ResponsiveContainer width="100%" height={300}>
                <BarChart data={sampleChartData}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="mes" />
                  <YAxis />
                  <Tooltip />
                  <Bar dataKey="usuarios" fill="#1a5276" />
                  <Bar dataKey="licencias" fill="#2980b9" />
                </BarChart>
              </ResponsiveContainer>
            </Paper>
          </Grid>

          <Grid item xs={12} md={4}>
            <Paper elevation={2} sx={{ p: 3 }}>
              <Typography variant="h6" gutterBottom>{t('admin.alertas')}</Typography>
              {usuarios.filter(u => u.dias_restantes <= 15).map(u => (
                <Alert severity="warning" key={u.id} sx={{ mb: 1 }}>
                  {u.email} - {u.dias_restantes} días restantes
                </Alert>
              ))}
              {usuarios.filter(u => u.dias_restantes <= 15).length === 0 && (
                <Typography color="text.secondary">Sin alertas</Typography>
              )}
            </Paper>
          </Grid>
        </Grid>
      )}

      {tab === 2 && (
        <TableContainer component={Paper} elevation={2}>
          {loading && <LinearProgress />}
          <Table>
            <TableHead>
              <TableRow>
                <TableCell>Email</TableCell>
                <TableCell>Nombre</TableCell>
                <TableCell>Empresas</TableCell>
                <TableCell>Tipo Licencia</TableCell>
                <TableCell>Vigencia</TableCell>
                <TableCell>Estado</TableCell>
                <TableCell>Acciones</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {usuarios.map((u) => (
                <TableRow key={u.id} hover>
                  <TableCell>{u.email}</TableCell>
                  <TableCell>{u.nombres} {u.apellidos}</TableCell>
                  <TableCell>{u.num_empresas}</TableCell>
                  <TableCell>
                    <Chip label={u.tipo_licencia || 'N/A'} size="small" />
                  </TableCell>
                  <TableCell>
                    <Chip
                      label={u.dias_restantes > 0 ? `${u.dias_restantes} días` : 'Vencida'}
                      color={u.dias_restantes > 15 ? 'success' : u.dias_restantes > 0 ? 'warning' : 'error'}
                      size="small"
                    />
                  </TableCell>
                  <TableCell>
                    <Chip label={u.activo ? 'Activo' : 'Inactivo'} color={u.activo ? 'success' : 'default'} size="small" />
                  </TableCell>
                  <TableCell>
                    <Button size="small" variant="outlined" onClick={() => renovarLicencia(u.id, 'mensual')}>
                      Mensual
                    </Button>
                    <Button size="small" variant="outlined" sx={{ ml: 1 }} onClick={() => renovarLicencia(u.id, 'anual')}>
                      Anual
                    </Button>
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </TableContainer>
      )}
    </Box>
  );
};

export default AdminPanel;
