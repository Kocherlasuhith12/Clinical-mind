import { useState, useRef } from "react";
import { useNavigate } from "react-router-dom";
import { useTranslation } from "react-i18next";
import { useForm } from "react-hook-form";
import toast from "react-hot-toast";
import { Mic, MicOff, Upload, X, ArrowLeft } from "lucide-react";
import { casesAPI } from "../api/client";
import { useOfflineSync } from "../hooks/useOfflineSync";
import Navbar from "../components/Navbar";

export default function NewCase() {
  const { t } = useTranslation();
  const navigate = useNavigate();
  const { isOnline, saveOffline } = useOfflineSync();
  const { register, handleSubmit, formState: { errors } } = useForm();
  const [loading, setLoading] = useState(false);
  const [images, setImages] = useState([]);
  const [audioBlob, setAudioBlob] = useState(null);
  const [isRecording, setIsRecording] = useState(false);
  const [selectedLang, setSelectedLang] = useState("en");
  const mediaRef = useRef(null);
  const chunksRef = useRef([]);

  const startRecording = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      const recorder = new MediaRecorder(stream);
      chunksRef.current = [];
      recorder.ondataavailable = (e) => chunksRef.current.push(e.data);
      recorder.onstop = () => {
        const blob = new Blob(chunksRef.current, { type: "audio/webm" });
        setAudioBlob(blob);
        stream.getTracks().forEach((t) => t.stop());
      };
      recorder.start();
      mediaRef.current = recorder;
      setIsRecording(true);
    } catch {
      toast.error("Microphone access denied");
    }
  };

  const stopRecording = () => {
    mediaRef.current?.stop();
    setIsRecording(false);
  };

  const handleImages = (e) => {
    const files = Array.from(e.target.files).slice(0, 3);
    setImages((prev) => [...prev, ...files].slice(0, 3));
  };

  const onSubmit = async (data) => {
    setLoading(true);
    try {
      if (!isOnline) {
        await saveOffline({ ...data, symptoms_language: selectedLang });
        toast.success(t("case.offline_note"));
        navigate("/dashboard");
        return;
      }

      const form = new FormData();
      form.append("patient_age", data.patient_age);
      form.append("patient_sex", data.patient_sex);
      form.append("symptoms_text", data.symptoms_text || "");
      form.append("symptoms_language", selectedLang);
      form.append("is_offline", "false");

      if (audioBlob) {
        form.append("audio", new File([audioBlob], "recording.webm", { type: "audio/webm" }));
      }
      images.forEach((img) => form.append("images", img));

      const { data: res } = await casesAPI.submit(form);
      toast.success("Case submitted! AI is analyzing...");
      navigate(`/cases/${res.case_id}`);
    } catch (err) {
      toast.error(t("errors.submit_failed"));
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gray-50">
      <Navbar />
      <main className="max-w-2xl mx-auto px-4 py-6">
        <button onClick={() => navigate(-1)} className="flex items-center gap-2 text-sm text-gray-500 hover:text-gray-700 mb-4">
          <ArrowLeft className="w-4 h-4" /> Back
        </button>

        <h2 className="text-xl font-semibold text-gray-800 mb-6">{t("case.new_case")}</h2>

        <form onSubmit={handleSubmit(onSubmit)} className="space-y-5">
          {/* Patient info */}
          <div className="bg-white rounded-2xl border border-gray-100 p-5">
            <h3 className="text-sm font-semibold text-gray-700 mb-4">Patient Information</h3>
            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="block text-sm text-gray-600 mb-1">{t("case.patient_age")}</label>
                <input
                  type="number" min="0" max="120"
                  className="w-full border border-gray-200 rounded-xl px-4 py-3 text-sm focus:outline-none focus:ring-2 focus:ring-brand-500"
                  {...register("patient_age", { required: true, min: 0, max: 120 })}
                />
              </div>
              <div>
                <label className="block text-sm text-gray-600 mb-1">{t("case.patient_sex")}</label>
                <select
                  className="w-full border border-gray-200 rounded-xl px-4 py-3 text-sm focus:outline-none focus:ring-2 focus:ring-brand-500"
                  {...register("patient_sex", { required: true })}
                >
                  <option value="M">{t("case.male")}</option>
                  <option value="F">{t("case.female")}</option>
                  <option value="O">{t("case.other")}</option>
                </select>
              </div>
            </div>
          </div>

          {/* Symptoms */}
          <div className="bg-white rounded-2xl border border-gray-100 p-5">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-sm font-semibold text-gray-700">{t("case.symptoms")}</h3>
              <select
                value={selectedLang}
                onChange={(e) => setSelectedLang(e.target.value)}
                className="text-xs border border-gray-200 rounded-lg px-3 py-1.5 focus:outline-none"
              >
                <option value="en">English</option>
                <option value="ta">தமிழ்</option>
                <option value="hi">हिंदी</option>
              </select>
            </div>
            <textarea
              rows={4}
              className="w-full border border-gray-200 rounded-xl px-4 py-3 text-sm focus:outline-none focus:ring-2 focus:ring-brand-500 resize-none"
              placeholder={t("case.symptoms_placeholder")}
              {...register("symptoms_text")}
            />

            {/* Voice recording */}
            <div className="mt-3 flex items-center gap-3">
              <button
                type="button"
                onClick={isRecording ? stopRecording : startRecording}
                className={`flex items-center gap-2 px-4 py-2 rounded-xl text-sm font-medium transition-colors ${
                  isRecording
                    ? "bg-red-50 text-red-600 border border-red-200 animate-pulse"
                    : "bg-gray-50 text-gray-600 border border-gray-200 hover:border-brand-300"
                }`}
              >
                {isRecording ? <MicOff className="w-4 h-4" /> : <Mic className="w-4 h-4" />}
                {isRecording ? t("case.stop_recording") : t("case.record_voice")}
              </button>
              {audioBlob && (
                <span className="text-xs text-green-600 font-medium">Audio recorded</span>
              )}
            </div>
          </div>

          {/* Images */}
          <div className="bg-white rounded-2xl border border-gray-100 p-5">
            <h3 className="text-sm font-semibold text-gray-700 mb-3">{t("case.upload_image")}</h3>
            <label className="flex items-center gap-3 border-2 border-dashed border-gray-200 rounded-xl p-4 cursor-pointer hover:border-brand-400 transition-colors">
              <Upload className="w-5 h-5 text-gray-400" />
              <span className="text-sm text-gray-500">Click to upload (max 3 images)</span>
              <input type="file" className="hidden" accept="image/*" multiple onChange={handleImages} />
            </label>
            {images.length > 0 && (
              <div className="flex gap-2 mt-3 flex-wrap">
                {images.map((img, i) => (
                  <div key={i} className="relative">
                    <img
                      src={URL.createObjectURL(img)}
                      alt=""
                      className="w-16 h-16 object-cover rounded-lg border border-gray-200"
                    />
                    <button
                      type="button"
                      onClick={() => setImages((prev) => prev.filter((_, j) => j !== i))}
                      className="absolute -top-1.5 -right-1.5 w-5 h-5 bg-red-500 text-white rounded-full flex items-center justify-center"
                    >
                      <X className="w-3 h-3" />
                    </button>
                  </div>
                ))}
              </div>
            )}
          </div>

          {/* Submit */}
          <button
            type="submit"
            disabled={loading}
            className="w-full bg-brand-600 hover:bg-brand-700 text-white font-semibold py-4 rounded-2xl transition-colors disabled:opacity-60 text-base"
          >
            {loading ? t("case.submitting") : isOnline ? t("case.submit") : "Save Offline"}
          </button>

          {!isOnline && (
            <p className="text-center text-sm text-yellow-600 bg-yellow-50 rounded-xl p-3">
              {t("case.offline_note")}
            </p>
          )}
        </form>
      </main>
    </div>
  );
}
