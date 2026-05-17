import React, { useEffect } from 'react';
import { useTranslation } from 'react-i18next';
import { useSelector, useDispatch } from 'react-redux';
import {
  Grid,
  Paper,
  Typography,
  Box,
  Card,
  CardContent,
  LinearProgress,
  Alert,
  Chip,
} from '@mui/material';
import {
  Business,
  People,
  Inventory,
  Receipt,
  AccountBalance,
  Warning,
} from '@mui/icons-material';
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
  PieChart,
  Pie,
  Cell,
  LineChart,
  Line,
} from 'recharts';
import { fetchEmpresas } from '../../features/empresaSlice';

const COLORS = ['#1a5276', '#2980b9', '#3498db', '#5dade2', '#85c1e9'];

const StatCard = ({ title, value, icon: Icon, color, subtitle }) => (
  <Card elevation={2}>
    <CardContent>
      <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
        <Box>
          <Typography color="text.secondary" variant="body2" gutterBottom>
            {title}
          </Typography>
          <Typography variant="h4" fontWeight="bold">
            {value}
          </Typography>
          {subtitle && (
            <Typography variant="caption" color="text.secondary">
              {subtitle}
            </Typography>
          )}
        </Box>
        <Box
          sx={{
            bgcolor: `${color}.light`,
            borderRadius: 2,
            p: 1.5,
            display: 'flex',
          }}
        >
          <Icon sx={{ color: `${color}.main`, fontSize: 32 }} />
        </Box>
      </Box>
    </CardContent>
  </Card>
);

const sampleData = {
  ventasMensuales: [
    { mes: 'Ene', ventas: 4500 },
    { mes: 'Feb', ventas: 5200 },
    { mes: 'Mar', ventas: 4800 },
    { mes: 'Abr', ventas: 6100 },
    { mes: 'May', ventas: 5800 },
    { mes: 'Jun', ventas: 7200 },
  ],
  productosTop: [
    { nombre: 'Producto A', ventas: 120 },
    { nombre: 'Producto B', ventas: 98 },
    { nombre: 'Producto C', ventas: 86 },
    { nombre: 'Producto D', ventas: 54 },
    { nombre: 'Producto E', ventas: 43 },
  ],
  estadoFacturas: [
    { name: 'Autorizadas', value: 85 },
    { name: 'Pendientes', value: 10 },
    { name: 'Rechazadas', value: 5 },
  ],
};

const Dashboard = () => {
  const { t } = useTranslation();
  const dispatch = useDispatch();
  const { user } = useSelector((state) => state.auth);
  const { empresas, empresaActiva } = useSelector((state) => state.empresa);

  useEffect(() => {
    dispatch(fetchEmpresas());
  }, [dispatch]);

  // Verificar licencia próxima a vencer (mock)
  const licenciaProxima = true;
  const diasRestantes = 15;

  return (
    <Box>
      <Typography variant="h4" gutterBottom fontWeight="bold">
        Dashboard
      </Typography>

      {licenciaProxima && (
        <Alert severity="warning" sx={{ mb: 3 }}>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
            <Warning />
            <Typography>
              Tu licencia está próxima a vencer. Quedan {diasRestantes} días.
              <Chip
                label="Renovar"
                color="warning"
                size="small"
                sx={{ ml: 1, cursor: 'pointer' }}
                onClick={() => window.open('https://wa.me/593960068866?text=Quiero%20renovar%20mi%20licencia%20por%20mes', '_blank')}
              />
            </Typography>
          </Box>
        </Alert>
      )}

      {!empresaActiva && (
        <Alert severity="info" sx={{ mb: 3 }}>
          {t('empresas.noEmpresas')} {t('empresas.createFirst')}
        </Alert>
      )}

      <Grid container spacing={3} sx={{ mb: 3 }}>
        <Grid item xs={12} sm={6} md={3}>
          <StatCard
            title="Empresas"
            value={empresas.length}
            icon={Business}
            color="primary"
          />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <StatCard
            title="Clientes"
            value={128}
            icon={People}
            color="info"
          />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <StatCard
            title="Productos"
            value={45}
            icon={Inventory}
            color="success"
          />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <StatCard
            title="Facturas (Mes)"
            value={32}
            icon={Receipt}
            color="warning"
            subtitle="$ 24,580.00"
          />
        </Grid>
      </Grid>

      <Grid container spacing={3}>
        <Grid item xs={12} md={8}>
          <Paper elevation={2} sx={{ p: 3, borderRadius: 2 }}>
            <Typography variant="h6" gutterBottom>
              Ventas Mensuales
            </Typography>
            <ResponsiveContainer width="100%" height={300}>
              <BarChart data={sampleData.ventasMensuales}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="mes" />
                <YAxis />
                <Tooltip />
                <Bar dataKey="ventas" fill="#1a5276" radius={[4, 4, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </Paper>
        </Grid>

        <Grid item xs={12} md={4}>
          <Paper elevation={2} sx={{ p: 3, borderRadius: 2 }}>
            <Typography variant="h6" gutterBottom>
              Estado de Facturas
            </Typography>
            <ResponsiveContainer width="100%" height={300}>
              <PieChart>
                <Pie
                  data={sampleData.estadoFacturas}
                  cx="50%"
                  cy="50%"
                  labelLine={false}
                  label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`}
                  outerRadius={80}
                  dataKey="value"
                >
                  {sampleData.estadoFacturas.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={COLORS[index]} />
                  ))}
                </Pie>
                <Tooltip />
              </PieChart>
            </ResponsiveContainer>
          </Paper>
        </Grid>

        <Grid item xs={12}>
          <Paper elevation={2} sx={{ p: 3, borderRadius: 2 }}>
            <Typography variant="h6" gutterBottom>
              Productos Más Vendidos
            </Typography>
            <ResponsiveContainer width="100%" height={250}>
              <BarChart data={sampleData.productosTop} layout="vertical">
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis type="number" />
                <YAxis dataKey="nombre" type="category" width={100} />
                <Tooltip />
                <Bar dataKey="ventas" fill="#2980b9" radius={[0, 4, 4, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </Paper>
        </Grid>
      </Grid>
    </Box>
  );
};

export default Dashboard;
