import React, { useState, useEffect } from 'react';
import { useTranslation } from 'react-i18next';
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
  Grid,
  Switch,
  FormControlLabel,
  Chip,
  LinearProgress,
  Tabs,
  Tab,
} from '@mui/material';
import { Add, Edit, Delete, CloudUpload } from '@mui/icons-material';
import api from '../../api/axiosConfig';

const Inventario = () => {
  const { t } = useTranslation();
  const [tab, setTab] = useState(0);
  const [productos, setProductos] = useState([]);
  const [categorias, setCategorias] = useState([]);
  const [loading, setLoading] = useState(false);
  const [open, setOpen] = useState(false);
  const [formData, setFormData] = useState({
    codigo: '', nombre: '', descripcion: '', categoria_id: '',
    precio_compra: 0, precio_venta: 0, stock: 0, stock_minimo: 0,
    unidad_medida: 'unidad', tiene_iva: true, activo: true,
  });

  useEffect(() => { loadProductos(); }, []);

  const loadProductos = async () => {
    setLoading(true);
    try {
      const response = await api.get('/productos');
      setProductos(response.data);
    } catch (error) { console.error('Error:', error); }
    setLoading(false);
  };

  return (
    <Box>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
        <Typography variant="h4" fontWeight="bold">{t('inventario.title')}</Typography>
        <Box>
          <Button variant="outlined" component="label" startIcon={<CloudUpload />} sx={{ mr: 1 }}>
            Importar
            <input type="file" accept=".xlsx,.csv" hidden onChange={(e) => {
              const formData = new FormData();
              formData.append('file', e.target.files[0]);
              api.post('/upload/importar-productos', formData).then(() => loadProductos());
            }} />
          </Button>
          <Button variant="contained" startIcon={<Add />} onClick={() => setOpen(true)}>
            {t('inventario.create')}
          </Button>
        </Box>
      </Box>

      <Tabs value={tab} onChange={(e, v) => setTab(v)} sx={{ mb: 2 }}>
        <Tab label="Productos" />
        <Tab label="Movimientos" />
        <Tab label="Categorías" />
      </Tabs>

      {tab === 0 && (
        <TableContainer component={Paper} elevation={2}>
          {loading && <LinearProgress />}
          <Table>
            <TableHead>
              <TableRow>
                <TableCell>Código</TableCell>
                <TableCell>Nombre</TableCell>
                <TableCell>Precio Compra</TableCell>
                <TableCell>Precio Venta</TableCell>
                <TableCell>Stock</TableCell>
                <TableCell>Estado</TableCell>
                <TableCell>Acciones</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {productos.map((p) => (
                <TableRow key={p.id} hover>
                  <TableCell>{p.codigo}</TableCell>
                  <TableCell>{p.nombre}</TableCell>
                  <TableCell>${p.precio_compra?.toFixed(2)}</TableCell>
                  <TableCell>${p.precio_venta?.toFixed(2)}</TableCell>
                  <TableCell>
                    <Chip label={p.stock} color={p.stock <= p.stock_minimo ? 'error' : 'success'} size="small" />
                  </TableCell>
                  <TableCell><Chip label={p.activo ? 'Activo' : 'Inactivo'} color={p.activo ? 'success' : 'default'} size="small" /></TableCell>
                  <TableCell>
                    <IconButton><Edit /></IconButton>
                    <IconButton color="error"><Delete /></IconButton>
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

export default Inventario;
