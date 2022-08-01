import Axios from "axios";
import jwtDecode from "jwt-decode";
import store, { login, setToken, setUser } from "./store";

export const BACKEND_HOST = process.env.REACT_APP_BACKEND_HOST;
export const JWT_EXPIRY_TIME =
  parseInt(process.env.REACT_APP_JWT_EXPIRY_TIME) || 1000 * 60 * 5;

export const USERS_URI = "/api/users/";
export const OBTAIN_TOKEN_PAIR_URI = "/api/auth/token-pair/obtain/";
export const REFRESH_TOKEN_PAIR_URI = "/api/auth/token-pair/refresh/";
export const EXPIRE_REFRESH_TOKEN_URI = "/api/auth/refresh-token/expire/";

export const INVALID_EMAIL_PATTERN_MESSAGE = "Enter a valid email address.";

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
    .post(USERS_URI, {
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
  axios.defaults.headers.common["Authorization"] = `Bearer ${accessToken}`;
  setTimeout(() => {
    refreshJWT();
  }, JWT_EXPIRY_TIME - 60000);
};
export const obtainJWT = (email, password) =>
  axios
    .post(OBTAIN_TOKEN_PAIR_URI, { email, password })
    .then((response) => onObtainJWTSuccess(response));

export const refreshJWT = () =>
  axios.post(REFRESH_TOKEN_PAIR_URI).then(onObtainJWTSuccess);

export const retrieveUser = () => {
  const {
    auth: { accessToken },
  } = store.getState();
  if (accessToken) {
    const { user_id: userId } = jwtDecode(accessToken);
    return axios.get(`${USERS_URI}${userId}/`);
  }
};

export const deleteRefreshTokenCookie = () =>
  axios.post(EXPIRE_REFRESH_TOKEN_URI);

export const searchUsers = (params) => axios.get(USERS_URI, { params });

export const emailAlreadyRegistered = async (email) => {
  const { data } = await searchUsers({ email });
  return data.length > 0; // user with this email does exist
};
