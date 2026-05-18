import React, { useState, useEffect } from 'react';
import { Box, Typography, Paper, Button, Grid, TextField, Dialog, DialogTitle, DialogContent, DialogActions, IconButton, Snackbar, Alert } from '@mui/material';
import { DataGrid } from '@mui/x-data-grid';
import { Add, Edit, Delete, People } from '@mui/icons-material';
import api from '../../api/axiosConfig';
import { useSelector } from 'react-redux';

const Empleados = () => {
  const [empleados, setEmpleados] = useState([]);
  const [loading, setLoading] = useState(false);
  const [open, setOpen] = useState(false);
  const [form, setForm] = useState({ id: null, cedula: '', nombres: '', apellidos: '', direccion: '', telefono: '', email: '', fecha_nacimiento: '', fecha_ingreso: '', cargo: '', salario_base: 0, departamento: '', tipo_contrato: 'indefinido', estado: 'activo' });
  const [snackbar, setSnackbar] = useState({ open: false, message: '', severity: 'success' });
  const empresaId = useSelector((state) => state.empresa.empresaActiva);

  const fetchEmpleados = async () => {
    if (!empresaId) return;
    setLoading(true);
    try {
      const res = await api.get(`/nomina/empleados?empresa_id=${empresaId}`);
      setEmpleados(res.data.map((e) => ({ ...e, id: e.id })));
    } catch (e) {
      setSnackbar({ open: true, message: 'Error al cargar empleados', severity: 'error' });
    }
    setLoading(false);
  };

  useEffect(() => { fetchEmpleados(); }, [empresaId]);

  const handleSave = async () => {
    try {
      const data = { ...form, empresa_id: empresaId };
      if (form.id) await api.put(`/nomina/empleados/${form.id}`, data);
      else await api.post('/nomina/empleados', data);
      setOpen(false);
      fetchEmpleados();
      setSnackbar({ open: true, message: 'Empleado guardado', severity: 'success' });
    } catch (e) {
      setSnackbar({ open: true, message: 'Error al guardar', severity: 'error' });
    }
  };

  const handleDelete = async (id) => {
    if (!window.confirm('¿Eliminar empleado?')) return;
    try { await api.delete(`/nomina/empleados/${id}`); fetchEmpleados(); } catch (e) { setSnackbar({ open: true, message: 'Error al eliminar', severity: 'error' }); }
  };

  const columns = [
    { field: 'cedula', headerName: 'Cédula', flex: 1 },
    { field: 'nombres', headerName: 'Nombres', flex: 2 },
    { field: 'apellidos', headerName: 'Apellidos', flex: 2 },
    { field: 'cargo', headerName: 'Cargo', flex: 1 },
    { field: 'departamento', headerName: 'Departamento', flex: 1 },
    { field: 'salario_base', headerName: 'Salario', flex: 1, type: 'number' },
    { field: 'fecha_ingreso', headerName: 'Ingreso', flex: 1 },
    { field: 'estado', headerName: 'Estado', flex: 0.8 },
    { field: 'acciones', headerName: 'Acciones', flex: 1, sortable: false, renderCell: (p) => (
      <Box>
        <IconButton size="small" onClick={() => { setForm(p.row); setOpen(true); }}><Edit fontSize="small" /></IconButton>
        <IconButton size="small" color="error" onClick={() => handleDelete(p.row.id)}><Delete fontSize="small" /></IconButton>
      </Box>
    )}
  ];

  return (
    <Box p={3}>
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={2}>
        <Typography variant="h5"><People sx={{ mr: 1, verticalAlign: 'middle' }} />Empleados</Typography>
        <Button variant="contained" startIcon={<Add />} onClick={() => { setForm({ id: null, cedula: '', nombres: '', apellidos: '', direccion: '', telefono: '', email: '', fecha_nacimiento: '', fecha_ingreso: '', cargo: '', salario_base: 0, departamento: '', tipo_contrato: 'indefinido', estado: 'activo' }); setOpen(true); }}>
          Nuevo Empleado
        </Button>
      </Box>
      <Paper sx={{ height: '70vh' }}>
        <DataGrid rows={empleados} columns={columns} loading={loading} pageSizeOptions={[10, 25, 50]} disableRowSelectionOnClick />
      </Paper>
      <Dialog open={open} onClose={() => setOpen(false)} maxWidth="md" fullWidth>
        <DialogTitle>{form.id ? 'Editar' : 'Nuevo'} Empleado</DialogTitle>
        <DialogContent>
          <Grid container spacing={2} mt={1}>
            <Grid item xs={12} sm={6}><TextField label="Cédula" fullWidth value={form.cedula} onChange={(e) => setForm({ ...form, cedula: e.target.value })} /></Grid>
            <Grid item xs={12} sm={6}><TextField label="Nombres" fullWidth value={form.nombres} onChange={(e) => setForm({ ...form, nombres: e.target.value })} /></Grid>
            <Grid item xs={12} sm={6}><TextField label="Apellidos" fullWidth value={form.apellidos} onChange={(e) => setForm({ ...form, apellidos: e.target.value })} /></Grid>
            <Grid item xs={12} sm={6}><TextField label="Cargo" fullWidth value={form.cargo} onChange={(e) => setForm({ ...form, cargo: e.target.value })} /></Grid>
            <Grid item xs={12} sm={6}><TextField label="Departamento" fullWidth value={form.departamento} onChange={(e) => setForm({ ...form, departamento: e.target.value })} /></Grid>
            <Grid item xs={12} sm={6}><TextField label="Salario Base" type="number" fullWidth value={form.salario_base} onChange={(e) => setForm({ ...form, salario_base: parseFloat(e.target.value) || 0 })} /></Grid>
            <Grid item xs={12} sm={6}><TextField label="Teléfono" fullWidth value={form.telefono} onChange={(e) => setForm({ ...form, telefono: e.target.value })} /></Grid>
            <Grid item xs={12} sm={6}><TextField label="Email" fullWidth value={form.email} onChange={(e) => setForm({ ...form, email: e.target.value })} /></Grid>
            <Grid item xs={12} sm={6}><TextField label="Fecha Nacimiento" type="date" fullWidth value={form.fecha_nacimiento} onChange={(e) => setForm({ ...form, fecha_nacimiento: e.target.value })} InputLabelProps={{ shrink: true }} /></Grid>
            <Grid item xs={12} sm={6}><TextField label="Fecha Ingreso" type="date" fullWidth value={form.fecha_ingreso} onChange={(e) => setForm({ ...form, fecha_ingreso: e.target.value })} InputLabelProps={{ shrink: true }} /></Grid>
            <Grid item xs={12}><TextField label="Dirección" fullWidth value={form.direccion} onChange={(e) => setForm({ ...form, direccion: e.target.value })} /></Grid>
          </Grid>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setOpen(false)}>Cancelar</Button>
          <Button variant="contained" onClick={handleSave}>Guardar</Button>
        </DialogActions>
      </Dialog>
      <Snackbar open={snackbar.open} autoHideDuration={4000} onClose={() => setSnackbar({ ...snackbar, open: false })}>
        <Alert severity={snackbar.severity}>{snackbar.message}</Alert>
      </Snackbar>
    </Box>
  );
};

export default Empleados;
