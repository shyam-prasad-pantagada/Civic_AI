import React from 'react'
import Icon from '../Icon'
import { useLanguage } from '../../i18n'
import { translateMinistry } from '../../utils/ministryTranslator'

export default function EligibilityResults({
  results,
  onOpenDetails,
  onAnswerFollowUp,
}) {
  const { lang, t } = useLanguage()

  if (!results) return null

  const eligibleSchemes = results.eligible || []
  const needMoreInfoSchemes = results.need_more_info || []
  const notEligibleSchemes = results.not_eligible || []

  return (
    <div style={{ marginTop: '2.5rem', marginBottom: '3rem' }}>
      <div style={{ textAlign: 'center', marginBottom: '2rem' }}>
        <span className="badge badge-verified" style={{ marginBottom: '0.6rem' }}>
          <Icon name="check" size={12} style={{ marginRight: '4px' }} />
          {t('evaluationComplete', 'Evaluation Complete')}
        </span>
        <h2 style={{ fontFamily: 'var(--font-family-heading)', fontSize: '1.85rem', fontWeight: 800 }}>
          {t('eligibilityResultsTitle', 'Your Welfare Eligibility Results')}
        </h2>
        <p style={{ color: 'var(--text-secondary)', fontSize: '0.92rem', maxWidth: '580px', margin: '0.35rem auto 0' }}>
          {t('eligibleCount', `Found ${eligibleSchemes.length} schemes you qualify for`)}, {needMoreInfoSchemes.length} {t('needMoreInfoCount', 'requiring extra info')}, {t('notEligibleCount', `and ${notEligibleSchemes.length} not applicable`)}.
        </p>
      </div>

      {/* Eligible Schemes Section */}
      {eligibleSchemes.length > 0 && (
        <div style={{ marginBottom: '2.5rem' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '1rem' }}>
            <span style={{ width: '10px', height: '10px', borderRadius: '50%', background: 'var(--accent-verified)' }}></span>
            <h3 style={{ fontSize: '1.15rem', fontWeight: 700, color: 'var(--accent-verified)' }}>
              {t('eligible', 'Eligible Schemes')} ({eligibleSchemes.length})
            </h3>
          </div>

          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(320px, 1fr))', gap: '1.25rem' }}>
            {eligibleSchemes.map((item, idx) => {
              return (
                <div
                  key={idx}
                  className="card"
                  style={{
                    borderLeft: '4px solid var(--accent-verified)',
                    display: 'flex',
                    flexDirection: 'column',
                    justifyContent: 'space-between',
                  }}
                >
                  <div>
                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '0.5rem' }}>
                      <span className="badge badge-verified" style={{ fontSize: '0.72rem' }}>
                        <Icon name="check" size={11} style={{ marginRight: '3px' }} />
                        {t('eligible', 'Eligible')}
                      </span>
                      <span style={{ fontSize: '0.74rem', color: 'var(--text-muted)' }}>
                        {item.state === 'Central' ? t('centralScheme', 'Central Scheme') : `${t('state', 'State')}: ${item.state}`}
                      </span>
                    </div>

                    <h4 style={{ fontSize: '1.1rem', fontWeight: 700, color: 'var(--text-primary)', marginBottom: '0.35rem' }}>
                      {item.scheme_name}
                    </h4>
                    {(item.nodal_authority || item.ministry) && (
                      <div style={{ fontSize: '0.78rem', color: 'var(--text-muted)', marginBottom: '0.55rem', display: 'flex', alignItems: 'center', gap: '5px' }}>
                        <span>🏛️</span>
                        <span>{translateMinistry(item.nodal_authority || item.ministry, lang)}</span>
                      </div>
                    )}

                    {/* Deciding Rule */}
                    <div style={{ fontSize: '0.8rem', color: 'var(--text-muted)', marginBottom: '0.75rem', background: 'var(--bg-glass-input)', padding: '0.4rem 0.65rem', borderRadius: 'var(--radius-sm)' }}>
                      <strong>{t('rulePassed', 'Rule passed')}: </strong> {item.reason}
                    </div>

                    {/* Benefits */}
                    {item.benefits && item.benefits.length > 0 && (
                      <div style={{ fontSize: '0.84rem', color: 'var(--text-primary)', marginBottom: '1rem', lineHeight: 1.5 }}>
                        {item.benefits[0]}
                      </div>
                    )}
                  </div>

                  {/* Action Bar */}
                  <div style={{ display: 'flex', gap: '0.45rem', alignItems: 'center', paddingTop: '0.75rem', borderTop: '1px solid var(--border-subtle)', flexWrap: 'wrap' }}>
                    <button
                      type="button"
                      className="btn-secondary"
                      style={{ padding: '0.35rem 0.75rem', fontSize: '0.78rem' }}
                      onClick={() => onOpenDetails(item)}
                    >
                      <span>{t('policyDetails', 'Policy Details')}</span>
                      <Icon name="chevron-down" size={12} />
                    </button>

                    <a
                      href={item.direct_apply_url || item.official_link}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="btn-primary"
                      style={{ padding: '0.35rem 0.75rem', fontSize: '0.78rem', textDecoration: 'none', marginLeft: 'auto', display: 'inline-flex', alignItems: 'center', gap: '4px' }}
                    >
                      <span>{t('applyOfficial', 'Apply')}</span>
                      <Icon name="external" size={11} />
                    </a>
                  </div>
                </div>
              )
            })}
          </div>
        </div>
      )}

      {/* Need More Info Schemes */}
      {needMoreInfoSchemes.length > 0 && (
        <div style={{ marginBottom: '2.5rem' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '1rem' }}>
            <span style={{ width: '10px', height: '10px', borderRadius: '50%', background: 'var(--accent-warning)' }}></span>
            <h3 style={{ fontSize: '1.15rem', fontWeight: 700, color: 'var(--accent-warning)' }}>
              {t('requiresMoreInfo', 'Requires More Information')} ({needMoreInfoSchemes.length})
            </h3>
          </div>

          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(320px, 1fr))', gap: '1.25rem' }}>
            {needMoreInfoSchemes.map((item, idx) => (
              <div
                key={idx}
                className="card"
                style={{
                  borderLeft: '4px solid var(--accent-warning)',
                  background: 'var(--bg-surface-elevated)',
                }}
              >
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '0.4rem' }}>
                  <span className="badge badge-warning" style={{ fontSize: '0.72rem' }}>
                    {t('needInfo', 'Need Info')}
                  </span>
                  <span style={{ fontSize: '0.74rem', color: 'var(--text-muted)' }}>
                    {item.scheme_id}
                  </span>
                </div>

                <h4 style={{ fontSize: '1.05rem', fontWeight: 700, color: 'var(--text-primary)', marginBottom: '0.35rem' }}>
                  {item.scheme_name}
                </h4>

                <p style={{ fontSize: '0.84rem', color: 'var(--text-secondary)', marginBottom: '0.75rem' }}>
                  {item.missing_parameter_question || item.reason}
                </p>

                <div style={{ display: 'flex', gap: '0.5rem', alignItems: 'center' }}>
                  <button
                    type="button"
                    className="btn-secondary"
                    style={{ padding: '0.35rem 0.75rem', fontSize: '0.78rem' }}
                    onClick={() => onOpenDetails(item)}
                  >
                    <span>{t('viewRules', 'View Scheme Rules')}</span>
                  </button>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Not Eligible Schemes (Collapsible) */}
      {notEligibleSchemes.length > 0 && (
        <details className="card" style={{ padding: '1rem 1.25rem' }}>
          <summary style={{ cursor: 'pointer', fontWeight: 700, fontSize: '0.92rem', color: 'var(--text-muted)' }}>
            {t('viewIneligible', 'View Ineligible Schemes')} ({notEligibleSchemes.length}) — {t('clickInspectExclusion', 'Click to inspect exclusion criteria')}
          </summary>
          <div style={{ marginTop: '1rem', display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
            {notEligibleSchemes.map((item, idx) => (
              <div key={idx} style={{ padding: '0.75rem', background: 'var(--bg-glass-input)', borderRadius: 'var(--radius-sm)', border: '1px solid var(--border-subtle)', display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: '0.5rem' }}>
                <div>
                  <div style={{ fontWeight: 600, fontSize: '0.9rem', color: 'var(--text-primary)' }}>{item.scheme_name}</div>
                  <div style={{ fontSize: '0.78rem', color: 'var(--accent-error)', marginTop: '2px' }}>
                    ✕ {t('exclusionReason', 'Exclusion reason')}: {item.reason}
                  </div>
                </div>
                <button
                  type="button"
                  className="btn-secondary"
                  style={{ padding: '0.25rem 0.6rem', fontSize: '0.74rem' }}
                  onClick={() => onOpenDetails(item)}
                >
                  {t('inspectPolicy', 'Inspect Policy')}
                </button>
              </div>
            ))}
          </div>
        </details>
      )}
    </div>
  )
}
