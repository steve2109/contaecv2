import React, { useState, useEffect } from 'react';
import { Box, Typography, Paper, Button, Grid, TextField, Dialog, DialogTitle, DialogContent, DialogActions, IconButton, Snackbar, Alert } from '@mui/material';
import { DataGrid } from '@mui/x-data-grid';
import { Add, Edit, Delete, Upload, Download } from '@mui/icons-material';
import api from '../../api/axiosConfig';
import { useSelector } from 'react-redux';

const Clientes = () => {
  const [clientes, setClientes] = useState([]);
  const [loading, setLoading] = useState(false);
  const [open, setOpen] = useState(false);
  const [form, setForm] = useState({ id: null, identificacion: '', nombre: '', direccion: '', telefono: '', email: '', tipo: 'cliente' });
  const [snackbar, setSnackbar] = useState({ open: false, message: '', severity: 'success' });
  const empresaId = useSelector((state) => state.empresa.empresaActiva);

  const fetchClientes = async () => {
    if (!empresaId) return;
    setLoading(true);
    try {
      const res = await api.get(`/clientes?empresa_id=${empresaId}`);
      setClientes(res.data.map((c) => ({ ...c, id: c.id })));
    } catch (e) {
      setSnackbar({ open: true, message: 'Error al cargar clientes', severity: 'error' });
    }
    setLoading(false);
  };

  useEffect(() => { fetchClientes(); }, [empresaId]);

  const handleSave = async () => {
    try {
      const data = { ...form, empresa_id: empresaId };
      if (form.id) await api.put(`/clientes/${form.id}`, data);
      else await api.post('/clientes', data);
      setOpen(false);
      fetchClientes();
      setSnackbar({ open: true, message: 'Guardado correctamente', severity: 'success' });
    } catch (e) {
      setSnackbar({ open: true, message: 'Error al guardar', severity: 'error' });
    }
  };

  const handleDelete = async (id) => {
    if (!window.confirm('¿Eliminar este registro?')) return;
    try { await api.delete(`/clientes/${id}`); fetchClientes(); } catch (e) { setSnackbar({ open: true, message: 'Error al eliminar', severity: 'error' }); }
  };

  const handleFileImport = async (e) => {
    const file = e.target.files[0];
    if (!file) return;
    const fd = new FormData();
    fd.append('file', file);
    fd.append('empresa_id', empresaId);
    try {
      await api.post('/upload/import/clientes', fd, { headers: { 'Content-Type': 'multipart/form-data' } });
      fetchClientes();
      setSnackbar({ open: true, message: 'Importación exitosa', severity: 'success' });
    } catch (err) {
      setSnackbar({ open: true, message: err.response?.data?.detail || 'Error al importar', severity: 'error' });
    }
  };

  const columns = [
    { field: 'identificacion', headerName: 'Identificación', flex: 1 },
    { field: 'nombre', headerName: 'Nombre/Razón Social', flex: 2 },
    { field: 'direccion', headerName: 'Dirección', flex: 2 },
    { field: 'telefono', headerName: 'Teléfono', flex: 1 },
    { field: 'email', headerName: 'Email', flex: 1 },
    { field: 'tipo', headerName: 'Tipo', flex: 0.8 },
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
        <Typography variant="h5">Clientes / Proveedores</Typography>
        <Box>
          <Button variant="outlined" component="label" startIcon={<Upload />} sx={{ mr: 1 }}>
            Importar
            <input type="file" hidden accept=".xlsx,.csv" onChange={handleFileImport} />
          </Button>
          <Button variant="contained" startIcon={<Add />} onClick={() => { setForm({ id: null, identificacion: '', nombre: '', direccion: '', telefono: '', email: '', tipo: 'cliente' }); setOpen(true); }}>
            Nuevo
          </Button>
        </Box>
      </Box>
      <Paper sx={{ height: '70vh' }}>
        <DataGrid rows={clientes} columns={columns} loading={loading} pageSizeOptions={[10, 25, 50]} disableRowSelectionOnClick />
      </Paper>
      <Dialog open={open} onClose={() => setOpen(false)} maxWidth="sm" fullWidth>
        <DialogTitle>{form.id ? 'Editar' : 'Nuevo'} Cliente/Proveedor</DialogTitle>
        <DialogContent>
          <Grid container spacing={2} mt={1}>
            <Grid item xs={12} sm={6}><TextField label="Identificación" fullWidth value={form.identificacion} onChange={(e) => setForm({ ...form, identificacion: e.target.value })} /></Grid>
            <Grid item xs={12} sm={6}><TextField label="Nombre/Razón Social" fullWidth value={form.nombre} onChange={(e) => setForm({ ...form, nombre: e.target.value })} /></Grid>
            <Grid item xs={12}><TextField label="Dirección" fullWidth value={form.direccion} onChange={(e) => setForm({ ...form, direccion: e.target.value })} /></Grid>
            <Grid item xs={12} sm={6}><TextField label="Teléfono" fullWidth value={form.telefono} onChange={(e) => setForm({ ...form, telefono: e.target.value })} /></Grid>
            <Grid item xs={12} sm={6}><TextField label="Email" fullWidth value={form.email} onChange={(e) => setForm({ ...form, email: e.target.value })} /></Grid>
            <Grid item xs={12} sm={6}>
              <TextField select label="Tipo" fullWidth value={form.tipo} onChange={(e) => setForm({ ...form, tipo: e.target.value })} SelectProps={{ native: true }}>
                <option value="cliente">Cliente</option>
                <option value="proveedor">Proveedor</option>
              </TextField>
            </Grid>
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

export default Clientes;
