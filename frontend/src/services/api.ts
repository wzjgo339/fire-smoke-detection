import axios from "axios";
import { API_BASE } from "../lib/constants";

const api = axios.create({
  baseURL: API_BASE,
  timeout: 600000,
});

api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response) {
      const msg = error.response.data?.detail || error.response.data?.error?.message || error.message;
      return Promise.reject(new Error(typeof msg === "string" ? msg : "Request failed"));
    }
    return Promise.reject(error);
  }
);

export default api;
