import { useTranslation } from "react-i18next";

const LANGS = [
  { code: "en", label: "EN" },
  { code: "ta", label: "தமிழ்" },
  { code: "hi", label: "हि" },
];

export default function LanguageSwitcher({ compact = false }) {
  const { i18n } = useTranslation();

  const change = (code) => {
    i18n.changeLanguage(code);
    localStorage.setItem("cm_lang", code);
  };

  return (
    <div className="flex items-center gap-1">
      {LANGS.map((l) => (
        <button
          key={l.code}
          onClick={() => change(l.code)}
          className={`px-2 py-1 rounded-lg text-xs font-medium transition-colors ${
            i18n.language === l.code
              ? "bg-brand-600 text-white"
              : "text-gray-500 hover:text-gray-700 hover:bg-gray-100"
          }`}
        >
          {compact ? l.code.toUpperCase() : l.label}
        </button>
      ))}
    </div>
  );
}
