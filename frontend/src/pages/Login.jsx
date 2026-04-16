import { useState } from "react";
import { useNavigate, Link } from "react-router-dom";
import { useTranslation } from "react-i18next";
import { useForm } from "react-hook-form";
import toast from "react-hot-toast";
import { authAPI } from "../api/client";
import { useAuthStore } from "../hooks/useAuthStore";
import LanguageSwitcher from "../components/LanguageSwitcher";

export default function Login() {
  const { t } = useTranslation();
  const navigate = useNavigate();
  const login = useAuthStore((s) => s.login);
  const [loading, setLoading] = useState(false);
  const { register, handleSubmit, formState: { errors } } = useForm();

  const onSubmit = async ({ email, password }) => {
    setLoading(true);
    try {
      const { data } = await authAPI.login(email, password);
      login({ id: data.user_id, name: data.name, role: data.role, language: data.language }, data.access_token);
      navigate("/dashboard");
    } catch {
      toast.error(t("errors.login_failed"));
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-brand-50 to-white flex items-center justify-center p-4">
      <div className="w-full max-w-md">
        {/* Logo */}
        <div className="text-center mb-8">
          <div className="w-16 h-16 bg-brand-600 rounded-2xl flex items-center justify-center mx-auto mb-4 shadow-lg">
            <span className="text-white text-2xl font-bold">CM</span>
          </div>
          <h1 className="text-2xl font-bold text-brand-700">{t("app_name")}</h1>
          <p className="text-gray-500 text-sm mt-1">{t("tagline")}</p>
          <div className="mt-3"><LanguageSwitcher /></div>
        </div>

        <div className="bg-white rounded-2xl shadow-sm border border-gray-100 p-8">
          <h2 className="text-lg font-semibold text-gray-800 mb-6">{t("auth.login")}</h2>
          <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">{t("auth.email")}</label>
              <input
                type="email"
                className="w-full border border-gray-200 rounded-xl px-4 py-3 text-sm focus:outline-none focus:ring-2 focus:ring-brand-500 focus:border-transparent"
                placeholder="doctor@clinic.com"
                {...register("email", { required: true })}
              />
              {errors.email && <p className="text-red-500 text-xs mt-1">{t("errors.required")}</p>}
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">{t("auth.password")}</label>
              <input
                type="password"
                className="w-full border border-gray-200 rounded-xl px-4 py-3 text-sm focus:outline-none focus:ring-2 focus:ring-brand-500 focus:border-transparent"
                placeholder="••••••••"
                {...register("password", { required: true })}
              />
            </div>
            <button
              type="submit"
              disabled={loading}
              className="w-full bg-brand-600 hover:bg-brand-700 text-white font-medium py-3 rounded-xl transition-colors disabled:opacity-60"
            >
              {loading ? "..." : t("auth.submit_login")}
            </button>
          </form>
          <p className="text-center text-sm text-gray-500 mt-6">
            {t("auth.no_account")}{" "}
            <Link to="/register" className="text-brand-600 font-medium hover:underline">{t("auth.register")}</Link>
          </p>
        </div>
      </div>
    </div>
  );
}
