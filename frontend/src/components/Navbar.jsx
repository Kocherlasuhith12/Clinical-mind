import { Link, useNavigate } from "react-router-dom";
import { useTranslation } from "react-i18next";
import { LogOut, PlusCircle } from "lucide-react";
import { useAuthStore } from "../hooks/useAuthStore";
import LanguageSwitcher from "./LanguageSwitcher";

export default function Navbar() {
  const { t } = useTranslation();
  const navigate = useNavigate();
  const { user, logout } = useAuthStore();

  const handleLogout = () => {
    logout();
    navigate("/login");
  };

  return (
    <nav className="bg-white border-b border-gray-100 sticky top-0 z-40">
      <div className="max-w-4xl mx-auto px-4 h-14 flex items-center justify-between">
        <Link to="/dashboard" className="flex items-center gap-2">
          <div className="w-7 h-7 bg-brand-600 rounded-lg flex items-center justify-center">
            <span className="text-white text-xs font-bold">CM</span>
          </div>
          <span className="font-semibold text-gray-800 text-sm">ClinicalMind</span>
        </Link>

        <div className="flex items-center gap-3">
          <LanguageSwitcher compact />
          <Link
            to="/cases/new"
            className="flex items-center gap-1.5 bg-brand-600 text-white text-xs font-medium px-3 py-1.5 rounded-lg hover:bg-brand-700 transition-colors"
          >
            <PlusCircle className="w-3.5 h-3.5" />
            {t("nav.new_case")}
          </Link>
          <button onClick={handleLogout} className="p-1.5 text-gray-400 hover:text-gray-600 transition-colors">
            <LogOut className="w-4 h-4" />
          </button>
        </div>
      </div>
    </nav>
  );
}
