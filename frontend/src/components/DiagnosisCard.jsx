import { useTranslation } from "react-i18next";
import { BookOpen, Shield, ArrowRight, Cpu } from "lucide-react";

export default function DiagnosisCard({ diagnosis }) {
  const { t } = useTranslation();
  const conf = diagnosis.confidence ? Math.round(diagnosis.confidence * 100) : null;

  return (
    <div className="space-y-4">
      {/* Primary diagnosis */}
      <div className="bg-white rounded-2xl border border-gray-100 p-5">
        <div className="flex items-start justify-between mb-2">
          <p className="text-xs font-semibold text-gray-400 uppercase tracking-wide">{t("diagnosis.primary")}</p>
          {conf && (
            <div className="flex items-center gap-1.5">
              <div className="w-16 h-1.5 bg-gray-100 rounded-full overflow-hidden">
                <div
                  className={`h-full rounded-full ${conf >= 75 ? "bg-green-500" : conf >= 50 ? "bg-yellow-400" : "bg-red-400"}`}
                  style={{ width: `${conf}%` }}
                />
              </div>
              <span className="text-xs font-medium text-gray-500">{conf}%</span>
            </div>
          )}
        </div>
        <h3 className="text-lg font-semibold text-gray-900">{diagnosis.primary_dx}</h3>
        <p className="text-xs text-gray-400 mt-1 flex items-center gap-1">
          <Cpu className="w-3 h-3" /> {t("diagnosis.model")}: {diagnosis.model_used || "GPT-4o"}
        </p>
      </div>

      {/* Differentials */}
      {diagnosis.differentials?.length > 0 && (
        <div className="bg-white rounded-2xl border border-gray-100 p-5">
          <p className="text-xs font-semibold text-gray-400 uppercase tracking-wide mb-3">{t("diagnosis.differentials")}</p>
          <div className="space-y-2">
            {diagnosis.differentials.map((d, i) => (
              <div key={i} className="flex items-center gap-3">
                <div className="w-6 h-6 bg-gray-100 rounded-full flex items-center justify-center text-xs text-gray-500 flex-shrink-0">
                  {i + 1}
                </div>
                <div className="flex-1 min-w-0">
                  <div className="flex items-center justify-between">
                    <span className="text-sm font-medium text-gray-800">{d.name}</span>
                    <span className="text-xs text-gray-400">{Math.round((d.confidence || 0) * 100)}%</span>
                  </div>
                  {d.reason && <p className="text-xs text-gray-400 mt-0.5">{d.reason}</p>}
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Treatment */}
      <div className="bg-white rounded-2xl border border-gray-100 p-5">
        <p className="text-xs font-semibold text-brand-600 uppercase tracking-wide mb-2">{t("diagnosis.treatment")}</p>
        <p className="text-sm text-gray-700 leading-relaxed">{diagnosis.treatment_plan}</p>
      </div>

      {/* Precautions */}
      {diagnosis.precautions && (
        <div className="bg-yellow-50 rounded-2xl border border-yellow-100 p-5">
          <div className="flex items-center gap-2 mb-2">
            <Shield className="w-4 h-4 text-yellow-600" />
            <p className="text-xs font-semibold text-yellow-700 uppercase tracking-wide">{t("diagnosis.precautions")}</p>
          </div>
          <p className="text-sm text-yellow-800 leading-relaxed">{diagnosis.precautions}</p>
        </div>
      )}

      {/* When to refer */}
      {diagnosis.when_to_refer && (
        <div className="bg-white rounded-2xl border border-gray-100 p-5">
          <div className="flex items-center gap-2 mb-2">
            <ArrowRight className="w-4 h-4 text-brand-600" />
            <p className="text-xs font-semibold text-gray-400 uppercase tracking-wide">{t("diagnosis.refer")}</p>
          </div>
          <p className="text-sm text-gray-700 leading-relaxed">{diagnosis.when_to_refer}</p>
        </div>
      )}

      {/* Evidence references */}
      {diagnosis.references?.length > 0 && (
        <div className="bg-white rounded-2xl border border-gray-100 p-5">
          <div className="flex items-center gap-2 mb-3">
            <BookOpen className="w-4 h-4 text-gray-400" />
            <p className="text-xs font-semibold text-gray-400 uppercase tracking-wide">{t("diagnosis.evidence")}</p>
          </div>
          <div className="space-y-1">
            {diagnosis.references.slice(0, 4).map((r, i) => (
              <div key={i} className="text-xs text-gray-500 flex items-center gap-2">
                <div className="w-1 h-1 bg-gray-400 rounded-full" />
                {r.source} {r.score && <span className="text-gray-300">({r.score})</span>}
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
