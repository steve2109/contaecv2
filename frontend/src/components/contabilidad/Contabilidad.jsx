import React, { useState, useEffect } from 'react';
import { Box, Typography, Paper, Button, Grid, Tabs, Tab, TextField, Dialog, DialogTitle, DialogContent, DialogActions, IconButton, Snackbar, Alert } from '@mui/material';
import { DataGrid } from '@mui/x-data-grid';
import { Add, Edit, Delete, AccountBalance } from '@mui/icons-material';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';
import api from '../../api/axiosConfig';
import { useSelector } from 'react-redux';

const Contabilidad = () => {
  const [tab, setTab] = useState(0);
  const [cuentas, setCuentas] = useState([]);
  const [asientos, setAsientos] = useState([]);
  const [loading, setLoading] = useState(false);
  const [open, setOpen] = useState(false);
  const [form, setForm] = useState({ id: null, codigo: '', nombre: '', tipo: '', nivel: 1, cuenta_padre_id: null });
  const [snackbar, setSnackbar] = useState({ open: false, message: '', severity: 'success' });
  const empresaId = useSelector((state) => state.empresa.empresaActiva);

  const fetchData = async () => {
    if (!empresaId) return;
    setLoading(true);
    try {
      const [c, a] = await Promise.all([
        api.get(`/contabilidad/cuentas?empresa_id=${empresaId}`),
        api.get(`/contabilidad/asientos?empresa_id=${empresaId}`)
      ]);
      setCuentas(c.data.map(x => ({ ...x, id: x.id })));
      setAsientos(a.data.map(x => ({ ...x, id: x.id })));
    } catch (e) {
      setSnackbar({ open: true, message: 'Error al cargar datos', severity: 'error' });
    }
    setLoading(false);
  };

  useEffect(() => { fetchData(); }, [empresaId]);

  const handleSaveCuenta = async () => {
    try {
      const data = { ...form, empresa_id: empresaId };
      if (form.id) await api.put(`/contabilidad/cuentas/${form.id}`, data);
      else await api.post('/contabilidad/cuentas', data);
      setOpen(false); fetchData();
      setSnackbar({ open: true, message: 'Cuenta guardada', severity: 'success' });
    } catch (e) {
      setSnackbar({ open: true, message: 'Error al guardar', severity: 'error' });
    }
  };

  const handleDeleteCuenta = async (id) => {
    if (!window.confirm('¿Eliminar cuenta?')) return;
    try { await api.delete(`/contabilidad/cuentas/${id}`); fetchData(); } catch (e) { setSnackbar({ open: true, message: 'Error al eliminar', severity: 'error' }); }
  };

  const cuentaCols = [
    { field: 'codigo', headerName: 'Código', flex: 1 },
    { field: 'nombre', headerName: 'Nombre', flex: 2 },
    { field: 'tipo', headerName: 'Tipo', flex: 1 },
    { field: 'nivel', headerName: 'Nivel', flex: 0.5 },
    { field: 'acciones', headerName: 'Acciones', flex: 1, sortable: false, renderCell: (p) => (
      <Box>
        <IconButton size="small" onClick={() => { setForm(p.row); setOpen(true); }}><Edit fontSize="small" /></IconButton>
        <IconButton size="small" color="error" onClick={() => handleDeleteCuenta(p.row.id)}><Delete fontSize="small" /></IconButton>
      </Box>
    )}
  ];

  const asientoCols = [
    { field: 'fecha', headerName: 'Fecha', flex: 1 },
    { field: 'referencia', headerName: 'Referencia', flex: 1 },
    { field: 'descripcion', headerName: 'Descripción', flex: 2 },
    { field: 'total_debe', headerName: 'Debe', flex: 1, type: 'number' },
    { field: 'total_haber', headerName: 'Haber', flex: 1, type: 'number' },
  ];

  return (
    <Box p={3}>
      <Typography variant="h5" gutterBottom><AccountBalance sx={{ mr: 1, verticalAlign: 'middle' }} />Contabilidad</Typography>
      <Tabs value={tab} onChange={(_, v) => setTab(v)} sx={{ mb: 2 }}>
        <Tab label="Plan de Cuentas" />
        <Tab label="Asientos Contables" />
        <Tab label="Balance General" />
      </Tabs>

      {tab === 0 && (
        <>
          <Box display="flex" justifyContent="flex-end" mb={2}>
            <Button variant="contained" startIcon={<Add />} onClick={() => { setForm({ id: null, codigo: '', nombre: '', tipo: 'activo', nivel: 1, cuenta_padre_id: null }); setOpen(true); }}>Nueva Cuenta</Button>
          </Box>
          <Paper sx={{ height: '60vh' }}>
            <DataGrid rows={cuentas} columns={cuentaCols} loading={loading} pageSizeOptions={[10, 25, 50]} disableRowSelectionOnClick />
          </Paper>
        </>
      )}

      {tab === 1 && (
        <Paper sx={{ height: '60vh' }}>
          <DataGrid rows={asientos} columns={asientoCols} loading={loading} pageSizeOptions={[10, 25, 50]} disableRowSelectionOnClick />
        </Paper>
      )}

      {tab === 2 && (
        <Box>
          <Typography variant="h6" gutterBottom>Balance General</Typography>
          <ResponsiveContainer width="100%" height={300}>
            <LineChart data={[]}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="mes" />
              <YAxis />
              <Tooltip />
              <Legend />
              <Line type="monotone" dataKey="activos" stroke="#1a5276" name="Activos" />
              <Line type="monotone" dataKey="pasivos" stroke="#c0392b" name="Pasivos" />
              <Line type="monotone" dataKey="patrimonio" stroke="#27ae60" name="Patrimonio" />
            </LineChart>
          </ResponsiveContainer>
        </Box>
      )}

      <Dialog open={open} onClose={() => setOpen(false)} maxWidth="sm" fullWidth>
        <DialogTitle>{form.id ? 'Editar' : 'Nueva'} Cuenta</DialogTitle>
        <DialogContent>
          <Grid container spacing={2} mt={1}>
            <Grid item xs={12} sm={6}><TextField label="Código" fullWidth value={form.codigo} onChange={(e) => setForm({ ...form, codigo: e.target.value })} /></Grid>
            <Grid item xs={12} sm={6}><TextField label="Nombre" fullWidth value={form.nombre} onChange={(e) => setForm({ ...form, nombre: e.target.value })} /></Grid>
            <Grid item xs={12} sm={6}>
              <TextField select label="Tipo" fullWidth value={form.tipo} onChange={(e) => setForm({ ...form, tipo: e.target.value })} SelectProps={{ native: true }}>
                <option value="activo">Activo</option>
                <option value="pasivo">Pasivo</option>
                <option value="patrimonio">Patrimonio</option>
                <option value="ingreso">Ingreso</option>
                <option value="gasto">Gasto</option>
              </TextField>
            </Grid>
            <Grid item xs={12} sm={6}><TextField label="Nivel" type="number" fullWidth value={form.nivel} onChange={(e) => setForm({ ...form, nivel: parseInt(e.target.value) || 1 })} /></Grid>
          </Grid>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setOpen(false)}>Cancelar</Button>
          <Button variant="contained" onClick={handleSaveCuenta}>Guardar</Button>
        </DialogActions>
      </Dialog>

      <Snackbar open={snackbar.open} autoHideDuration={4000} onClose={() => setSnackbar({ ...snackbar, open: false })}>
        <Alert severity={snackbar.severity}>{snackbar.message}</Alert>
      </Snackbar>
    </Box>
  );
};

export default Contabilidad;
