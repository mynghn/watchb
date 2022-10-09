import { configureStore, createSlice } from "@reduxjs/toolkit";

const authSlice = createSlice({
  name: "auth",
  initialState: {
    isAuthenticated: false,
    accessToken: null,
    user: {},
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
      user: { ...state.user, ...action.payload },
    }),
    logout: (state) => ({
      isAuthenticated: false,
      accessToken: null,
      user: {},
    }),
  },
});

const moviesSlice = createSlice({
  name: "movies",
  initialState: {
    movie: {},
  },
  reducers: {
    setMovie: (state, action) => ({
      ...state,
      movie: { ...state.movie, ...action.payload },
    }),
    detachMovie: (state) => ({
      ...state,
      movie: {},
    }),
  },
});

export const { login, setToken, setUser, logout } = authSlice.actions;
export const { setMovie, detachMovie } = moviesSlice.actions;

export default configureStore({
  reducer: { auth: authSlice.reducer, movies: moviesSlice.reducer },
});
