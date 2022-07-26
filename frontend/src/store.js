import { configureStore, createSlice } from "@reduxjs/toolkit";

const authSlice = createSlice({
  name: "auth",
  initialState: {
    isAuthenticated: false,
    accessToken: null,
    userId: null,
    username: null,
  },
  reducers: {
    login: (state, action) => ({
      ...state,
      isAuthenticated: true,
      accessToken: action.payload.accessToken,
      userId: action.payload.userId,
      username: action.payload.username,
    }),
    logout: (state) => ({
      ...state,
      isAuthenticated: false,
      accessToken: null,
      userId: null,
      username: null,
    }),
  },
});

export const { login, logout } = authSlice.actions;

export default configureStore({ reducer: { auth: authSlice.reducer } });
