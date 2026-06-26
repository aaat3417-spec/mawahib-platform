import axios from "axios";

function getApiBaseUrl() {
  const configuredUrl = import.meta.env.VITE_API_URL;
  if (!configuredUrl) {
    return "/api";
  }

  const normalizedUrl = configuredUrl.replace(/\/+$/, "");
  return normalizedUrl.endsWith("/api") ? normalizedUrl : `${normalizedUrl}/api`;
}

export const api = axios.create({
  baseURL: getApiBaseUrl()
});

api.interceptors.request.use((config) => {
  const token = localStorage.getItem("mawahib_token");
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem("mawahib_token");
      localStorage.removeItem("mawahib_user");
    }
    return Promise.reject(error);
  }
);

export function apiErrorMessage(error) {
  if (!error.response) {
    return "Cannot reach the server. Check your connection and try again.";
  }
  const detail = error.response?.data?.detail;
  if (Array.isArray(detail)) {
    return detail.map((item) => {
      const field = Array.isArray(item.loc) ? item.loc.filter((part) => part !== "body").join(".") : "";
      const message = item.msg || "Invalid value";
      return field ? `${field}: ${message}` : message;
    }).join(" ");
  }
  if (typeof detail === "object" && detail !== null) {
    return JSON.stringify(detail);
  }
  return detail || error.message || "Something went wrong.";
}
