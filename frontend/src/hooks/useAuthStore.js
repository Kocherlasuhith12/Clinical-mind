import { create } from "zustand";

const stored = localStorage.getItem("cm_user");

export const useAuthStore = create((set) => ({
  user: stored ? JSON.parse(stored) : null,
  token: localStorage.getItem("cm_token") || null,

  login: (user, token) => {
    localStorage.setItem("cm_token", token);
    localStorage.setItem("cm_user", JSON.stringify(user));
    set({ user, token });
  },

  logout: () => {
    localStorage.removeItem("cm_token");
    localStorage.removeItem("cm_user");
    set({ user: null, token: null });
  },
}));
