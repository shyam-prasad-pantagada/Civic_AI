import React, { useState } from 'react'
import SourceBadge from '../components/SourceBadge'
import CitationChip from '../components/CitationChip'
import { renderClickableContent } from '../utils/linkify'
import { useLanguage } from '../i18n'

const API_BASE = import.meta.env.VITE_API_URL || (import.meta.env.PROD ? '' : 'http://localhost:8000')

export default function RightsPage() {
  const { lang, t, currentLanguage } = useLanguage()
  const [query, setQuery] = useState('')
  const [state, setState] = useState('Central')
  const [loading, setLoading] = useState(false)
  const [result, setResult] = useState(null)
  const [error, setError] = useState(null)

  const quickQuestions = [
    t('q1', 'Can my landlord evict me without notice?'),
    t('q2', 'What can I do if a company refuses refund for a defective product?'),
    t('q3', 'How many days does an officer have to reply to an RTI application?'),
    t('q4', 'What legal protections exist against domestic violence and forceful eviction from home?'),
    t('q5', 'Can senior citizens claim maintenance from their adult children?'),
    t('q6', 'What are my rights if an employer or contractor delays minimum wages?'),
  ]

  const handleSearch = async (questionToSearch) => {
    const q = questionToSearch || query
    if (!q.trim()) return

    setLoading(true)
    setError(null)

    try {
      const res = await fetch(`${API_BASE}/api/rights?lang=${lang}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          question: q,
          state: state === 'Central' ? null : state,
          lang: lang,
        }),
      })

      if (!res.ok) {
        const errJson = await res.json().catch(() => ({}))
        throw new Error(errJson.detail || `Server error (${res.status})`)
      }

      const data = await res.json()
      setResult(data)
    } catch (err) {
      console.error('Rights query failed:', err)
      setError(err.message || 'Failed to search rights. Please verify backend connection.')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div>
      {/* Header */}
      <div className="page-header">
        <span className="badge badge-pill page-badge">
          <span>⚖️</span>
          <span>Rights &amp; Legal Intelligence • {currentLanguage?.native || lang.toUpperCase()}</span>
        </span>
        <h1 className="page-title">
          {t('rightsTitle', 'Citizen Rights & Legal Remedies')}
        </h1>
        <p className="page-subtitle">
          {t('rightsSub', 'Instant guidance on citizen rights under Indian law, regulatory rules, and official citations.')}
        </p>
      </div>

      <div style={{ maxWidth: '880px', margin: '0 auto', display: 'flex', flexDirection: 'column', gap: '2rem' }}>
        {/* Search Box */}
        <div className="glass-card">
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1rem', flexWrap: 'wrap', gap: '0.75rem' }}>
            <span style={{ fontSize: '0.85rem', textTransform: 'uppercase', letterSpacing: '0.08em', color: 'var(--accent-info)', fontWeight: 700 }}>
              {t('askRightsQuestion', 'Ask Any Citizen Rights Question')}
            </span>
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
              <span style={{ fontSize: '0.82rem', color: 'var(--text-muted)' }}>{t('state', 'State')}:</span>
              <select 
                className="select" 
                style={{ width: 'auto', padding: '0.35rem 1.8rem 0.35rem 0.75rem', fontSize: '0.82rem' }}
                value={state}
                onChange={(e) => setState(e.target.value)}
              >
                <option value="Central">{t('state_Central', 'Central / All India')}</option>
                <option value="DL">{t('state_DL', 'Delhi')}</option>
                <option value="MH">{t('state_MH', 'Maharashtra')}</option>
                <option value="KA">{t('state_KA', 'Karnataka')}</option>
                <option value="UP">{t('state_UP', 'Uttar Pradesh')}</option>
                <option value="TN">{t('state_TN', 'Tamil Nadu')}</option>
                <option value="GJ">{t('state_GJ', 'Gujarat')}</option>
                <option value="WB">{t('state_WB', 'West Bengal')}</option>
                <option value="TS">{t('state_TS', 'Telangana')}</option>
                <option value="AP">{t('state_AP', 'Andhra Pradesh')}</option>
              </select>
            </div>
          </div>

          <div style={{ display: 'flex', gap: '0.75rem', marginBottom: '1.25rem', flexWrap: 'wrap', alignItems: 'center' }}>
            <input 
              type="text" 
              className="input" 
              style={{ flex: 1, minWidth: '240px' }}
              placeholder={t('askRightsPlaceholder', 'Ask about consumer refunds, tenant eviction, RTI, police FIR, labor rights...')}
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              onKeyDown={(e) => e.key === 'Enter' && handleSearch()}
            />
            <button 
              type="button" 
              className="btn-primary" 
              onClick={() => handleSearch()}
              disabled={loading || !query.trim()}
            >
              <span>{loading ? 'Searching Rights...' : t('askAiRightsBtn', 'Search Rights')}</span>
              <span>→</span>
            </button>
          </div>

          {/* Quick Questions Pills */}
          <div>
            <div style={{ fontSize: '0.78rem', color: 'var(--text-muted)', marginBottom: '0.5rem' }}>
              {t('frequentlyAskedQueries', 'Frequently Asked Rights Queries (click to test):')}
            </div>
            <div style={{ display: 'flex', flexWrap: 'wrap', gap: '0.5rem' }}>
              {quickQuestions.map((q, idx) => (
                <button
                  key={idx}
                  type="button"
                  onClick={() => {
                    setQuery(q)
                    handleSearch(q)
                  }}
                  className="quick-query-btn"
                >
                  {q}
                </button>
              ))}
            </div>
          </div>
        </div>

        {/* Error */}
        {error && (
          <div style={{ padding: '1rem', background: 'var(--accent-error-bg)', border: '1px solid rgba(239, 68, 68, 0.3)', borderRadius: 'var(--radius-md)', color: 'var(--accent-error)' }}>
            <strong>Error:</strong> {error}
          </div>
        )}

        {/* Loading Spinner */}
        {loading && (
          <div style={{ textAlign: 'center', margin: '2.5rem 0' }}>
            <div className="loading-spinner"></div>
            <div style={{ marginTop: '1rem', color: 'var(--text-secondary)', fontSize: '0.92rem' }}>
              {t('searchingRightsDb', 'Checking rights repository and evaluating guidance...')}
            </div>
          </div>
        )}

        {/* Results Area */}
        {result && (
          <div className="glass-card" style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
            {/* Header Bar */}
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', borderBottom: '1px solid var(--border-subtle)', paddingBottom: '1rem', flexWrap: 'wrap', gap: '0.75rem' }}>
              <div>
                <span className={`badge ${result.has_official_source ? 'badge-verified' : 'badge-warning'}`} style={{ marginRight: '0.5rem' }}>
                  {result.has_official_source ? t('rightsProtectionFound', '✓ Official Rights Source Found') : t('dynamicRightsGuidance', '✦ Dynamic AI Rights Guidance')}
                </span>
                <span style={{ fontSize: '0.85rem', color: 'var(--text-muted)' }}>
                  {t('questionLabel', 'Question')}: "{result.question}"
                </span>
              </div>
            </div>

            {/* Official Citations Box with Clickable Citation Chips */}
            {result.citations && result.citations.length > 0 ? (
              <div style={{ padding: '1.1rem', background: 'var(--bg-surface)', border: '1px solid var(--border-card)', borderRadius: 'var(--radius-md)' }}>
                <div style={{ fontSize: '0.8rem', textTransform: 'uppercase', letterSpacing: '0.06em', color: 'var(--accent-info)', fontWeight: 700, marginBottom: '0.65rem' }}>
                  {t('officialCitations', 'Official Rights Citations (India Code / Official Acts)')}
                </div>
                <div style={{ display: 'flex', flexWrap: 'wrap', gap: '0.65rem' }}>
                  {result.citations.map((c, idx) => (
                    <CitationChip
                      key={idx}
                      url={c.url}
                      label={c.act_name}
                      section={c.section}
                      type="act"
                    />
                  ))}
                  <CitationChip
                    url="https://www.indiacode.nic.in"
                    label={t('indiaCodeRepository', 'India Code Digital Repository')}
                    type="code"
                  />
                </div>
              </div>
            ) : (
              <div style={{ padding: '1rem', background: 'rgba(245, 158, 11, 0.08)', border: '1px solid rgba(245, 158, 11, 0.25)', borderRadius: 'var(--radius-md)', fontSize: '0.88rem' }}>
                <strong>{t('nonStatutoryRightsNotice', 'Not Directly Under Statutory Law: This topic is not governed by a standalone Act in our indexed rights repository; live AI rights & regulatory guidance is shown below.')}</strong>
              </div>
            )}

            {/* Your Rights */}
            {result.your_rights && result.your_rights.length > 0 && (
              <div>
                <div style={{ fontSize: '0.8rem', textTransform: 'uppercase', letterSpacing: '0.08em', color: 'var(--accent-verified)', fontWeight: 700, marginBottom: '0.6rem', display: 'flex', alignItems: 'center', gap: '0.4rem' }}>
                  <span>🛡️</span> {t('yourProtectedRights', 'Your Rights & Guidance')}
                </div>
                <div style={{ display: 'flex', flexDirection: 'column', gap: '0.6rem' }}>
                  {result.your_rights.map((right, idx) => (
                    <div key={idx} style={{ padding: '0.9rem 1.1rem', background: 'rgba(16, 185, 129, 0.05)', border: '1px solid rgba(16, 185, 129, 0.15)', borderRadius: 'var(--radius-sm)', fontSize: '0.92rem', color: 'var(--text-primary)', lineHeight: 1.55 }}>
                      {renderClickableContent(right)}
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* What You Can Do (Remedies) */}
            {result.what_you_can_do && result.what_you_can_do.length > 0 && (
              <div>
                <div style={{ fontSize: '0.8rem', textTransform: 'uppercase', letterSpacing: '0.08em', color: 'var(--accent-info)', fontWeight: 700, marginBottom: '0.6rem', display: 'flex', alignItems: 'center', gap: '0.4rem' }}>
                  <span>📋</span> {t('immediateRemedies', 'Immediate Steps & Remedies Available to You')}
                </div>
                <ol style={{ paddingLeft: '1.25rem', fontSize: '0.9rem', color: 'var(--text-primary)', lineHeight: 1.65 }}>
                  {result.what_you_can_do.map((step, idx) => (
                    <li key={idx} style={{ marginBottom: '0.4rem' }}>
                      {renderClickableContent(step)}
                    </li>
                  ))}
                </ol>
              </div>
            )}

            {/* Free Legal Aid / Where to Complain */}
            {result.where_to_complain_or_get_free_help && result.where_to_complain_or_get_free_help.length > 0 && (
              <div style={{ background: 'var(--bg-glass-input)', padding: '1.25rem', borderRadius: 'var(--radius-md)', border: '1px solid var(--border-subtle)' }}>
                <div style={{ fontSize: '0.8rem', textTransform: 'uppercase', letterSpacing: '0.08em', color: 'var(--text-primary)', fontWeight: 700, marginBottom: '0.6rem', display: 'flex', alignItems: 'center', gap: '0.4rem' }}>
                  <span>🏛️</span> {t('freeLegalAidHeading', 'Where to Lodge Complaints & Free Legal Aid')}
                </div>
                <ul style={{ paddingLeft: '1.2rem', fontSize: '0.88rem', color: 'var(--text-secondary)', lineHeight: 1.6 }}>
                  {result.where_to_complain_or_get_free_help.map((item, idx) => (
                    <li key={idx} style={{ marginBottom: '0.35rem' }}>
                      {renderClickableContent(item)}
                    </li>
                  ))}
                </ul>
              </div>
            )}

            {/* Freshness Status & Verification Metadata */}
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', borderTop: '1px solid var(--border-subtle)', paddingTop: '1rem', flexWrap: 'wrap', gap: '0.75rem' }}>
              <SourceBadge 
                status={result.has_official_source ? 'verified' : 'could_not_verify'} 
                sourceName="Rights & Official Sources" 
                sourceUrl="https://www.indiacode.nic.in" 
                lastVerified={t('sectionCitationsChecked', 'Rights & citations checked')} 
              />
              <span style={{ fontSize: '0.78rem', color: 'var(--text-muted)' }}>
                {t('stateContext', 'State Context')}: <strong>{result.state || 'Central'}</strong>
              </span>
            </div>
          </div>
        )}
      </div>
    </div>
  )
}
