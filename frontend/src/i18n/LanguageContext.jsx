import React, { createContext, useContext, useState, useEffect } from 'react'
import { translations, SUPPORTED_LANGUAGES } from './translations'

const LanguageContext = createContext({
  lang: 'en',
  setLang: () => {},
  t: (key, fallback) => fallback || key,
  supportedLanguages: SUPPORTED_LANGUAGES,
  currentLanguage: SUPPORTED_LANGUAGES[0],
})

export function LanguageProvider({ children }) {
  const [lang, setLangState] = useState(() => {
    try {
      const saved = localStorage.getItem('civic_ai_lang')
      if (saved && translations[saved]) {
        return saved
      }
    } catch (_) {}
    return 'en'
  })

  const setLang = (newLang) => {
    if (translations[newLang]) {
      setLangState(newLang)
      try {
        localStorage.setItem('civic_ai_lang', newLang)
      } catch (_) {}
      // Update document direction if Urdu
      if (newLang === 'ur') {
        document.documentElement.setAttribute('dir', 'rtl')
      } else {
        document.documentElement.setAttribute('dir', 'ltr')
      }
    }
  }

  useEffect(() => {
    if (lang === 'ur') {
      document.documentElement.setAttribute('dir', 'rtl')
    } else {
      document.documentElement.setAttribute('dir', 'ltr')
    }
  }, [lang])

  const t = (key, fallback) => {
    const dict = translations[lang] || translations.en
    if (dict && dict[key] !== undefined) {
      return dict[key]
    }
    const enDict = translations.en
    if (enDict && enDict[key] !== undefined) {
      return enDict[key]
    }
    return fallback !== undefined ? fallback : key
  }

  const currentLanguage = SUPPORTED_LANGUAGES.find((l) => l.code === lang) || SUPPORTED_LANGUAGES[0]

  return (
    <LanguageContext.Provider
      value={{
        lang,
        setLang,
        t,
        supportedLanguages: SUPPORTED_LANGUAGES,
        currentLanguage,
      }}
    >
      {children}
    </LanguageContext.Provider>
  )
}

export function useLanguage() {
  return useContext(LanguageContext)
}
