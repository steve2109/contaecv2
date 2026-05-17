import React, { useState } from 'react';
import { useSelector, useDispatch } from 'react-redux';
import { useNavigate, useLocation } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import {
  Box,
  Drawer,
  AppBar,
  Toolbar,
  List,
  Typography,
  Divider,
  IconButton,
  ListItem,
  ListItemButton,
  ListItemIcon,
  ListItemText,
  Avatar,
  Menu,
  MenuItem,
  Badge,
  Tooltip,
  Select,
  FormControl,
} from '@mui/material';
import {
  Menu as MenuIcon,
  Dashboard,
  Business,
  People,
  Inventory,
  Receipt,
  AccountBalance,
  Work,
  Person,
  Settings,
  AdminPanelSettings,
  Logout,
  Brightness4,
  Brightness7,
  Translate,
  Notifications,
  ChevronLeft,
} from '@mui/icons-material';
import { logout } from '../../features/authSlice';
import { toggleSidebar, setTheme, setLanguage } from '../../features/uiSlice';

const drawerWidth = 260;

const menuItems = [
  { path: '/dashboard', icon: Dashboard, label: 'nav.dashboard' },
  { path: '/empresas', icon: Business, label: 'nav.empresas' },
  { path: '/clientes', icon: People, label: 'nav.clientes' },
  { path: '/inventario', icon: Inventory, label: 'nav.inventario' },
  { path: '/facturas', icon: Receipt, label: 'nav.facturas' },
  { path: '/contabilidad', icon: AccountBalance, label: 'nav.contabilidad' },
  { path: '/empleados', icon: Work, label: 'nav.empleados' },
  { path: '/nomina', icon: Receipt, label: 'nav.nomina' },
  { path: '/configuracion', icon: Settings, label: 'nav.configuracion' },
  { path: '/admin', icon: AdminPanelSettings, label: 'nav.admin', admin: true },
];

