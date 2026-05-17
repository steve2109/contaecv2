import React, { useState } from 'react';
import { useTranslation } from 'react-i18next';
import { useDispatch } from 'react-redux';
import {
  Box, Typography, Paper, Tabs, Tab, TextField, Button, Switch,
  FormControlLabel, Divider, Alert, Grid, Card, CardContent,
} from '@mui/material';
import {
  Save, Email, Backup, Security, Palette, Language,
} from '@mui/icons-material';
import { setTheme } from '../../features/uiSlice';
import api from '../../api/axiosConfig';

const Configuracion = () => {
  const { t, i18n } = useTranslation();
  const dispatch = useDispatch();
  const [tab, setTab] = useState(0);
  const [emailConfig, setEmailConfig] = useState({
    smtp_host: '', smtp_port: 587, smtp_user: '', smtp_pass: '', use_tls: true,
  });
  const [backupKey, setBackupKey] = useState('');
  const [theme, setLocalTheme] = useState(localStorage.getItem('theme') || 'light');
  const [message, setMessage] = useState(null);

  const handleSaveEmail = async () => {
    try {
      await api.post('/configuracion/email', emailConfig);
      setMessage({ type: 'success', text: 'Configuración de email guardada' });
    } catch (error) {
      setMessage({ type: 'error', text: 'Error al guardar' });
    }
  };

  const handleGenerateBackup = async () => {
    try {
      await api.post('/backup/generar', { clave_encriptacion: backupKey });
      setMessage({ type: 'success', text: 'Backup generado correctamente' });
    } catch (error) {
      setMessage({ type: 'error', text: 'Error al generar backup' });
    }
  };

  const handleThemeChange = (newTheme) => {
    setLocalTheme(newTheme);
    dispatch(setTheme(newTheme));
    localStorage.setItem('theme', newTheme);
    window.dispatchEvent(new Event('storage'));
  };

  const handleLanguageChange = (lang) => {
    i18n.changeLanguage(lang);
  };

  return (
    <Box>
      <Typography variant="h4" fontWeight="bold" gutterBottom>
        {t('configuracion.title')}
      </Typography>

      {message && (
        <Alert severity={message.type} sx={{ mb: 3 }} onClose={() => setMessage(null)}>
          {message.text}
        </Alert>
      )}

      <Tabs value={tab} onChange={(e, v) => setTab(v)} sx={{ mb: 3 }}>
        <Tab label="Perfil" icon={<Security />} iconPosition="start" />
        <Tab label={t('configuracion.email')} icon={<Email />} iconPosition="start" />
        <Tab label={t('configuracion.backup')} icon={<Backup />} iconPosition="start" />
        <Tab label="Apariencia" icon={<Palette />} iconPosition="start" />
        <Tab label="Idioma" icon={<Language />} iconPosition="start" />
      </Tabs>

      {tab === 1 && (
        <Paper elevation={2} sx={{ p: 3 }}>
          <Typography variant="h6" gutterBottom>Configuración de Email</Typography>
          <Grid container spacing={2}>
            <Grid item xs={12} sm={6}>
              <TextField
                fullWidth label="Servidor SMTP" value={emailConfig.smtp_host}
                onChange={(e) => setEmailConfig({ ...emailConfig, smtp_host: e.target.value })}
              />
            </Grid>
            <Grid item xs={12} sm={6}>
              <TextField
                fullWidth label="Puerto SMTP" type="number" value={emailConfig.smtp_port}
                onChange={(e) => setEmailConfig({ ...emailConfig, smtp_port: parseInt(e.target.value) })}
              />
            </Grid>
            <Grid item xs={12} sm={6}>
              <TextField
                fullWidth label="Usuario SMTP" value={emailConfig.smtp_user}
                onChange={(e) => setEmailConfig({ ...emailConfig, smtp_user: e.target.value })}
              />
            </Grid>
            <Grid item xs={12} sm={6}>
              <TextField
                fullWidth label="Contraseña SMTP" type="password" value={emailConfig.smtp_pass}
                onChange={(e) => setEmailConfig({ ...emailConfig, smtp_pass: e.target.value })}
              />
            </Grid>
            <Grid item xs={12}>
              <FormControlLabel
                control={<Switch checked={emailConfig.use_tls} onChange={(e) => setEmailConfig({ ...emailConfig, use_tls: e.target.checked })} />}
                label="Usar TLS"
              />
            </Grid>
          </Grid>
          <Box sx={{ mt: 3 }}>
            <Button variant="contained" startIcon={<Save />} onClick={handleSaveEmail}>
              Guardar Configuración
            </Button>
            <Button variant="outlined" sx={{ ml: 2 }} onClick={() => api.post('/configuracion/email/test')}>
              Probar Configuración
            </Button>
          </Box>
        </Paper>
      )}

      {tab === 2 && (
        <Paper elevation={2} sx={{ p: 3 }}>
          <Typography variant="h6" gutterBottom>{t('configuracion.backup')}</Typography>
          <Alert severity="info" sx={{ mb: 3 }}>
            La clave de encriptación se usará para cifrar tus backups. Guárdala en un lugar seguro.
          </Alert>
          <TextField
            fullWidth type="password" label={t('configuracion.backupKey')}
            value={backupKey} onChange={(e) => setBackupKey(e.target.value)}
            sx={{ mb: 3 }}
          />
          <Button variant="contained" startIcon={<Backup />} onClick={handleGenerateBackup}>
            {t('configuracion.generarBackup')}
          </Button>
          <Divider sx={{ my: 3 }} />
          <Typography variant="h6" gutterBottom>Restaurar Backup</Typography>
          <Button variant="outlined" component="label">
            Seleccionar Archivo de Backup
            <input type="file" hidden accept=".zip,.enc" onChange={(e) => {
              const formData = new FormData();
              formData.append('file', e.target.files[0]);
              api.post('/backup/restaurar', formData).then(() => setMessage({ type: 'success', text: 'Backup restaurado' }));
            }} />
          </Button>
        </Paper>
      )}

      {tab === 3 && (
        <Paper elevation={2} sx={{ p: 3 }}>
          <Typography variant="h6" gutterBottom>Tema Visual</Typography>
          <Grid container spacing={2}>
            <Grid item xs={12} sm={6}>
              <Card
                sx={{
                  cursor: 'pointer',
                  border: theme === 'light' ? '2px solid #1a5276' : 'none',
                  bgcolor: '#f5f7fa',
                }}
                onClick={() => handleThemeChange('light')}
              >
                <CardContent>
                  <Typography variant="h6" sx={{ color: '#2c3e50' }}>Modo Claro</Typography>
                  <Typography variant="body2" sx={{ color: '#5d6d7e' }}>
                    Colores suaves diseñados para reducir la fatiga visual
                  </Typography>
                </CardContent>
              </Card>
            </Grid>
            <Grid item xs={12} sm={6}>
              <Card
                sx={{
                  cursor: 'pointer',
                  border: theme === 'dark' ? '2px solid #3498db' : 'none',
                  bgcolor: '#1e1e1e',
                }}
                onClick={() => handleThemeChange('dark')}
              >
                <CardContent>
                  <Typography variant="h6" sx={{ color: '#e0e0e0' }}>Modo Oscuro</Typography>
                  <Typography variant="body2" sx={{ color: '#a0a0a0' }}>
                    Ideal para trabajar en ambientes con poca luz
                  </Typography>
                </CardContent>
              </Card>
            </Grid>
          </Grid>
        </Paper>
      )}

      {tab === 4 && (
        <Paper elevation={2} sx={{ p: 3 }}>
          <Typography variant="h6" gutterBottom>Idioma</Typography>
          <Grid container spacing={2}>
            <Grid item xs={12} sm={6}>
              <Card
                sx={{
                  cursor: 'pointer',
                  border: i18n.language === 'es' ? '2px solid #1a5276' : 'none',
                }}
                onClick={() => handleLanguageChange('es')}
              >
                <CardContent>
                  <Typography variant="h6">Español</Typography>
                  <Typography variant="body2" color="text.secondary">
                    Español de Ecuador (predeterminado)
                  </Typography>
                </CardContent>
              </Card>
            </Grid>
            <Grid item xs={12} sm={6}>
              <Card
                sx={{
                  cursor: 'pointer',
                  border: i18n.language === 'en' ? '2px solid #1a5276' : 'none',
                }}
                onClick={() => handleLanguageChange('en')}
              >
                <CardContent>
                  <Typography variant="h6">English</Typography>
                  <Typography variant="body2" color="text.secondary">
                    English language
                  </Typography>
                </CardContent>
              </Card>
            </Grid>
          </Grid>
        </Paper>
      )}
    </Box>
  );
};

export default Configuracion;
