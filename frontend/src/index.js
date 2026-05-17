import React from 'react';
import ReactDOM from 'react-dom/client';
import { BrowserRouter } from 'react-router-dom';
import { ThemeProvider } from '@mui/material/styles';
import { CssBaseline } from '@mui/material';
import { Provider } from 'react-redux';
import { store } from './store';
import App from './App';
import { lightTheme, darkTheme } from './theme';
import './i18n';

const root = ReactDOM.createRoot(document.getElementById('root'));

function Main() {
  const [darkMode, setDarkMode] = React.useState(
    localStorage.getItem('theme') === 'dark'
  );

  React.useEffect(() => {
    const handler = () => {
      setDarkMode(localStorage.getItem('theme') === 'dark');
    };
    window.addEventListener('storage', handler);
    return () => window.removeEventListener('storage', handler);
  }, []);

  return (
    <Provider store={store}>
      <ThemeProvider theme={darkMode ? darkTheme : lightTheme}>
        <CssBaseline />
        <BrowserRouter>
          <App />
        </BrowserRouter>
      </ThemeProvider>
    </Provider>
  );
}

root.render(
  <React.StrictMode>
    <Main />
  </React.StrictMode>
);
