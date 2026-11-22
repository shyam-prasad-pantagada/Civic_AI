import React from 'react'
import Icon from '../Icon'
import { renderClickableContent } from '../../utils/linkify'
import { useLanguage } from '../../i18n'
import { useSchemeTranslation } from '../../services/schemeTranslation'
import { translateMinistry, translateApplicationMode } from '../../utils/ministryTranslator'

export default function SchemeCard({
  scheme,
  onOpenDetails,
  onTestEligibility,
}) {
  const { lang, t } = useLanguage()
  const { scheme: activeScheme, isTranslating } = useSchemeTranslation(scheme, lang)

  const displayName = activeScheme.scheme_name || scheme.scheme_name
  const displaySummary = activeScheme.summary || scheme.summary

  const getGovernanceBadge = () => {
    const type = activeScheme.scheme_type || (activeScheme.state === 'Central' ? 'central' : 'state')
    switch (type) {
      case 'integrated':
        return {
          label: t('integratedScheme', 'Integrated / Joint Scheme'),
          subtitle: t('coFundedCenterState', 'Co-Funded Center + State'),
          badgeClass: 'badge-verified',
          icon: 'refresh',
        }
      case 'multi_state':
        return {
          label: t('multiStateScheme', 'Multi-State Regional Scheme'),
          subtitle: 'Regional / Inter-State',
          badgeClass: 'badge-pill',
          icon: 'globe',
        }
      case 'local':
        return {
          label: t('localScheme', 'Local / Municipal Scheme'),
          subtitle: 'District Administered',
          badgeClass: 'badge-pill',
          icon: 'building',
        }
      case 'central':
        return {
          label: t('centralScheme', 'Central Scheme (All India)'),
          subtitle: t('applicableAllStates', 'Applicable Across All 28 States & 8 UTs'),
          badgeClass: 'badge-verified',
          icon: 'gov',
        }
      case 'state':
      default: {
        const stateKey = `state_${activeScheme.state}`
        const stateName = t(stateKey, activeScheme.state)
        return {
          label: `${t('stateScheme', 'State Scheme')} • ${stateName}`,
          subtitle: t('administeredByState', 'Administered by State Government'),
          badgeClass: 'badge-pill',
          icon: 'building',
        }
      }
    }
  }

  const badge = getGovernanceBadge()

  const getBenefitTypeLabel = (type) => {
    if (!type) return ''
    const tLower = String(type).toLowerCase()
    if (tLower.includes('cash') || tLower.includes('dbt')) return t('cashDbt', 'Cash / DBT')
    if (tLower.includes('kind') || tLower.includes('material')) return t('inkind', 'In-Kind / Material')
    if (tLower.includes('credit') || tLower.includes('subsidy') || tLower.includes('composite') || tLower.includes('loan')) return t('subsidy', 'Composite / Subsidy')
    if (tLower.includes('health') || tLower.includes('insurance')) return t('healthcare', 'Health / Insurance')
    return type
  }

  return (
    <div className="card scheme-directory-card" style={{ display: 'flex', flexDirection: 'column', justifyContent: 'space-between' }}>
      <div>
        {/* Top Badges Bar */}
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', gap: '0.5rem', marginBottom: '0.75rem', flexWrap: 'wrap' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.4rem', flexWrap: 'wrap' }}>
            <span className={`badge ${badge.badgeClass}`} style={{ fontSize: '0.74rem' }}>
              <Icon name={badge.icon} size={12} style={{ marginRight: '4px' }} />
              {badge.label}
            </span>
            {activeScheme.application_mode && (
              <span className="badge badge-pill" style={{ fontSize: '0.7rem' }}>
                {translateApplicationMode(activeScheme.application_mode, lang)}
              </span>
            )}
            {activeScheme.benefit_type && (
              <span className="badge badge-pill" style={{ fontSize: '0.7rem' }}>
                {getBenefitTypeLabel(activeScheme.benefit_type)}
              </span>
            )}
          </div>

          {activeScheme.is_live_verified && (
            <span className="badge badge-verified" style={{ fontSize: '0.72rem' }}>
              <Icon name="check" size={11} style={{ marginRight: '3px' }} />
              {t('liveWebVerified', 'Live Web Verified')}
            </span>
          )}
        </div>

        {/* Scheme Name & Ministry */}
        {isTranslating ? (
          <div style={{ marginBottom: '0.75rem' }}>
            <div className="skeleton-line" style={{ height: '22px', width: '85%', marginBottom: '8px' }}></div>
            <div className="skeleton-line" style={{ height: '14px', width: '50%', marginBottom: '12px' }}></div>
            <div className="skeleton-line" style={{ height: '14px', width: '100%', marginBottom: '6px' }}></div>
            <div className="skeleton-line" style={{ height: '14px', width: '70%', marginBottom: '12px' }}></div>
          </div>
        ) : (
          <>
            <h3 style={{ fontSize: '1.15rem', fontWeight: 800, color: 'var(--text-primary)', marginBottom: '0.35rem', lineHeight: 1.35 }}>
              {displayName}
            </h3>
            <div style={{ fontSize: '0.8rem', color: 'var(--text-secondary)', marginBottom: '0.65rem', display: 'flex', alignItems: 'center', gap: '6px' }}>
              <Icon name="gov" size={14} style={{ color: 'var(--primary-start)' }} />
              <span style={{ fontWeight: 500 }}>{translateMinistry(activeScheme.nodal_authority || activeScheme.ministry, lang)}</span>
            </div>

            {/* Plain Language Summary */}
            <p style={{ fontSize: '0.86rem', color: 'var(--text-secondary)', lineHeight: 1.55, marginBottom: '0.85rem' }}>
              {displaySummary || t('seeOfficialPortalDetail', 'See the official portal for this detail')}
            </p>
          </>
        )}

        {/* Key Entitlement Box */}
        {activeScheme.benefits && activeScheme.benefits.length > 0 ? (
          <div style={{ background: 'var(--bg-glass-input)', padding: '0.75rem 0.9rem', borderRadius: 'var(--radius-sm)', border: '1px solid var(--border-subtle)', marginBottom: '1rem' }}>
            <div style={{ fontSize: '0.75rem', fontWeight: 700, color: 'var(--accent-verified)', marginBottom: '0.25rem', display: 'flex', alignItems: 'center', gap: '4px' }}>
              <Icon name="check" size={12} />
              <span>{t('keyBenefits', 'Key Benefits:')}</span>
            </div>
            <div style={{ fontSize: '0.82rem', color: 'var(--text-primary)', lineHeight: 1.45 }}>
              {renderClickableContent(activeScheme.benefits[0])}
            </div>
          </div>
        ) : (
          <div style={{ background: 'var(--bg-glass-input)', padding: '0.6rem 0.85rem', borderRadius: 'var(--radius-sm)', border: '1px solid var(--border-subtle)', marginBottom: '1rem', fontSize: '0.78rem', color: 'var(--text-muted)' }}>
            <span>{t('seeOfficialPortalDetail', 'See the official portal for this detail')}</span>
          </div>
        )}
      </div>

      {/* Card Action Bar */}
      <div>
        <div style={{ display: 'flex', gap: '0.45rem', alignItems: 'center', flexWrap: 'wrap', paddingTop: '0.75rem', borderTop: '1px solid var(--border-subtle)', marginBottom: '0.65rem' }}>
          <button
            type="button"
            className="btn-secondary"
            style={{ padding: '0.4rem 0.75rem', fontSize: '0.78rem' }}
            onClick={() => onOpenDetails(activeScheme)}
            title="Read full 8-point statutory policy breakdown"
          >
            <span>{t('viewPolicyDetails', 'Policy Details')}</span>
            <Icon name="chevron-down" size={12} />
          </button>

          <button
            type="button"
            className="btn-secondary"
            style={{ padding: '0.4rem 0.75rem', fontSize: '0.78rem' }}
            onClick={() => onTestEligibility(activeScheme)}
            title="Evaluate your profile against this scheme's rules"
          >
            <span>{t('testEligibility', 'Check Rules')}</span>
            <Icon name="arrow-right" size={12} />
          </button>

          <a
            href={activeScheme.direct_apply_url || activeScheme.official_link}
            target="_blank"
            rel="noopener noreferrer"
            className="btn-primary"
            style={{ padding: '0.4rem 0.85rem', fontSize: '0.78rem', textDecoration: 'none', marginLeft: 'auto', display: 'inline-flex', alignItems: 'center', gap: '4px' }}
            title="Open official government application portal"
          >
            <span>{t('applyOfficialPortal', 'Apply Now')}</span>
            <Icon name="external" size={11} />
          </a>
        </div>

        {/* Official Portal Source Chip */}
        <div style={{ fontSize: '0.74rem', color: 'var(--text-muted)', display: 'flex', alignItems: 'center', gap: '0.35rem' }}>
          <Icon name="gov" size={12} />
          <a
            href={activeScheme.official_link}
            target="_blank"
            rel="noopener noreferrer"
            style={{ color: 'inherit', textDecoration: 'underline' }}
          >
            {activeScheme.scheme_id} {t('officialSourceLink', 'Official Portal')} ↗
          </a>
        </div>
      </div>
    </div>
  )
}
