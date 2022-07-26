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
    login: (state) => ({
      ...state,
      isAuthenticated: true,
    }),
    setToken: (state, action) => ({
      ...state,
      accessToken: action.payload,
    }),
    setUser: (state, action) => ({
      ...state,
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

export const { login, setToken, setUser, logout } = authSlice.actions;

export default configureStore({ reducer: { auth: authSlice.reducer } });
