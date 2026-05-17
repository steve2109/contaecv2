import React, { useState, useEffect } from 'react';
import { useTranslation } from 'react-i18next';
import {
  Box, Typography, Button, Paper, Table, TableBody, TableCell,
  TableContainer, TableHead, TableRow, IconButton, Chip, Dialog,
  DialogTitle, DialogContent, DialogActions, TextField, Grid,
  Autocomplete, Divider, LinearProgress,
} from '@mui/material';
import { Add, Visibility, Download, Send } from '@mui/icons-material';
import api from '../../api/axiosConfig';

const Facturas = () => {
  const { t } = useTranslation();
  const [facturas, setFacturas] = useState([]);
  const [open, setOpen] = useState(false);
  const [loading, setLoading] = useState(false);
  const [clientes, setClientes] = useState([]);
  const [productos, setProductos] = useState([]);
  const [detalles, setDetalles] = useState([{ producto_id: '', cantidad: 1, precio_unitario: 0, descuento: 0 }]);

  useEffect(() => { loadFacturas(); }, []);

  const loadFacturas = async () => {
    setLoading(true);
    try {
      const response = await api.get('/facturas');
      setFacturas(response.data);
    } catch (error) { console.error('Error:', error); }
    setLoading(false);
  };

  const enviarSRI = async (id) => {
    try {
      await api.post(`/facturas/${id}/enviar-sri`);
      loadFacturas();
    } catch (error) { console.error('Error:', error); }
  };

  const getEstadoColor = (estado) => {
    switch (estado) {
      case 'AUTORIZADA': return 'success';
      case 'PENDIENTE': return 'warning';
      case 'RECHAZADA': return 'error';
      case 'ANULADA': return 'default';
      default: return 'info';
    }
  };

  return (
    <Box>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
        <Typography variant="h4" fontWeight="bold">{t('facturas.title')}</Typography>
        <Button variant="contained" startIcon={<Add />} onClick={() => setOpen(true)}>
          {t('facturas.create')}
        </Button>
      </Box>

      {loading && <LinearProgress sx={{ mb: 2 }} />}

      <TableContainer component={Paper} elevation={2}>
        <Table>
          <TableHead>
            <TableRow>
              <TableCell>Número</TableCell>
              <TableCell>Cliente</TableCell>
              <TableCell>Fecha</TableCell>
              <TableCell>Total</TableCell>
              <TableCell>Estado</TableCell>
              <TableCell>Acciones</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {facturas.map((f) => (
              <TableRow key={f.id} hover>
                <TableCell>{f.numero}</TableCell>
                <TableCell>{f.cliente?.razon_social}</TableCell>
                <TableCell>{f.fecha}</TableCell>
                <TableCell>${f.total?.toFixed(2)}</TableCell>
                <TableCell>
                  <Chip label={f.estado} color={getEstadoColor(f.estado)} size="small" />
                </TableCell>
                <TableCell>
                  <IconButton><Visibility /></IconButton>
                  {f.estado === 'CREADA' && (
                    <IconButton color="primary" onClick={() => enviarSRI(f.id)}><Send /></IconButton>
                  )}
                  <IconButton><Download /></IconButton>
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </TableContainer>
    </Box>
  );
};

export default Facturas;
