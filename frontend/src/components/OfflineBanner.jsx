import { useTranslation } from "react-i18next";
import { WifiOff, RefreshCw } from "lucide-react";
import { useOfflineSync } from "../hooks/useOfflineSync";

export default function OfflineBanner({ isOnline, pendingCount }) {
  const { t } = useTranslation();
  const { isSyncing, syncPending } = useOfflineSync();

  if (isOnline && pendingCount === 0) return null;

  return (
    <div className={`px-4 py-2 text-xs font-medium flex items-center justify-between ${
      isOnline ? "bg-blue-50 text-blue-700" : "bg-yellow-50 text-yellow-700"
    }`}>
      <div className="flex items-center gap-2">
        <WifiOff className="w-3.5 h-3.5" />
        {!isOnline
          ? t("offline.offline_mode")
          : `${pendingCount} ${t("offline.cases_queued")}`}
      </div>
      {isOnline && pendingCount > 0 && (
        <button
          onClick={syncPending}
          disabled={isSyncing}
          className="flex items-center gap-1 underline"
        >
          <RefreshCw className={`w-3 h-3 ${isSyncing ? "animate-spin" : ""}`} />
          {isSyncing ? t("offline.syncing") : "Sync now"}
        </button>
      )}
    </div>
  );
}
