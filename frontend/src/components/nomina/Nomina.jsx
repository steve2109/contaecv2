import React, { useState, useEffect } from 'react';
import { Box, Typography, Paper, Button, Tabs, Tab, Snackbar, Alert } from '@mui/material';
import { DataGrid } from '@mui/x-data-grid';
import { People } from '@mui/icons-material';
import api from '../../api/axiosConfig';
import { useSelector } from 'react-redux';
import { Link } from 'react-router-dom';

const Nomina = () => {
  const [tab, setTab] = useState(0);
  const [roles, setRoles] = useState([]);
  const [empleados, setEmpleados] = useState([]);
  const [loading, setLoading] = useState(false);
  const [snackbar, setSnackbar] = useState({ open: false, message: '', severity: 'success' });
  const empresaId = useSelector((state) => state.empresa.empresaActiva);

  const fetchData = async () => {
    if (!empresaId) return;
    setLoading(true);
    try {
      const [r, e] = await Promise.all([
        api.get(`/nomina/roles?empresa_id=${empresaId}`),
        api.get(`/nomina/empleados?empresa_id=${empresaId}`)
      ]);
      setRoles(r.data.map(x => ({ ...x, id: x.id })));
      setEmpleados(e.data.map(x => ({ ...x, id: x.id })));
    } catch (e) {
      setSnackbar({ open: true, message: 'Error al cargar nómina', severity: 'error' });
    }
    setLoading(false);
  };

  useEffect(() => { fetchData(); }, [empresaId]);

  const roleCols = [
    { field: 'fecha_inicio', headerName: 'Periodo Inicio', flex: 1 },
    { field: 'fecha_fin', headerName: 'Periodo Fin', flex: 1 },
    { field: 'total_ingresos', headerName: 'Ingresos', flex: 1, type: 'number' },
    { field: 'total_descuentos', headerName: 'Descuentos', flex: 1, type: 'number' },
    { field: 'total_neto', headerName: 'Neto', flex: 1, type: 'number' },
    { field: 'estado', headerName: 'Estado', flex: 0.8 },
  ];

  const empCols = [
    { field: 'cedula', headerName: 'Cédula', flex: 1 },
    { field: 'nombres', headerName: 'Nombres', flex: 2 },
    { field: 'cargo', headerName: 'Cargo', flex: 1 },
    { field: 'salario_base', headerName: 'Salario', flex: 1, type: 'number' },
    { field: 'fecha_ingreso', headerName: 'Fecha Ingreso', flex: 1 },
    { field: 'estado', headerName: 'Estado', flex: 0.8 },
  ];

  return (
    <Box p={3}>
      <Typography variant="h5" gutterBottom><People sx={{ mr: 1, verticalAlign: 'middle' }} />Nómina / Recursos Humanos</Typography>
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={2}>
        <Tabs value={tab} onChange={(_, v) => setTab(v)}>
          <Tab label="Roles de Pago" />
          <Tab label="Empleados" />
        </Tabs>
        <Button variant="contained" component={Link} to="/empleados">Gestionar Empleados</Button>
      </Box>

      {tab === 0 && (
        <Paper sx={{ height: '60vh' }}>
          <DataGrid rows={roles} columns={roleCols} loading={loading} pageSizeOptions={[10, 25, 50]} disableRowSelectionOnClick />
        </Paper>
      )}

      {tab === 1 && (
        <Paper sx={{ height: '60vh' }}>
          <DataGrid rows={empleados} columns={empCols} loading={loading} pageSizeOptions={[10, 25, 50]} disableRowSelectionOnClick />
        </Paper>
      )}

      <Snackbar open={snackbar.open} autoHideDuration={4000} onClose={() => setSnackbar({ ...snackbar, open: false })}>
        <Alert severity={snackbar.severity}>{snackbar.message}</Alert>
      </Snackbar>
    </Box>
  );
};

export default Nomina;
