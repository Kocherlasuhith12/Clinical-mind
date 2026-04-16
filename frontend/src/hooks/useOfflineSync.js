import { useState, useEffect, useCallback } from "react";
import { casesAPI } from "../api/client";

const DB_NAME = "clinicalmind_offline";
const STORE_NAME = "pending_cases";

function openDB() {
  return new Promise((resolve, reject) => {
    const req = indexedDB.open(DB_NAME, 1);
    req.onupgradeneeded = (e) => {
      e.target.result.createObjectStore(STORE_NAME, { keyPath: "localId", autoIncrement: true });
    };
    req.onsuccess = () => resolve(req.result);
    req.onerror = () => reject(req.error);
  });
}

export function useOfflineSync() {
  const [isOnline, setIsOnline] = useState(navigator.onLine);
  const [pendingCount, setPendingCount] = useState(0);
  const [isSyncing, setIsSyncing] = useState(false);

  const countPending = useCallback(async () => {
    const db = await openDB();
    const tx = db.transaction(STORE_NAME, "readonly");
    const count = await new Promise((res) => {
      const req = tx.objectStore(STORE_NAME).count();
      req.onsuccess = () => res(req.result);
    });
    setPendingCount(count);
  }, []);

  const saveOffline = useCallback(async (caseData) => {
    const db = await openDB();
    const tx = db.transaction(STORE_NAME, "readwrite");
    tx.objectStore(STORE_NAME).add({ ...caseData, savedAt: new Date().toISOString() });
    await countPending();
  }, [countPending]);

  const syncPending = useCallback(async () => {
    if (!navigator.onLine || isSyncing) return;
    setIsSyncing(true);
    try {
      const db = await openDB();
      const tx = db.transaction(STORE_NAME, "readonly");
      const all = await new Promise((res) => {
        const req = tx.objectStore(STORE_NAME).getAll();
        req.onsuccess = () => res(req.result);
      });

      if (all.length === 0) return;

      await casesAPI.sync(all.map(({ localId, savedAt, ...rest }) => rest));

      // Clear synced records
      const delTx = db.transaction(STORE_NAME, "readwrite");
      const store = delTx.objectStore(STORE_NAME);
      for (const item of all) store.delete(item.localId);
      await countPending();
    } catch (err) {
      console.error("Sync failed:", err);
    } finally {
      setIsSyncing(false);
    }
  }, [isSyncing, countPending]);

  useEffect(() => {
    countPending();
    const onOnline = () => { setIsOnline(true); syncPending(); };
    const onOffline = () => setIsOnline(false);
    window.addEventListener("online", onOnline);
    window.addEventListener("offline", onOffline);
    return () => {
      window.removeEventListener("online", onOnline);
      window.removeEventListener("offline", onOffline);
    };
  }, []);

  return { isOnline, pendingCount, isSyncing, saveOffline, syncPending };
}