const Layout = ({ children }) => {
  const { t, i18n } = useTranslation();
  const dispatch = useDispatch();
  const navigate = useNavigate();
  const location = useLocation();
  const { sidebarOpen, theme, language } = useSelector((state) => state.ui);
  const { user } = useSelector((state) => state.auth);
  const { empresas, empresaActiva } = useSelector((state) => state.empresa);

  const [anchorEl, setAnchorEl] = useState(null);
  const [notificationAnchor, setNotificationAnchor] = useState(null);

  const handleProfileMenuOpen = (event) => setAnchorEl(event.currentTarget);
  const handleMenuClose = () => setAnchorEl(null);
  const handleNotificationsOpen = (event) => setNotificationAnchor(event.currentTarget);
  const handleNotificationsClose = () => setNotificationAnchor(null);

  const handleLogout = () => {
    dispatch(logout());
    navigate('/login');
  };

  const handleThemeToggle = () => {
    const newTheme = theme === 'light' ? 'dark' : 'light';
    dispatch(setTheme(newTheme));
    localStorage.setItem('theme', newTheme);
    window.dispatchEvent(new Event('storage'));
  };

  const handleLanguageChange = (e) => {
    const lang = e.target.value;
    i18n.changeLanguage(lang);
    dispatch(setLanguage(lang));
  };

  const isActive = (path) => location.pathname.startsWith(path);

  return (
    <Box sx={{ display: 'flex' }}>
      <AppBar
        position="fixed"
        sx={{
          width: { md: sidebarOpen ? `calc(100% - ${drawerWidth}px)` : '100%' },
          ml: { md: sidebarOpen ? `${drawerWidth}px` : 0 },
          transition: 'width 0.3s',
          boxShadow: 1,
        }}
      >
        <Toolbar>
          <IconButton
            color="inherit"
            edge="start"
            onClick={() => dispatch(toggleSidebar())}
            sx={{ mr: 2 }}
          >
            {sidebarOpen ? <ChevronLeft /> : <MenuIcon />}
          </IconButton>
          <Typography variant="h6" noWrap component="div" sx={{ flexGrow: 1 }}>
            ContaEC
          </Typography>

          <FormControl size="small" sx={{ minWidth: 100, mr: 2 }}>
            <Select
              value={empresaActiva || ''}
              displayEmpty
              variant="standard"
              sx={{ color: 'inherit', '&:before': { borderBottom: 'none' } }}
            >
              <MenuItem value="" disabled>
                {t('empresas.selectEmpresa')}
              </MenuItem>
              {empresas.map((emp) => (
                <MenuItem key={emp.id} value={emp.id}>
                  {emp.razon_social}
                </MenuItem>
              ))}
            </Select>
          </FormControl>

          <IconButton color="inherit" onClick={handleNotificationsOpen}>
            <Badge badgeContent={0} color="error">
              <Notifications />
            </Badge>
          </IconButton>

          <IconButton color="inherit" onClick={handleThemeToggle}>
            {theme === 'light' ? <Brightness4 /> : <Brightness7 />}
          </IconButton>

          <IconButton color="inherit" onClick={handleProfileMenuOpen}>
            <Avatar sx={{ width: 32, height: 32, bgcolor: 'secondary.main' }}>
              {user?.nombres?.[0] || 'U'}
            </Avatar>
          </IconButton>

          <Menu
            anchorEl={anchorEl}
            open={Boolean(anchorEl)}
            onClose={handleMenuClose}
          >
            <MenuItem onClick={() => { navigate('/configuracion'); handleMenuClose(); }}>
              <ListItemIcon><Settings fontSize="small" /></ListItemIcon>
              {t('configuracion.perfil')}
            </MenuItem>
            <MenuItem onClick={() => { navigate('/empresas'); handleMenuClose(); }}>
              <ListItemIcon><Business fontSize="small" /></ListItemIcon>
              {t('nav.empresas')}
            </MenuItem>
            <Divider />
            <MenuItem onClick={handleLogout}>
              <ListItemIcon><Logout fontSize="small" color="error" /></ListItemIcon>
              <Typography color="error">{t('nav.logout')}</Typography>
            </MenuItem>
          </Menu>
        </Toolbar>
      </AppBar>

      <Drawer
        variant="persistent"
        anchor="left"
        open={sidebarOpen}
        sx={{
          width: drawerWidth,
          flexShrink: 0,
          '& .MuiDrawer-paper': {
            width: drawerWidth,
            boxSizing: 'border-box',
          },
        }}
      >
        <Toolbar>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
            <Avatar sx={{ bgcolor: 'primary.main' }}>
              <Business />
            </Avatar>
            <Box>
              <Typography variant="subtitle1" fontWeight="bold">
                ContaEC
              </Typography>
              <Typography variant="caption" color="text.secondary">
                v1.0.0
              </Typography>
            </Box>
          </Box>
        </Toolbar>
        <Divider />
        <List sx={{ pt: 1 }}>
          {menuItems.map((item) => {
            if (item.admin && user?.email !== 'steve.mejia@tymtechnology.shop') return null;
            const Icon = item.icon;
            return (
              <ListItem key={item.path} disablePadding>
                <ListItemButton
                  selected={isActive(item.path)}
                  onClick={() => navigate(item.path)}
                  sx={{
                    borderRadius: 1,
                    mx: 1,
                    mb: 0.5,
                    '&.Mui-selected': {
                      bgcolor: 'primary.main',
                      color: 'primary.contrastText',
                      '&:hover': { bgcolor: 'primary.dark' },
                      '& .MuiListItemIcon-root': { color: 'primary.contrastText' },
                    },
                  }}
                >
                  <ListItemIcon sx={{ minWidth: 40 }}>
                    <Icon />
                  </ListItemIcon>
                  <ListItemText primary={t(item.label)} />
                </ListItemButton>
              </ListItem>
            );
          })}
        </List>
      </Drawer>

      <Box
        component="main"
        sx={{
          flexGrow: 1,
          p: 3,
          mt: 8,
          minHeight: '100vh',
          bgcolor: 'background.default',
          transition: 'margin 0.3s',
          ml: sidebarOpen ? 0 : `-${drawerWidth}px`,
        }}
      >
        {children}
      </Box>
    </Box>
  );
};

export default Layout;
