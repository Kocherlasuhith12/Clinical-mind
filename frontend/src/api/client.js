import axios from "axios";

const BASE_URL = import.meta.env.VITE_API_URL || "http://localhost:8000";

const api = axios.create({ baseURL: BASE_URL, timeout: 30000 });

// Attach JWT to every request
api.interceptors.request.use((config) => {
  const token = localStorage.getItem("cm_token");
  if (token) config.headers.Authorization = `Bearer ${token}`;
  return config;
});

// Handle 401 — redirect to login
api.interceptors.response.use(
  (res) => res,
  (err) => {
    if (err.response?.status === 401) {
      localStorage.removeItem("cm_token");
      localStorage.removeItem("cm_user");
      window.location.href = "/login";
    }
    return Promise.reject(err);
  }
);

// Auth
export const authAPI = {
  login: (email, password) => {
    const form = new FormData();
    form.append("username", email);
    form.append("password", password);
    return api.post("/auth/login", form);
  },
  register: (data) => api.post("/auth/register", data),
  me: () => api.get("/auth/me"),
};

// Cases
export const casesAPI = {
  submit: (formData) => api.post("/cases/submit", formData, {
    headers: { "Content-Type": "multipart/form-data" },
    timeout: 60000,
  }),
  list: (params) => api.get("/cases/", { params }),
  get: (id) => api.get(`/cases/${id}`),
  sync: (cases) => api.post("/cases/sync", cases),
  exportPDF: (id) => api.get(`/cases/${id}/export`, { responseType: "blob" }),
};

export default api;
