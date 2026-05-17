import { createTheme } from '@mui/material/styles';

// Colores del brand
const primaryColor = '#1a5276';  // Azul oscuro profesional
const secondaryColor = '#2980b9'; // Azul medio
const accentColor = '#3498db';    // Azul claro
const successColor = '#27ae60';   // Verde
const warningColor = '#f39c12';   // Naranja
const errorColor = '#e74c3c';     // Rojo

// Colores de modo claro suave (anti-fatiga visual)
const lightBackground = '#f5f7fa';
const lightSurface = '#ffffff';
const lightText = '#2c3e50';
const lightTextSecondary = '#5d6d7e';

// Colores de modo oscuro
const darkBackground = '#121212';
const darkSurface = '#1e1e1e';
const darkText = '#e0e0e0';
const darkTextSecondary = '#a0a0a0';

export const lightTheme = createTheme({
  palette: {
    mode: 'light',
    primary: {
      main: primaryColor,
      light: accentColor,
      dark: '#154360',
    },
    secondary: {
      main: secondaryColor,
      light: '#5dade2',
      dark: '#21618c',
    },
    background: {
      default: lightBackground,
      paper: lightSurface,
    },
    text: {
      primary: lightText,
      secondary: lightTextSecondary,
    },
    success: {
      main: successColor,
    },
    warning: {
      main: warningColor,
    },
    error: {
      main: errorColor,
    },
  },
  typography: {
    fontFamily: '"Roboto", "Helvetica", "Arial", sans-serif',
    h1: { fontWeight: 500, fontSize: '2rem' },
    h2: { fontWeight: 500, fontSize: '1.75rem' },
    h3: { fontWeight: 500, fontSize: '1.5rem' },
    h4: { fontWeight: 500, fontSize: '1.25rem' },
    h5: { fontWeight: 500, fontSize: '1.1rem' },
    h6: { fontWeight: 500, fontSize: '1rem' },
    body1: { fontSize: '0.95rem', lineHeight: 1.6 },
    body2: { fontSize: '0.875rem', lineHeight: 1.5 },
  },
  components: {
    MuiPaper: {
      styleOverrides: {
        root: {
          borderRadius: 8,
          boxShadow: '0 2px 8px rgba(0,0,0,0.08)',
        },
      },
    },
    MuiButton: {
      styleOverrides: {
        root: {
          borderRadius: 6,
          textTransform: 'none',
          fontWeight: 500,
        },
      },
    },
    MuiTextField: {
      styleOverrides: {
        root: {
          '& .MuiOutlinedInput-root': {
            borderRadius: 6,
          },
        },
      },
    },
    MuiCard: {
      styleOverrides: {
        root: {
          borderRadius: 8,
          boxShadow: '0 2px 8px rgba(0,0,0,0.08)',
        },
      },
    },
  },
});

export const darkTheme = createTheme({
  palette: {
    mode: 'dark',
    primary: {
      main: accentColor,
      light: '#5dade2',
      dark: primaryColor,
    },
    secondary: {
      main: '#5dade2',
      light: '#85c1e9',
      dark: secondaryColor,
    },
    background: {
      default: darkBackground,
      paper: darkSurface,
    },
    text: {
      primary: darkText,
      secondary: darkTextSecondary,
    },
    success: {
      main: '#2ecc71',
    },
    warning: {
      main: '#f1c40f',
    },
    error: {
      main: '#ec7063',
    },
  },
  typography: {
    fontFamily: '"Roboto", "Helvetica", "Arial", sans-serif',
    h1: { fontWeight: 500, fontSize: '2rem' },
    h2: { fontWeight: 500, fontSize: '1.75rem' },
    h3: { fontWeight: 500, fontSize: '1.5rem' },
    h4: { fontWeight: 500, fontSize: '1.25rem' },
    h5: { fontWeight: 500, fontSize: '1.1rem' },
    h6: { fontWeight: 500, fontSize: '1rem' },
    body1: { fontSize: '0.95rem', lineHeight: 1.6 },
    body2: { fontSize: '0.875rem', lineHeight: 1.5 },
  },
  components: {
    MuiPaper: {
      styleOverrides: {
        root: {
          borderRadius: 8,
          boxShadow: '0 2px 8px rgba(0,0,0,0.3)',
          backgroundColor: darkSurface,
        },
      },
    },
    MuiButton: {
      styleOverrides: {
        root: {
          borderRadius: 6,
          textTransform: 'none',
          fontWeight: 500,
        },
      },
    },
    MuiTextField: {
      styleOverrides: {
        root: {
          '& .MuiOutlinedInput-root': {
            borderRadius: 6,
            backgroundColor: '#2a2a2a',
          },
        },
      },
    },
    MuiCard: {
      styleOverrides: {
        root: {
          borderRadius: 8,
          boxShadow: '0 2px 8px rgba(0,0,0,0.3)',
          backgroundColor: darkSurface,
        },
      },
    },
    MuiDrawer: {
      styleOverrides: {
        paper: {
          backgroundColor: '#1a1a1a',
          borderRight: '1px solid #333',
        },
      },
    },
  },
});
