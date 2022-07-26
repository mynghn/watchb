import Axios from "axios";
import store, { login, setToken, setUser } from "./store";

export const BACKEND_HOST = process.env.REACT_APP_BACKEND_HOST;
export const SIGN_UP_URI = "/api/accounts/";
export const JWT_OBTAIN_URI = "/api/accounts/jwt/";
export const JWT_REFRESH_URI = "/api/accounts/jwt/refresh/";

export const axios = Axios.create({
  baseURL: BACKEND_HOST,
  withCredentials: true,
  xsrfCookieName: "csrftoken",
  xsrfHeaderName: "X-CSRFToken",
});

const onSignUpSucess = async (signUpResponse, email, password) => {
  const {
    data: { id: userId, username },
  } = signUpResponse;
  obtainJWT(email, password);
  store.dispatch(setUser({ userId, username }));
  store.dispatch(login());
};
export const signUp = (username, email, password) => {
  axios
    .post(SIGN_UP_URI, {
      username,
      email,
      password,
    })
    .then((response) => onSignUpSucess(response, email, password));
};

const onObtainJWTSuccess = (obtainJWTResponse) => {
  const {
    data: { access: accessToken },
  } = obtainJWTResponse;
  store.dispatch(setToken(accessToken));
};
export const obtainJWT = (email, password) =>
  axios
    .post(JWT_OBTAIN_URI, { email, password })
    .then((response) => onObtainJWTSuccess(response));
