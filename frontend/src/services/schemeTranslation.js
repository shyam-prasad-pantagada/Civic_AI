/**
 * Civic_AI Client-Side Scheme Translation & Caching Service
 *
 * Provides multi-tier caching:
 * 1. In-memory JS Map for instantaneous (<1ms) component re-renders.
 * 2. LocalStorage persistence across page reloads.
 * 3. Asynchronous batch translation from backend API for visible schemes.
 */

import { useState, useEffect } from 'react'

const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:8000'

const CACHE_PREFIX = 'civic_trans_v6_'

// Clean up any legacy or stale cache keys on module load
try {
  const keysToRemove = []
  for (let i = 0; i < localStorage.length; i++) {
    const k = localStorage.key(i)
    if (k && k.startsWith('civic_trans_') && !k.startsWith(CACHE_PREFIX)) {
      keysToRemove.push(k)
    }
  }
  keysToRemove.forEach((k) => localStorage.removeItem(k))
} catch (e) {
  // ignore
}

// In-memory cache: key = `${scheme_id}_${lang}`
const memoryCache = new Map()

// Batch queue to avoid redundant network calls
let pendingBatch = new Set()
let batchTimer = null
const batchCallbacks = new Map()

function getCacheKey(schemeId, lang) {
  return `${(schemeId || '').toUpperCase()}_${lang}`
}

export function getCachedScheme(schemeId, lang) {
  if (!schemeId || !lang || lang === 'en') return null
  const key = getCacheKey(schemeId, lang)

  // 1. Check in-memory Map
  if (memoryCache.has(key)) {
    return memoryCache.get(key)
  }

  // 2. Check localStorage
  try {
    const raw = localStorage.getItem(`${CACHE_PREFIX}${key}`)
    if (raw) {
      const parsed = JSON.parse(raw)
      memoryCache.set(key, parsed)
      return parsed
    }
  } catch (e) {
    // ignore storage quota / parse errors
  }

  return null
}

export function setCachedScheme(schemeId, lang, data) {
  if (!schemeId || !lang || !data) return
  const key = getCacheKey(schemeId, lang)
  memoryCache.set(key, data)

  try {
    localStorage.setItem(`${CACHE_PREFIX}${key}`, JSON.stringify(data))
  } catch (e) {
    // ignore
  }
}

/**
 * Fetch complete translated scheme details from backend
 */
export async function fetchTranslatedScheme(schemeId, lang) {
  if (!schemeId || !lang || lang === 'en') return null

  // Check cache first
  const cached = getCachedScheme(schemeId, lang)
  if (cached) return cached

  try {
    const res = await fetch(`${API_BASE}/api/schemes/${encodeURIComponent(schemeId)}?lang=${lang}`)
    if (!res.ok) throw new Error(`HTTP ${res.status}`)
    const data = await res.json()
    setCachedScheme(schemeId, lang, data)
    return data
  } catch (err) {
    console.warn(`Failed to fetch scheme translation for ${schemeId} (${lang}):`, err)
    return null
  }
}

/**
 * Batch translation queue processor
 */
function processBatchQueue(lang) {
  if (pendingBatch.size === 0) return

  const idsToFetch = Array.from(pendingBatch).slice(0, 24)
  idsToFetch.forEach((id) => pendingBatch.delete(id))

  fetch(`${API_BASE}/api/schemes/batch-translate`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ scheme_ids: idsToFetch, lang }),
  })
    .then((res) => (res.ok ? res.json() : { translations: {} }))
    .then((data) => {
      const transMap = data.translations || {}
      Object.entries(transMap).forEach(([id, trans]) => {
        setCachedScheme(id, lang, trans)
        const cbs = batchCallbacks.get(getCacheKey(id, lang)) || []
        cbs.forEach((cb) => cb(trans))
        batchCallbacks.delete(getCacheKey(id, lang))
      })
    })
    .catch((err) => console.warn('Batch translation error:', err))
}

export function queueSchemeForTranslation(schemeId, lang, onDone) {
  if (!schemeId || !lang || lang === 'en') return

  const key = getCacheKey(schemeId, lang)
  const cached = getCachedScheme(schemeId, lang)
  if (cached) {
    if (onDone) onDone(cached)
    return
  }

  if (onDone) {
    const list = batchCallbacks.get(key) || []
    list.push(onDone)
    batchCallbacks.set(key, list)
  }

  pendingBatch.add(schemeId)
  if (batchTimer) clearTimeout(batchTimer)
  batchTimer = setTimeout(() => processBatchQueue(lang), 60)
}

/**
 * React hook to localize a scheme object automatically
 */
export function useSchemeTranslation(scheme, lang) {
  const [translated, setTranslated] = useState(() => {
    if (!scheme || !lang || lang === 'en') return scheme
    // If scheme was already translated by backend endpoint /api/schemes?lang=..., prioritize it!
    if (scheme.original_scheme_name) {
      setCachedScheme(scheme.scheme_id, lang, scheme)
      return scheme
    }
    return getCachedScheme(scheme.scheme_id, lang) || (scheme.translations?.[lang] ? { ...scheme, ...scheme.translations[lang] } : scheme)
  })
  const [isTranslating, setIsTranslating] = useState(() => {
    if (!scheme || !lang || lang === 'en') return false
    if (scheme.original_scheme_name) return false
    return !getCachedScheme(scheme.scheme_id, lang) && !scheme.translations?.[lang]
  })

  useEffect(() => {
    if (!scheme || !lang || lang === 'en') {
      setTranslated(scheme)
      setIsTranslating(false)
      return
    }

    // Backend already localized this scheme
    if (scheme.original_scheme_name) {
      setCachedScheme(scheme.scheme_id, lang, scheme)
      setTranslated(scheme)
      setIsTranslating(false)
      return
    }

    const cached = getCachedScheme(scheme.scheme_id, lang)
    if (cached) {
      setTranslated({ ...scheme, ...cached })
      setIsTranslating(false)
      return
    }

    if (scheme.translations?.[lang]) {
      const prebaked = { ...scheme, ...scheme.translations[lang] }
      setCachedScheme(scheme.scheme_id, lang, prebaked)
      setTranslated(prebaked)
      setIsTranslating(false)
      return
    }

    setIsTranslating(true)
    queueSchemeForTranslation(scheme.scheme_id, lang, (result) => {
      setTranslated({ ...scheme, ...result })
      setIsTranslating(false)
    })
  }, [scheme?.scheme_id, scheme?.original_scheme_name, lang])

  return {
    scheme: translated || scheme,
    isTranslating,
  }
}
