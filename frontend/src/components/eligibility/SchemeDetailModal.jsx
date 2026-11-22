import React, { useEffect } from 'react'
import { createPortal } from 'react-dom'
import CitationChip from '../CitationChip'
import Icon from '../Icon'
import { renderClickableContent } from '../../utils/linkify'
import { useLanguage } from '../../i18n'
import { useSchemeTranslation } from '../../services/schemeTranslation'
import { translateMinistry, translateApplicationMode } from '../../utils/ministryTranslator'

export default function SchemeDetailModal({
  scheme,
  onClose,
  onTestEligibility,
  selectedStateFilter = 'ALL',
}) {
  const { lang, t, currentLanguage } = useLanguage()
  const { scheme: activeScheme, isTranslating } = useSchemeTranslation(scheme, lang)

  // Lock background scroll and handle Escape key
  useEffect(() => {
    document.body.style.overflow = 'hidden'
    const handleKeyDown = (e) => {
      if (e.key === 'Escape') onClose()
    }
    window.addEventListener('keydown', handleKeyDown)
    return () => {
      document.body.style.overflow = ''
      window.removeEventListener('keydown', handleKeyDown)
    }
  }, [onClose])

  if (!scheme) return null

  const displayName = activeScheme.scheme_name || scheme.scheme_name
  const displaySummary = activeScheme.summary || scheme.summary

  const getBenefitTypeLabel = (type) => {
    if (!type) return ''
    const tLower = String(type).toLowerCase()
    if (tLower.includes('cash') || tLower.includes('dbt')) return t('cashDbt', 'Cash / DBT')
    if (tLower.includes('kind') || tLower.includes('material')) return t('inkind', 'In-Kind / Material')
    if (tLower.includes('credit') || tLower.includes('subsidy') || tLower.includes('composite') || tLower.includes('loan')) return t('subsidy', 'Composite / Subsidy')
    if (tLower.includes('health') || tLower.includes('insurance')) return t('healthcare', 'Health / Insurance')
    return type
  }

  const getGovernanceBadge = () => {
    const type = activeScheme.scheme_type || (activeScheme.state === 'Central' ? 'central' : 'state')
    switch (type) {
      case 'integrated':
        return { label: t('integratedScheme', 'Integrated / Joint Scheme'), badgeClass: 'badge-verified', icon: 'refresh' }
      case 'multi_state':
        return { label: t('multiStateScheme', 'Multi-State Regional Scheme'), badgeClass: 'badge-pill', icon: 'globe' }
      case 'local':
        return { label: t('localScheme', 'Local / Municipal Scheme'), badgeClass: 'badge-pill', icon: 'building' }
      case 'central':
        return { label: t('centralScheme', 'Central Scheme (All India)'), badgeClass: 'badge-verified', icon: 'gov' }
      case 'state':
      default: {
        const stateKey = `state_${activeScheme.state}`
        return { label: `${t('stateScheme', 'State Scheme')} • ${t(stateKey, activeScheme.state)}`, badgeClass: 'badge-pill', icon: 'building' }
      }
    }
  }

  const badge = getGovernanceBadge()

  return createPortal(
    <div
      className="modal-overlay"
      onClick={onClose}
      role="dialog"
      aria-modal="true"
      aria-labelledby="modal-scheme-title"
    >
      <div
        className="modal-dialog"
        onClick={(e) => e.stopPropagation()}
      >
        {/* Modal Header */}
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', borderBottom: '1px solid var(--border-subtle)', paddingBottom: '1.25rem', marginBottom: '1.5rem', gap: '1rem' }}>
          <div style={{ flex: 1 }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '0.4rem', flexWrap: 'wrap' }}>
              <span className={`badge ${badge.badgeClass}`} style={{ fontSize: '0.78rem' }}>
                <Icon name={badge.icon} size={13} style={{ marginRight: '4px' }} />
                {badge.label}
              </span>

              {activeScheme.application_mode && (
                <span className="badge badge-pill" style={{ fontSize: '0.72rem' }}>
                  {t('mode', 'Mode')}: {translateApplicationMode(activeScheme.application_mode, lang)}
                </span>
              )}

              <span className="badge badge-pill" style={{ fontSize: '0.75rem' }}>
                {getBenefitTypeLabel(activeScheme.benefit_type) || t('cashDbt', 'Cash / DBT')}
              </span>
              <span style={{ fontSize: '0.78rem', color: 'var(--text-muted)' }}>
                ID: {activeScheme.scheme_id}
              </span>
              {activeScheme.is_live_verified && (
                <span className="badge badge-verified" style={{ fontSize: '0.75rem' }}>
                  <Icon name="check" size={12} style={{ marginRight: '4px' }} />
                  {t('liveWebVerified', 'Live Web Verified')}
                </span>
              )}
              {lang !== 'en' && (
                <span className="badge badge-verified" style={{ fontSize: '0.75rem' }}>
                  🌐 {currentLanguage?.native || lang.toUpperCase()}
                </span>
              )}
            </div>

            <h2 id="modal-scheme-title" style={{ fontSize: '1.5rem', fontWeight: 800, color: 'var(--text-primary)', lineHeight: 1.25 }}>
              {displayName}
            </h2>
            <div style={{ fontSize: '0.88rem', color: 'var(--text-secondary)', marginTop: '0.35rem', display: 'flex', alignItems: 'center', gap: '6px' }}>
              <Icon name="gov" size={16} style={{ color: 'var(--primary-start)' }} />
              <span style={{ fontWeight: 500 }}>{translateMinistry(activeScheme.nodal_authority || activeScheme.ministry, lang)}</span>
            </div>
            <div style={{ fontSize: '0.8rem', color: 'var(--text-secondary)', marginTop: '0.35rem', display: 'flex', alignItems: 'center', gap: '5px' }}>
              <Icon name="target" size={13} style={{ color: 'var(--accent-verified)' }} />
              <span><strong>{t('jurisdictionScope', 'Jurisdiction Scope')}: </strong>
              {activeScheme.scheme_type === 'central' || activeScheme.state === 'Central' || (activeScheme.applicable_states && activeScheme.applicable_states.includes('All India'))
                ? t('applicableAllStates', 'Applicable Across All 28 States & 8 Union Territories (Central Ministry)')
                : `${t('operatesIn', 'Operates in')}: ${Array.isArray(activeScheme.applicable_states) ? activeScheme.applicable_states.map((s) => t(`state_${s}`, s)).join(', ') : t(`state_${activeScheme.state}`, activeScheme.state)}`}
              </span>
            </div>
          </div>

          <button
            type="button"
            onClick={onClose}
            className="modal-close-btn"
            style={{
              background: 'var(--bg-surface-elevated)',
              border: '1px solid var(--border-subtle)',
              borderRadius: '50%',
              width: '36px',
              height: '36px',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              color: 'var(--text-secondary)',
              cursor: 'pointer',
              flexShrink: 0,
            }}
            aria-label={t('close', 'Close')}
          >
            <Icon name="close" size={16} />
          </button>
        </div>

        {/* Action Bar */}
        <div style={{ display: 'flex', gap: '0.5rem', alignItems: 'center', flexWrap: 'wrap', marginBottom: '1.5rem', padding: '0.75rem', background: 'var(--bg-surface-elevated)', borderRadius: 'var(--radius-md)', border: '1px solid var(--border-subtle)' }}>
          <button
            type="button"
            className="btn-secondary"
            style={{ padding: '0.4rem 0.85rem', fontSize: '0.82rem' }}
            onClick={() => {
              navigator.clipboard?.writeText(`${displayName}\n${displaySummary}\nApply: ${activeScheme.official_link}`)
              alert(t('copiedAlert', 'Scheme summary copied to clipboard!'))
            }}
          >
            <Icon name="copy" size={13} />
            <span>{t('copySummary', 'Copy Summary')}</span>
          </button>

          <a
            href={activeScheme.direct_apply_url || activeScheme.official_link}
            target="_blank"
            rel="noopener noreferrer"
            className="btn-primary"
            style={{ padding: '0.4rem 0.85rem', fontSize: '0.82rem', textDecoration: 'none', marginLeft: 'auto', display: 'inline-flex', alignItems: 'center', gap: '4px' }}
          >
            <span>{t('applyOfficialPortal', 'Apply on Official Portal')}</span>
            <Icon name="external" size={12} />
          </a>
        </div>

        {/* Complete Policy Breakdown (Sections 1 to 8) */}
        {isTranslating ? (
          <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem', padding: '1rem 0' }}>
            <div className="skeleton-line" style={{ height: '18px', width: '30%' }}></div>
            <div className="skeleton-line" style={{ height: '50px', width: '100%' }}></div>
            <div className="skeleton-line" style={{ height: '18px', width: '40%' }}></div>
            <div className="skeleton-line" style={{ height: '80px', width: '100%' }}></div>
            <div className="skeleton-line" style={{ height: '18px', width: '35%' }}></div>
            <div className="skeleton-line" style={{ height: '60px', width: '100%' }}></div>
          </div>
        ) : (
          <div style={{ display: 'flex', flexDirection: 'column', gap: '1.35rem' }}>
            {/* 1. Summary */}
            <div>
              <h4 style={{ fontSize: '0.85rem', textTransform: 'uppercase', letterSpacing: '0.06em', color: 'var(--accent-info)', fontWeight: 700, marginBottom: '0.4rem' }}>
                {t('policySummary', '1. Policy Summary')}
              </h4>
              <p style={{ fontSize: '0.95rem', color: 'var(--text-primary)', lineHeight: 1.6 }}>
                {displaySummary}
              </p>
            </div>

            {/* 2. Key Benefits */}
            <div style={{ background: 'var(--bg-glass-input)', padding: '1.1rem', borderRadius: 'var(--radius-md)', border: '1px solid var(--border-subtle)' }}>
              <h4 style={{ fontSize: '0.85rem', textTransform: 'uppercase', letterSpacing: '0.06em', color: 'var(--accent-verified)', fontWeight: 700, marginBottom: '0.5rem' }}>
                {t('financialEntitlements', '2. Financial & Welfare Entitlements')}
              </h4>
              <ul style={{ paddingLeft: '1.2rem', fontSize: '0.9rem', color: 'var(--text-primary)', lineHeight: 1.6 }}>
                {(activeScheme.benefits || []).map((b, idx) => (
                  <li key={idx} style={{ marginBottom: '0.35rem' }}>
                    {renderClickableContent(b)}
                  </li>
                ))}
              </ul>
            </div>

            {/* 3. Complete Eligibility Criteria */}
            <div>
              <h4 style={{ fontSize: '0.85rem', textTransform: 'uppercase', letterSpacing: '0.06em', color: 'var(--accent-info)', fontWeight: 700, marginBottom: '0.5rem' }}>
                {t('whoIsEligible', '3. Who is Eligible')}
              </h4>
              <ul style={{ paddingLeft: '1.2rem', fontSize: '0.9rem', color: 'var(--text-secondary)', lineHeight: 1.6 }}>
                {(activeScheme.eligibility_criteria || []).map((crit, idx) => (
                  <li key={idx} style={{ marginBottom: '0.35rem' }}>
                    {renderClickableContent(crit)}
                  </li>
                ))}
              </ul>
            </div>

            {/* 4. Exclusions */}
            {activeScheme.exclusions && activeScheme.exclusions.length > 0 && (
              <div style={{ background: 'var(--bg-glass-input)', padding: '1.1rem', borderRadius: 'var(--radius-md)', border: '1px solid var(--border-subtle)' }}>
                <h4 style={{ fontSize: '0.85rem', textTransform: 'uppercase', letterSpacing: '0.06em', color: 'var(--accent-info)', fontWeight: 700, marginBottom: '0.5rem' }}>
                  {t('exclusions', '4. Exclusions / Who Cannot Apply')}
                </h4>
                <ul style={{ paddingLeft: '1.2rem', fontSize: '0.88rem', color: 'var(--text-primary)', lineHeight: 1.6 }}>
                  {activeScheme.exclusions.map((ex, idx) => (
                    <li key={idx} style={{ marginBottom: '0.3rem' }}>
                      {renderClickableContent(ex)}
                    </li>
                  ))}
                </ul>
              </div>
            )}

            {/* 5. Documents Checklist */}
            <div>
              <h4 style={{ fontSize: '0.85rem', textTransform: 'uppercase', letterSpacing: '0.06em', color: 'var(--accent-info)', fontWeight: 700, marginBottom: '0.5rem' }}>
                {t('requiredDocuments', '5. Required Documents Checklist')}
              </h4>
              <div style={{ display: 'flex', flexWrap: 'wrap', gap: '0.5rem' }}>
                {(activeScheme.documents_required || activeScheme.documents_needed || []).map((doc, idx) => (
                  <span key={idx} className="badge badge-pill" style={{ fontSize: '0.82rem', padding: '0.4rem 0.8rem' }}>
                    <Icon name="check" size={12} style={{ marginRight: '4px' }} />
                    {doc}
                  </span>
                ))}
              </div>
            </div>

            {/* 6. Step-by-Step Application */}
            <div style={{ background: 'var(--bg-glass-input)', padding: '1.25rem', borderRadius: 'var(--radius-md)', border: '1px solid var(--border-subtle)' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '0.6rem', flexWrap: 'wrap', gap: '0.5rem' }}>
                <h4 style={{ fontSize: '0.85rem', textTransform: 'uppercase', letterSpacing: '0.06em', color: 'var(--text-primary)', fontWeight: 700, margin: 0 }}>
                  {t('applicationProcedure', '6. Application Procedure & Direct Portals')}
                </h4>
                {activeScheme.application_mode && (
                  <span className="badge badge-pill" style={{ fontSize: '0.72rem' }}>
                    {t('mode', 'Mode')}: {translateApplicationMode(activeScheme.application_mode, lang)}
                  </span>
                )}
              </div>

              {activeScheme.application_steps && activeScheme.application_steps.length > 0 ? (
                <ol style={{ paddingLeft: '1.2rem', fontSize: '0.9rem', color: 'var(--text-secondary)', lineHeight: 1.6, marginBottom: '1rem' }}>
                  {activeScheme.application_steps.map((step, idx) => (
                    <li key={idx} style={{ marginBottom: '0.4rem' }}>
                      {renderClickableContent(step)}
                    </li>
                  ))}
                </ol>
              ) : (
                <p style={{ fontSize: '0.9rem', color: 'var(--text-secondary)', lineHeight: 1.6, marginBottom: '1rem' }}>
                  {renderClickableContent(activeScheme.how_to_apply)}
                </p>
              )}

              {/* State-by-State Direct Apply Links (for Integrated Schemes) */}
              {activeScheme.state_apply_links && activeScheme.state_apply_links.length > 0 && (
                <div style={{ background: 'var(--bg-card)', padding: '1rem', borderRadius: 'var(--radius-sm)', border: '1px solid var(--border-card)', marginTop: '0.75rem' }}>
                  <div style={{ fontSize: '0.8rem', fontWeight: 700, color: 'var(--accent-info)', marginBottom: '0.5rem', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                    <span>{t('statePortals', 'State-Specific Official Portals')}:</span>
                    <span style={{ fontSize: '0.72rem', color: 'var(--text-muted)' }}>{activeScheme.state_apply_links.length} {t('statesAvailable', 'States Available')}</span>
                  </div>
                  <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(220px, 1fr))', gap: '0.5rem' }}>
                    {activeScheme.state_apply_links.map((link, idx) => (
                      <a
                        key={idx}
                        href={link.url}
                        target="_blank"
                        rel="noopener noreferrer"
                        style={{
                          fontSize: '0.78rem',
                          padding: '0.45rem 0.65rem',
                          background: selectedStateFilter !== 'ALL' && link.state.includes(selectedStateFilter) ? 'var(--primary-color)' : 'var(--bg-surface-elevated)',
                          color: selectedStateFilter !== 'ALL' && link.state.includes(selectedStateFilter) ? '#ffffff' : 'var(--text-primary)',
                          border: '1px solid var(--border-card)',
                          borderRadius: 'var(--radius-sm)',
                          textDecoration: 'none',
                          display: 'flex',
                          justifyContent: 'space-between',
                          alignItems: 'center',
                        }}
                      >
                        <div>
                          <strong>{t(`state_${link.state}`, link.state)}</strong>
                          <div style={{ fontSize: '0.7rem', color: selectedStateFilter !== 'ALL' && link.state.includes(selectedStateFilter) ? 'rgba(255,255,255,0.85)' : 'var(--text-muted)' }}>
                            {link.portal_name}
                          </div>
                        </div>
                        <Icon name="external" size={11} />
                      </a>
                    ))}
                  </div>
                </div>
              )}
            </div>

            {/* 7 & 8: Citations & Test Eligibility */}
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', borderTop: '1px solid var(--border-subtle)', paddingTop: '1.25rem', marginTop: '0.5rem', flexWrap: 'wrap', gap: '1rem' }}>
              <div>
                <div style={{ fontSize: '0.78rem', color: 'var(--text-muted)', marginBottom: '0.35rem' }}>
                  {t('statutoryReferences', '7. Statutory References & Official Citations')}:
                </div>
                <div style={{ display: 'flex', flexWrap: 'wrap', gap: '0.5rem' }}>
                  <CitationChip
                    url={activeScheme.official_link}
                    label={`${activeScheme.scheme_id} ${t('officialSourceLink', 'Official Portal')}`}
                    type="scheme"
                  />
                  {activeScheme.myscheme_link && (
                    <CitationChip
                      url={activeScheme.myscheme_link}
                      label={`myScheme ${t('nationalPlatform', 'National Platform')}`}
                      type="portal"
                    />
                  )}
                </div>
              </div>

              <button
                type="button"
                className="btn-primary"
                onClick={() => onTestEligibility(activeScheme)}
              >
                <span>{t('testEligibility', '8. Check Rules & Evaluate Eligibility')}</span>
                <Icon name="arrow-right" size={13} />
              </button>
            </div>
          </div>
        )}
      </div>
    </div>,
    document.body
  )
}
