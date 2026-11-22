import React, { useState } from 'react'
import UploadCard from '../components/UploadCard'
import SourceBadge from '../components/SourceBadge'
import CitationChip from '../components/CitationChip'
import { renderClickableContent } from '../utils/linkify'
import { useLanguage } from '../i18n'

const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:8000'

export default function ExplainPage() {
  const { lang, t, currentLanguage } = useLanguage()
  const [analyzing, setAnalyzing] = useState(false)
  const [result, setResult] = useState(null)
  const [error, setError] = useState(null)
  const [verifying, setVerifying] = useState(false)
  const [verifyData, setVerifyData] = useState(null)

  const handleAnalyze = async (data) => {
    setAnalyzing(true)
    setError(null)
    setVerifyData(null)

    try {
      let res
      if (data.mode === 'upload' && data.file) {
        const formData = new FormData()
        formData.append('file', data.file)
        if (data.state) formData.append('state', data.state)
        formData.append('lang', lang)

        res = await fetch(`${API_BASE}/api/explain/upload`, {
          method: 'POST',
          body: formData,
        })
      } else {
        res = await fetch(`${API_BASE}/api/explain?lang=${lang}`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            text: data.text,
            state: data.state,
            document_type: data.docType,
            lang: lang,
          }),
        })
      }

      if (!res.ok) {
        const errJson = await res.json().catch(() => ({}))
        throw new Error(errJson.detail || `Server error (${res.status})`)
      }

      const json = await res.json()
      setResult(json)
    } catch (err) {
      console.error('Analysis failed:', err)
      setError(err.message || 'Failed to explain document. Please check the backend connection.')
    } finally {
      setAnalyzing(false)
    }
  }

  // Real-time Live Verification check
  const handleVerify = async () => {
    if (!result) return
    setVerifying(true)
    try {
      const res = await fetch(`${API_BASE}/api/verify`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          claim_or_circular_title: result.plain_summary.slice(0, 120),
          source_url: result.source_url,
          stated_deadline: result.deadlines?.[0] || null,
          lang: lang,
        }),
      })
      if (res.ok) {
        const data = await res.json()
        setVerifyData(data)
      }
    } catch (err) {
      console.error('Verification check error:', err)
    } finally {
      setVerifying(false)
    }
  }

  return (
    <div>
      {/* Header */}
      <div className="page-header">
        <span className="badge badge-pill page-badge">
          <span>📄</span>
          <span>{t('noticeExplainerTitle', 'Notice & Document Explainer')}</span>
        </span>
        <h1 className="page-title">
          {t('noticeExplainerTitle', 'Government Notice & Order Explainer')}
        </h1>
        <p className="page-subtitle">
          {t('noticeExplainerSub', 'Upload government circulars, court notices, welfare scheme PDFs or gazette notifications. Get plain summaries, affected citizen criteria, strict deadlines, and clear next steps.')}
        </p>
      </div>

      {/* Main Upload / Input Component */}
      <UploadCard onAnalyze={handleAnalyze} isLoading={analyzing} />

      {/* Error state */}
      {error && (
        <div style={{ maxWidth: '820px', margin: '2rem auto 0', padding: '1rem 1.5rem', background: 'rgba(239, 68, 68, 0.1)', border: '1px solid rgba(239, 68, 68, 0.3)', borderRadius: 'var(--radius-md)', color: '#fca5a5' }}>
          <strong>Error:</strong> {error}
        </div>
      )}

      {/* Processing State */}
      {analyzing && (
        <div style={{ textAlign: 'center', margin: '3rem 0' }}>
          <div className="loading-spinner"></div>
          <div style={{ marginTop: '1rem', color: 'var(--text-secondary)', fontSize: '0.95rem' }}>
            {t('analyzingDoc', 'Extracting text layer and analyzing official clauses with Civic AI AI Engine')} ({currentLanguage?.native || lang.toUpperCase()})...
          </div>
        </div>
      )}

      {/* Results Area */}
      {result && (
        <div style={{ marginTop: '3.5rem', maxWidth: '820px', margin: '3.5rem auto 0' }}>
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '1.25rem', flexWrap: 'wrap', gap: '0.75rem' }}>
            <h3 style={{ fontFamily: 'var(--font-family-heading)', fontSize: '1.3rem', fontWeight: 700 }}>
              {t('officialDocAnalysis', 'Official Document Analysis')}
            </h3>

            <SourceBadge 
              status={
                !verifyData 
                  ? 'not_verified' 
                  : verifyData.badge.includes('outdated') 
                  ? 'outdated' 
                  : verifyData.badge.includes('Could not verify') 
                  ? 'could_not_verify' 
                  : 'verified'
              } 
              sourceName={verifyData?.source_url ? new URL(verifyData.source_url).hostname : (result.source_url ? new URL(result.source_url.startsWith('http') ? result.source_url : 'https://egazette.gov.in').hostname : 'Official Source')} 
              sourceUrl={verifyData?.source_url || result.source_url} 
              lastVerified={verifyData?.badge} 
            />
          </div>

          {/* Structured Result Card */}
          <div className="glass-card" style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
            {/* Top Bar with Document Meta & Verification */}
            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', borderBottom: '1px solid var(--border-subtle)', paddingBottom: '1rem', flexWrap: 'wrap', gap: '0.75rem' }}>
              <div>
                <span className="badge badge-pill" style={{ marginRight: '0.5rem' }}>
                  🌐 {currentLanguage?.native || lang.toUpperCase()}
                </span>
                <span style={{ fontSize: '0.88rem', color: 'var(--text-muted)' }}>
                  {t('readingLevelGrade6', 'Reading Level: Grade 6 Plain Language')}
                </span>
              </div>

              <div style={{ display: 'flex', gap: '0.5rem', alignItems: 'center' }}>
                <button 
                  type="button" 
                  className="btn-secondary" 
                  style={{ padding: '0.4rem 0.9rem', fontSize: '0.82rem' }}
                  onClick={handleVerify}
                  disabled={verifying}
                >
                  <span>{verifying ? t('checking', 'Checking...') : t('verifyLiveStatus', '🔄 Verify Live Status')}</span>
                </button>
              </div>
            </div>

            {/* Verification Alert if checked */}
            {verifyData && (
              <div style={{ padding: '0.9rem 1.1rem', background: verifyData.badge.includes('outdated') ? 'rgba(239, 68, 68, 0.1)' : 'rgba(16, 185, 129, 0.1)', borderRadius: 'var(--radius-sm)', border: `1px solid ${verifyData.badge.includes('outdated') ? 'rgba(239, 68, 68, 0.3)' : 'rgba(16, 185, 129, 0.3)'}`, fontSize: '0.85rem' }}>
                <div style={{ marginBottom: '0.4rem' }}>
                  <strong>{t('verificationStatusLabel', 'Verification Status')}:</strong> {verifyData.badge}. {verifyData.notes}
                </div>
                {verifyData.newer_circular_url && (
                  <div style={{ marginTop: '0.4rem' }}>
                    <CitationChip 
                      url={verifyData.newer_circular_url} 
                      label={verifyData.newer_circular_title || t('viewNewerNotification', 'View Newer Notification')} 
                      type="gazette" 
                    />
                  </div>
                )}
              </div>
            )}

            {/* Plain Summary */}
            <div>
              <div style={{ fontSize: '0.78rem', textTransform: 'uppercase', letterSpacing: '0.08em', color: 'var(--accent-info)', fontWeight: 700, marginBottom: '0.4rem' }}>
                {t('plainSummary', 'Plain Language Summary')}
              </div>
              <p style={{ fontSize: '1.05rem', color: 'var(--text-primary)', lineHeight: 1.6, fontWeight: 400 }}>
                {renderClickableContent(result.plain_summary)}
              </p>
            </div>

            {/* Grid: Who is Affected & Deadlines */}
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))', gap: '1.25rem' }}>
              {/* Who is Affected */}
              <div style={{ background: 'var(--bg-glass-input)', padding: '1.2rem', borderRadius: 'var(--radius-md)', border: '1px solid var(--border-subtle)' }}>
                <div style={{ fontSize: '0.85rem', fontWeight: 700, color: 'var(--accent-info)', marginBottom: '0.5rem', display: 'flex', alignItems: 'center', gap: '0.4rem' }}>
                  <span>👥</span> {t('whoIsAffected', 'Who is Affected')}
                </div>
                <div style={{ fontSize: '0.88rem', color: 'var(--text-secondary)', lineHeight: 1.6 }}>
                  {renderClickableContent(result.who_is_affected)}
                </div>
              </div>

              {/* Hard Deadlines */}
              <div style={{ background: 'rgba(245, 158, 11, 0.05)', padding: '1.2rem', borderRadius: 'var(--radius-md)', border: '1px solid rgba(245, 158, 11, 0.2)' }}>
                <div style={{ fontSize: '0.85rem', fontWeight: 700, color: 'var(--accent-warning)', marginBottom: '0.5rem', display: 'flex', alignItems: 'center', gap: '0.4rem' }}>
                  <span>⏰</span> {t('deadlinesTitle', 'Important Deadlines')}
                </div>
                {result.deadlines && result.deadlines.length > 0 ? (
                  <div style={{ display: 'flex', flexDirection: 'column', gap: '0.4rem' }}>
                    {result.deadlines.map((dl, idx) => (
                      <div key={idx} style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', fontSize: '0.88rem' }}>
                        <span style={{ color: 'var(--text-primary)', fontWeight: 600 }}>{dl}</span>
                        <span className="badge badge-warning" style={{ fontSize: '0.72rem' }}>{t('required', 'Required')}</span>
                      </div>
                    ))}
                  </div>
                ) : (
                  <div style={{ fontSize: '0.82rem', color: 'var(--text-muted)' }}>
                    {t('noDeadlineSpecified', 'No hard statutory deadline specified in this circular.')}
                  </div>
                )}
              </div>
            </div>

            {/* Key Takeaways */}
            {result.key_points && result.key_points.length > 0 && (
              <div style={{ background: 'var(--bg-glass-input)', padding: '1.2rem', borderRadius: 'var(--radius-md)', border: '1px solid var(--border-subtle)' }}>
                <div style={{ fontSize: '0.85rem', fontWeight: 700, color: 'var(--accent-info)', marginBottom: '0.5rem' }}>
                  📌 {t('keyTakeaways', 'Key Takeaways')}
                </div>
                <ul style={{ paddingLeft: '1.2rem', fontSize: '0.88rem', color: 'var(--text-primary)', lineHeight: 1.6 }}>
                  {result.key_points.map((pt, idx) => (
                    <li key={idx}>{renderClickableContent(pt)}</li>
                  ))}
                </ul>
              </div>
            )}

            {/* Required Documents */}
            {result.required_documents && result.required_documents.length > 0 && (
              <div style={{ background: 'var(--bg-glass-input)', padding: '1.2rem', borderRadius: 'var(--radius-md)', border: '1px solid var(--border-subtle)' }}>
                <div style={{ fontSize: '0.85rem', fontWeight: 700, color: 'var(--accent-info)', marginBottom: '0.5rem' }}>
                  📁 {t('requiredDocuments', 'Documents Required From Citizen')}
                </div>
                <div style={{ display: 'flex', flexWrap: 'wrap', gap: '0.5rem' }}>
                  {result.required_documents.map((doc, idx) => (
                    <span key={idx} className="badge badge-pill">
                      {renderClickableContent(doc)}
                    </span>
                  ))}
                </div>
              </div>
            )}

            {/* Action Items for Citizen */}
            <div style={{ background: 'rgba(16, 185, 129, 0.05)', padding: '1.2rem', borderRadius: 'var(--radius-md)', border: '1px solid rgba(16, 185, 129, 0.2)' }}>
              <div style={{ fontSize: '0.85rem', fontWeight: 700, color: 'var(--accent-verified)', marginBottom: '0.6rem', display: 'flex', alignItems: 'center', gap: '0.4rem' }}>
                <span>✅</span> {t('citizenActions', 'Action Items for Citizens')}
              </div>
              <ol style={{ paddingLeft: '1.2rem', fontSize: '0.88rem', color: 'var(--text-primary)', lineHeight: 1.65 }}>
                {result.actions_for_citizen.map((action, idx) => (
                  <li key={idx}>{renderClickableContent(action)}</li>
                ))}
              </ol>
            </div>

            {/* Risk Flags */}
            {result.risk_flags && result.risk_flags.length > 0 && (
              <div style={{ background: 'rgba(244, 63, 94, 0.05)', padding: '1.2rem', borderRadius: 'var(--radius-md)', border: '1px solid rgba(244, 63, 94, 0.2)' }}>
                <div style={{ fontSize: '0.85rem', fontWeight: 700, color: 'var(--accent-error)', marginBottom: '0.5rem', display: 'flex', alignItems: 'center', gap: '0.4rem' }}>
                  <span>⚠️</span> {t('riskFlagsTitle', 'Risk Flags & Pitfalls')}
                </div>
                <ul style={{ paddingLeft: '1.2rem', fontSize: '0.88rem', color: 'var(--accent-error)', lineHeight: 1.6 }}>
                  {result.risk_flags.map((flag, idx) => (
                    <li key={idx}>{renderClickableContent(flag)}</li>
                  ))}
                </ul>
              </div>
            )}

            {/* Jargon Glossary */}
            {result.jargon_glossary && result.jargon_glossary.length > 0 && (
              <div style={{ background: 'var(--bg-glass-input)', padding: '1.2rem', borderRadius: 'var(--radius-md)', border: '1px solid var(--border-subtle)' }}>
                <div style={{ fontSize: '0.85rem', fontWeight: 700, color: 'var(--text-primary)', marginBottom: '0.6rem' }}>
                  📖 {t('jargonGlossary', 'Legal & Bureaucratic Jargon Explained')}
                </div>
                <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(240px, 1fr))', gap: '0.75rem' }}>
                  {result.jargon_glossary.map((item, idx) => (
                    <div key={idx} style={{ padding: '0.75rem', background: 'var(--bg-card)', borderRadius: 'var(--radius-sm)', border: '1px solid var(--border-subtle)' }}>
                      <strong style={{ color: 'var(--text-primary)', display: 'block', fontSize: '0.85rem', marginBottom: '0.2rem' }}>
                        {item.term}
                      </strong>
                      <span style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>
                        {renderClickableContent(item.definition)}
                      </span>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Verified Citations & Official Sources */}
            <div style={{ background: 'var(--bg-surface)', padding: '1.2rem', borderRadius: 'var(--radius-md)', border: '1px solid var(--border-card)' }}>
              <div style={{ fontSize: '0.85rem', fontWeight: 700, color: 'var(--accent-info)', marginBottom: '0.75rem', display: 'flex', alignItems: 'center', gap: '0.4rem' }}>
                <span>🔗</span> {t('officialSourcesExtracted', 'Official Sources & Reference Links Extracted')}
              </div>
              <div style={{ display: 'flex', flexWrap: 'wrap', gap: '0.6rem' }}>
                {result.source_url ? (
                  <CitationChip 
                    url={result.source_url} 
                    label={t('officialDocSource', 'Official Document Source')} 
                    type="gazette" 
                  />
                ) : null}
                {result.citations && result.citations.length > 0 ? (
                  result.citations.map((cite, idx) => (
                    <CitationChip
                      key={idx}
                      url={cite.url || cite}
                      label={cite.act_name || cite.title || t('officialReference', 'Official Reference')}
                      type="gazette"
                    />
                  ))
                ) : null}
                {!result.source_url && (!result.citations || result.citations.length === 0) && (
                  <div style={{ fontSize: '0.82rem', color: 'var(--text-muted)' }}>
                    {t('noUrlsCited', 'No specific official web URLs were cited in the extracted document text.')}
                  </div>
                )}
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
