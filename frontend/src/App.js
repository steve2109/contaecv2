import React, { useEffect } from 'react';
import { Routes, Route, Navigate } from 'react-router-dom';
import { useSelector } from 'react-redux';
import { ToastContainer } from 'react-toastify';
import 'react-toastify/dist/ReactToastify.css';

import Login from './components/auth/Login';
import Dashboard from './components/dashboard/Dashboard';
import Layout from './components/layout/Layout';
import Empresas from './components/empresas/Empresas';
import Clientes from './components/clientes/Clientes';
import Productos from './components/inventario/Productos';
import Facturas from './components/facturas/Facturas';
import Contabilidad from './components/contabilidad/Contabilidad';
import Nomina from './components/nomina/Nomina';
import Empleados from './components/nomina/Empleados';
import AdminPanel from './components/admin/AdminPanel';
import Configuracion from './components/configuracion/Configuracion';
import PrivateRoute from './components/auth/PrivateRoute';

function App() {
  const { token } = useSelector((state) => state.auth);

  return (
    <>
      <ToastContainer
        position="top-right"
        autoClose={5000}
        hideProgressBar={false}
        newestOnTop={false}
        closeOnClick
        rtl={false}
        pauseOnFocusLoss
        draggable
        pauseOnHover
        theme="colored"
      />
      <Routes>
        <Route path="/login" element={<Login />} />
        <Route
          path="/*"
          element={
            <PrivateRoute>
              <Layout>
                <Routes>
                  <Route path="/" element={<Navigate to="/dashboard" replace />} />
                  <Route path="/dashboard" element={<Dashboard />} />
                  <Route path="/empresas" element={<Empresas />} />
                  <Route path="/clientes" element={<Clientes />} />
                  <Route path="/inventario" element={<Productos />} />
                  <Route path="/facturas" element={<Facturas />} />
                  <Route path="/contabilidad" element={<Contabilidad />} />
                  <Route path="/nomina" element={<Nomina />} />
                  <Route path="/empleados" element={<Empleados />} />
                  <Route path="/configuracion" element={<Configuracion />} />
                  <Route path="/admin/*" element={<AdminPanel />} />
                </Routes>
              </Layout>
            </PrivateRoute>
          }
        />
      </Routes>
    </>
  );
}

export default App;
