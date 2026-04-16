import { useEffect, useState } from "react";
import { useParams, useNavigate } from "react-router-dom";
import { useTranslation } from "react-i18next";
import { AlertTriangle, Phone, FileDown, ArrowLeft, CheckCircle, Activity } from "lucide-react";
import toast from "react-hot-toast";
import { casesAPI } from "../api/client";
import { useWebSocket } from "../hooks/useWebSocket";
import Navbar from "../components/Navbar";
import DiagnosisCard from "../components/DiagnosisCard";
import EmergencyBanner from "../components/EmergencyBanner";

export default function CaseResult() {
  const { t } = useTranslation();
  const { id } = useParams();
  const navigate = useNavigate();
  const [caseData, setCaseData] = useState(null);
  const [loading, setLoading] = useState(true);
  const { status: wsStatus, isEmergency } = useWebSocket(id);

  const fetchCase = () => {
    casesAPI.get(id).then(({ data }) => setCaseData(data)).finally(() => setLoading(false));
  };

  useEffect(() => { fetchCase(); }, [id]);

  // Refresh when WebSocket reports update
  useEffect(() => {
    if (wsStatus) fetchCase();
  }, [wsStatus]);

  const exportPDF = async () => {
    try {
      const { data } = await casesAPI.exportPDF(id);
      const url = URL.createObjectURL(new Blob([data], { type: "application/pdf" }));
      const a = document.createElement("a");
      a.href = url;
      a.download = `case-${id.slice(0, 8)}.pdf`;
      a.click();
    } catch {
      toast.error("Export failed");
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50">
        <Navbar />
        <div className="flex items-center justify-center h-64">
          <Activity className="w-8 h-8 text-brand-500 animate-spin" />
        </div>
      </div>
    );
  }

  const isProcessing = caseData?.status === "processing" || caseData?.status === "pending";

  return (
    <div className="min-h-screen bg-gray-50">
      <Navbar />
      <main className="max-w-2xl mx-auto px-4 py-6">
        <button onClick={() => navigate("/dashboard")} className="flex items-center gap-2 text-sm text-gray-500 mb-4">
          <ArrowLeft className="w-4 h-4" /> Back
        </button>

        {/* Emergency banner */}
        {(isEmergency || caseData?.diagnosis?.is_emergency) && (
          <EmergencyBanner reason={caseData?.diagnosis?.emergency_reason} />
        )}

        {/* Patient header */}
        <div className="bg-white rounded-2xl border border-gray-100 p-5 mb-4">
          <div className="flex items-center justify-between">
            <div>
              <h2 className="font-semibold text-gray-800">
                Patient: {caseData?.patient_age}yr {caseData?.patient_sex === "M" ? "Male" : caseData?.patient_sex === "F" ? "Female" : "Other"}
              </h2>
              <p className="text-sm text-gray-500 mt-1">{caseData?.symptoms_text?.slice(0, 120)}</p>
              <p className="text-xs text-gray-400 mt-1">{caseData?.created_at?.slice(0, 10)}</p>
            </div>
            <StatusBadge status={caseData?.status} t={t} />
          </div>

          {/* Attached images */}
          {caseData?.image_urls?.length > 0 && (
            <div className="flex gap-2 mt-4 flex-wrap">
              {caseData.image_urls.map((url, i) => (
                <img key={i} src={url} alt="" className="w-16 h-16 object-cover rounded-lg border border-gray-200" />
              ))}
            </div>
          )}
        </div>

        {/* Processing state */}
        {isProcessing && (
          <div className="bg-blue-50 border border-blue-100 rounded-2xl p-6 text-center mb-4">
            <Activity className="w-8 h-8 text-blue-500 animate-spin mx-auto mb-3" />
            <p className="font-medium text-blue-700">{t("case.processing")}</p>
            <p className="text-sm text-blue-500 mt-1">This usually takes 10-30 seconds</p>
          </div>
        )}

        {/* Diagnosis result */}
        {caseData?.diagnosis && (
          <>
            <DiagnosisCard diagnosis={caseData.diagnosis} />
            <button
              onClick={exportPDF}
              className="w-full mt-4 flex items-center justify-center gap-2 border border-brand-200 text-brand-600 font-medium py-3 rounded-2xl hover:bg-brand-50 transition-colors"
            >
              <FileDown className="w-5 h-5" />
              {t("diagnosis.export_pdf")}
            </button>
          </>
        )}
      </main>
    </div>
  );
}

function StatusBadge({ status, t }) {
  const map = {
    done:       { bg: "bg-green-50",  text: "text-green-700",  label: "status.done" },
    urgent:     { bg: "bg-red-50",    text: "text-red-700",    label: "status.urgent" },
    processing: { bg: "bg-blue-50",   text: "text-blue-700",   label: "status.processing" },
    pending:    { bg: "bg-yellow-50", text: "text-yellow-700", label: "status.pending" },
  };
  const cfg = map[status] || map.pending;
  return (
    <span className={`px-3 py-1 rounded-full text-xs font-semibold ${cfg.bg} ${cfg.text}`}>
      {t(cfg.label)}
    </span>
  );
}
