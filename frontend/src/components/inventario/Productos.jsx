import React, { useState, useEffect } from 'react';
import { Box, Typography, Paper, Button, Grid, TextField, Dialog, DialogTitle, DialogContent, DialogActions, IconButton, Snackbar, Alert } from '@mui/material';
import { DataGrid } from '@mui/x-data-grid';
import { Add, Edit, Delete, Upload, Download } from '@mui/icons-material';
import api from '../../api/axiosConfig';
import { useSelector } from 'react-redux';

const Productos = () => {
  const [productos, setProductos] = useState([]);
  const [loading, setLoading] = useState(false);
  const [open, setOpen] = useState(false);
  const [form, setForm] = useState({ id: null, codigo: '', nombre: '', descripcion: '', categoria: '', precio: 0, costo: 0, stock: 0, stock_minimo: 0, unidad_medida: 'unidad' });
  const [snackbar, setSnackbar] = useState({ open: false, message: '', severity: 'success' });
  const empresaId = useSelector((state) => state.empresa.empresaActiva);

  const fetchProductos = async () => {
    if (!empresaId) return;
    setLoading(true);
    try {
      const res = await api.get(`/productos?empresa_id=${empresaId}`);
      setProductos(res.data.map((p) => ({ ...p, id: p.id })));
    } catch (e) {
      setSnackbar({ open: true, message: 'Error al cargar productos', severity: 'error' });
    }
    setLoading(false);
  };

  useEffect(() => { fetchProductos(); }, [empresaId]);

  const handleSave = async () => {
    try {
      const data = { ...form, empresa_id: empresaId };
      if (form.id) await api.put(`/productos/${form.id}`, data);
      else await api.post('/productos', data);
      setOpen(false);
      fetchProductos();
      setSnackbar({ open: true, message: 'Producto guardado', severity: 'success' });
    } catch (e) {
      setSnackbar({ open: true, message: 'Error al guardar', severity: 'error' });
    }
  };

  const handleDelete = async (id) => {
    if (!window.confirm('¿Eliminar producto?')) return;
    try { await api.delete(`/productos/${id}`); fetchProductos(); } catch (e) { setSnackbar({ open: true, message: 'Error al eliminar', severity: 'error' }); }
  };

  const handleFileImport = async (e) => {
    const file = e.target.files[0];
    if (!file) return;
    const fd = new FormData();
    fd.append('file', file);
    fd.append('empresa_id', empresaId);
    try {
      await api.post('/upload/import/productos', fd, { headers: { 'Content-Type': 'multipart/form-data' } });
      fetchProductos();
      setSnackbar({ open: true, message: 'Importación exitosa', severity: 'success' });
    } catch (err) {
      setSnackbar({ open: true, message: err.response?.data?.detail || 'Error al importar', severity: 'error' });
    }
  };

  const columns = [
    { field: 'codigo', headerName: 'Código', flex: 1 },
    { field: 'nombre', headerName: 'Nombre', flex: 2 },
    { field: 'categoria', headerName: 'Categoría', flex: 1 },
    { field: 'precio', headerName: 'Precio', flex: 1, type: 'number' },
    { field: 'costo', headerName: 'Costo', flex: 1, type: 'number' },
    { field: 'stock', headerName: 'Stock', flex: 1, type: 'number' },
    { field: 'stock_minimo', headerName: 'Stock Mínimo', flex: 1, type: 'number' },
    { field: 'unidad_medida', headerName: 'Unidad', flex: 0.8 },
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
        <Typography variant="h5">Inventario / Productos</Typography>
        <Box>
          <Button variant="outlined" component="label" startIcon={<Upload />} sx={{ mr: 1 }}>
            Importar
            <input type="file" hidden accept=".xlsx,.csv" onChange={handleFileImport} />
          </Button>
          <Button variant="contained" startIcon={<Add />} onClick={() => { setForm({ id: null, codigo: '', nombre: '', descripcion: '', categoria: '', precio: 0, costo: 0, stock: 0, stock_minimo: 0, unidad_medida: 'unidad' }); setOpen(true); }}>
            Nuevo Producto
          </Button>
        </Box>
      </Box>
      <Paper sx={{ height: '70vh' }}>
        <DataGrid rows={productos} columns={columns} loading={loading} pageSizeOptions={[10, 25, 50]} disableRowSelectionOnClick />
      </Paper>
      <Dialog open={open} onClose={() => setOpen(false)} maxWidth="sm" fullWidth>
        <DialogTitle>{form.id ? 'Editar' : 'Nuevo'} Producto</DialogTitle>
        <DialogContent>
          <Grid container spacing={2} mt={1}>
            <Grid item xs={12} sm={6}><TextField label="Código" fullWidth value={form.codigo} onChange={(e) => setForm({ ...form, codigo: e.target.value })} /></Grid>
            <Grid item xs={12} sm={6}><TextField label="Nombre" fullWidth value={form.nombre} onChange={(e) => setForm({ ...form, nombre: e.target.value })} /></Grid>
            <Grid item xs={12}><TextField label="Descripción" fullWidth multiline rows={2} value={form.descripcion} onChange={(e) => setForm({ ...form, descripcion: e.target.value })} /></Grid>
            <Grid item xs={12} sm={6}><TextField label="Categoría" fullWidth value={form.categoria} onChange={(e) => setForm({ ...form, categoria: e.target.value })} /></Grid>
            <Grid item xs={12} sm={6}><TextField label="Unidad de Medida" fullWidth value={form.unidad_medida} onChange={(e) => setForm({ ...form, unidad_medida: e.target.value })} /></Grid>
            <Grid item xs={12} sm={4}><TextField label="Precio" type="number" fullWidth value={form.precio} onChange={(e) => setForm({ ...form, precio: parseFloat(e.target.value) || 0 })} /></Grid>
            <Grid item xs={12} sm={4}><TextField label="Costo" type="number" fullWidth value={form.costo} onChange={(e) => setForm({ ...form, costo: parseFloat(e.target.value) || 0 })} /></Grid>
            <Grid item xs={12} sm={4}><TextField label="Stock Mínimo" type="number" fullWidth value={form.stock_minimo} onChange={(e) => setForm({ ...form, stock_minimo: parseInt(e.target.value) || 0 })} /></Grid>
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

export default Productos;
