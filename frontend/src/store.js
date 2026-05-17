import { configureStore } from '@reduxjs/toolkit';
import authReducer from './features/authSlice';
import empresaReducer from './features/empresaSlice';
import uiReducer from './features/uiSlice';

export const store = configureStore({
  reducer: {
    auth: authReducer,
    empresa: empresaReducer,
    ui: uiReducer,
  },
});
