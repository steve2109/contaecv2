import { createSlice, createAsyncThunk } from '@reduxjs/toolkit';
import api from '../api/axiosConfig';

export const fetchEmpresas = createAsyncThunk(
  'empresa/fetchEmpresas',
  async (_, { rejectWithValue }) => {
    try {
      const response = await api.get('/empresas');
      return response.data;
    } catch (error) {
      return rejectWithValue(error.response?.data || error.message);
    }
  }
);

export const setEmpresaActiva = createAsyncThunk(
  'empresa/setEmpresaActiva',
  async (empresaId, { rejectWithValue }) => {
    try {
      localStorage.setItem('empresaId', empresaId);
      return empresaId;
    } catch (error) {
      return rejectWithValue(error.message);
    }
  }
);

const empresaSlice = createSlice({
  name: 'empresa',
  initialState: {
    empresas: [],
    empresaActiva: localStorage.getItem('empresaId') || null,
    loading: false,
    error: null,
  },
  reducers: {
    clearEmpresaError: (state) => {
      state.error = null;
    },
  },
  extraReducers: (builder) => {
    builder
      .addCase(fetchEmpresas.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(fetchEmpresas.fulfilled, (state, action) => {
        state.loading = false;
        state.empresas = action.payload;
      })
      .addCase(fetchEmpresas.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload;
      })
      .addCase(setEmpresaActiva.fulfilled, (state, action) => {
        state.empresaActiva = action.payload;
      });
  },
});

export const { clearEmpresaError } = empresaSlice.actions;
export default empresaSlice.reducer;
