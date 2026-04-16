// EmergencyBanner.jsx
import { Phone, AlertTriangle } from "lucide-react";
import { useTranslation } from "react-i18next";

export default function EmergencyBanner({ reason }) {
  const { t } = useTranslation();
  return (
    <div className="bg-red-600 text-white rounded-2xl p-5 mb-4 animate-pulse">
      <div className="flex items-start gap-3">
        <AlertTriangle className="w-6 h-6 flex-shrink-0 mt-0.5" />
        <div className="flex-1">
          <p className="font-bold text-lg">{t("diagnosis.emergency")}</p>
          {reason && <p className="text-red-100 text-sm mt-1">{reason}</p>}
        </div>
      </div>
      <a
        href="tel:108"
        className="mt-4 flex items-center justify-center gap-2 bg-white text-red-600 font-bold py-3 rounded-xl"
      >
        <Phone className="w-5 h-5" />
        {t("diagnosis.call_108")}
      </a>
    </div>
  );
}
