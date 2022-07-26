import { configureStore, createSlice } from "@reduxjs/toolkit";

const authSlice = createSlice({
  name: "auth",
  initialState: { isAuthenticated: false, accessToken: null },
  reducers: {
    login: (state, action) => ({
      ...state,
      isAuthenticated: true,
      accessToken: action.payload,
    }),
    logout: (state) => ({
      ...state,
      isAuthenticated: false,
      accessToken: null,
    }),
  },
});

export const { login, logout } = authSlice.actions;

export default configureStore({ reducer: { auth: authSlice.reducer } });
