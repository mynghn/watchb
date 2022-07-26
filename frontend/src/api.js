import Axios from "axios";

export const BACKEND_HOST = process.env.REACT_APP_BACKEND_HOST;
export const SIGN_UP_URI = "/api/accounts/";
export const JWT_OBTAIN_URI = "/api/accounts/jwt/";

export const axios = Axios.create({
  baseURL: BACKEND_HOST,
  withCredentials: true,
  xsrfCookieName: "csrftoken",
  xsrfHeaderName: "X-CSRFToken",
});

export const signUp = async (username, email, password) => {
  try {
    const response = await axios.post(SIGN_UP_URI, {
      username,
      email,
      password,
    });
    return response;
  } catch (err) {
    return err.response;
  }
};
export const obtainJWT = async (email, password) => {
  try {
    const response = await axios.post(JWT_OBTAIN_URI, { email, password });
    return response;
  } catch (err) {
    return err.response;
  }
};
