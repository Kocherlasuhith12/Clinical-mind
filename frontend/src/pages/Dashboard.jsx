import { useEffect, useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { useTranslation } from "react-i18next";
import { PlusCircle, Activity, AlertTriangle, CheckCircle, Clock } from "lucide-react";
import { casesAPI } from "../api/client";
import { useAuthStore } from "../hooks/useAuthStore";
import { useOfflineSync } from "../hooks/useOfflineSync";
import OfflineBanner from "../components/OfflineBanner";
import Navbar from "../components/Navbar";

const STATUS_CONFIG = {
  done:       { icon: CheckCircle,   color: "text-green-600",  bg: "bg-green-50",  label: "status.done" },
  urgent:     { icon: AlertTriangle, color: "text-red-600",    bg: "bg-red-50",    label: "status.urgent" },
  processing: { icon: Activity,      color: "text-blue-600",   bg: "bg-blue-50",   label: "status.processing" },
  pending:    { icon: Clock,         color: "text-yellow-600", bg: "bg-yellow-50", label: "status.pending" },
};

export default function Dashboard() {
  const { t } = useTranslation();
  const navigate = useNavigate();
  const user = useAuthStore((s) => s.user);
  const { isOnline, pendingCount } = useOfflineSync();
  const [cases, setCases] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    casesAPI.list({ limit: 20 }).then(({ data }) => setCases(data)).finally(() => setLoading(false));
  }, []);

  const stats = {
    total: cases.length,
    urgent: cases.filter((c) => c.status === "urgent").length,
    done: cases.filter((c) => c.status === "done").length,
    pending: cases.filter((c) => c.status === "pending" || c.status === "processing").length,
  };

  return (
    <div className="min-h-screen bg-gray-50">
      <Navbar />
      <OfflineBanner isOnline={isOnline} pendingCount={pendingCount} />

      <main className="max-w-4xl mx-auto px-4 py-6">
        {/* Welcome */}
        <div className="mb-6">
          <h2 className="text-xl font-semibold text-gray-800">
            {t("nav.dashboard")} — {user?.name}
          </h2>
          <p className="text-sm text-gray-500 capitalize">{user?.role}</p>
        </div>

        {/* Stats */}
        <div className="grid grid-cols-4 gap-3 mb-6">
          {[
            { label: "Total Cases", value: stats.total, color: "text-brand-600" },
            { label: "Urgent", value: stats.urgent, color: "text-red-600" },
            { label: "Completed", value: stats.done, color: "text-green-600" },
            { label: "Pending", value: stats.pending, color: "text-yellow-600" },
          ].map((s) => (
            <div key={s.label} className="bg-white rounded-xl p-4 border border-gray-100 text-center">
              <div className={`text-2xl font-bold ${s.color}`}>{s.value}</div>
              <div className="text-xs text-gray-500 mt-1">{s.label}</div>
            </div>
          ))}
        </div>

        {/* New case button */}
        <Link
          to="/cases/new"
          className="flex items-center gap-3 w-full bg-brand-600 hover:bg-brand-700 text-white rounded-2xl p-4 mb-6 transition-colors shadow-sm"
        >
          <PlusCircle className="w-6 h-6" />
          <div>
            <div className="font-semibold">{t("case.new_case")}</div>
            <div className="text-brand-100 text-xs">Submit symptoms, image, or voice</div>
          </div>
        </Link>

        {/* Cases list */}
        <div className="space-y-3">
          <h3 className="text-sm font-medium text-gray-600 uppercase tracking-wide">Recent Cases</h3>
          {loading ? (
            <div className="text-center py-12 text-gray-400">Loading...</div>
          ) : cases.length === 0 ? (
            <div className="text-center py-12 text-gray-400">No cases yet. Submit your first case above.</div>
          ) : (
            cases.map((c) => {
              const cfg = STATUS_CONFIG[c.status] || STATUS_CONFIG.pending;
              const Icon = cfg.icon;
              return (
                <button
                  key={c.id}
                  onClick={() => navigate(`/cases/${c.id}`)}
                  className="w-full bg-white rounded-xl border border-gray-100 p-4 flex items-center gap-4 hover:border-brand-200 hover:shadow-sm transition-all text-left"
                >
                  <div className={`w-10 h-10 rounded-xl ${cfg.bg} flex items-center justify-center flex-shrink-0`}>
                    <Icon className={`w-5 h-5 ${cfg.color}`} />
                  </div>
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center justify-between">
                      <span className="text-sm font-medium text-gray-800">
                        {c.patient_age}yr {c.patient_sex} · {c.symptoms_text?.slice(0, 50) || "No symptoms text"}...
                      </span>
                      <span className={`text-xs font-medium px-2 py-0.5 rounded-full ${cfg.bg} ${cfg.color}`}>
                        {t(cfg.label)}
                      </span>
                    </div>
                    <div className="text-xs text-gray-400 mt-0.5">{c.created_at?.slice(0, 10)}</div>
                  </div>
                </button>
              );
            })
          )}
        </div>
      </main>
    </div>
  );
}
