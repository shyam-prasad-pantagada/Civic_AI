import React from 'react'
import Icon from './Icon'
import { useLanguage } from '../i18n'

/**
 * SourceBadge Component
 * Shows honest live verification status of documents, circulars, and scheme facts.
 * 
 * @param {'verified' | 'outdated' | 'unverified' | 'could_not_verify' | 'not_verified'} status
 * @param {string} sourceName - e.g. "myScheme.gov.in" or "India Code"
 * @param {string} sourceUrl - Official URL
 * @param {string} lastVerified - Timestamp e.g. "Verified today"
 */
export default function SourceBadge({
  status = 'not_verified',
  sourceName = null,
  sourceUrl = '#',
  lastVerified = null,
}) {
  const { t } = useLanguage()
  const displaySourceName = sourceName || t('officialSource', 'Official Government Source')

  if (status === 'verified') {
    return (
      <div className="source-badge status-verified" title={t('verifiedToday', 'Verified against live official source')}>
        <span className="pulse-dot"></span>
        <span style={{ fontWeight: 600 }}>{lastVerified || t('verifiedToday', 'Verified today')}</span>
        {displaySourceName && (
          <>
            <span style={{ opacity: 0.4 }}>•</span>
            {sourceUrl && sourceUrl !== '#' ? (
              <a href={sourceUrl} target="_blank" rel="noopener noreferrer">
                {displaySourceName} ↗
              </a>
            ) : (
              <span>{displaySourceName}</span>
            )}
          </>
        )}
      </div>
    )
  }

  if (status === 'outdated') {
    return (
      <div className="source-badge status-outdated" title={t('outdatedSource', 'A newer circular or amendment exists')}>
        <Icon name="warning" size={13} style={{ color: 'var(--accent-warning)', marginRight: '3px' }} />
        <span style={{ fontWeight: 600 }}>{t('outdatedSource', 'Possibly outdated: newer circular found')}</span>
        {sourceUrl && sourceUrl !== '#' && (
          <>
            <span style={{ opacity: 0.4 }}>•</span>
            <a href={sourceUrl} target="_blank" rel="noopener noreferrer">
              {displaySourceName} ↗
            </a>
          </>
        )}
      </div>
    )
  }

  if (status === 'unverified' || status === 'could_not_verify') {
    return (
      <div className="source-badge status-unverified" title={t('couldNotVerifySource', 'Could not locate official government circular')}>
        <Icon name="close" size={13} style={{ color: 'var(--accent-error)', marginRight: '3px' }} />
        <span style={{ fontWeight: 600 }}>{t('couldNotVerifySource', 'Could not verify official source')}</span>
      </div>
    )
  }

  // Default state: Not yet verified (prior to running a live /api/verify check)
  return (
    <div className="source-badge status-pending" title={t('notYetVerified', 'Live verification has not been performed yet')}>
      <Icon name="refresh" size={12} style={{ opacity: 0.7, marginRight: '3px' }} />
      <span style={{ fontWeight: 500 }}>{t('notYetVerified', 'Not yet verified')}</span>
    </div>
  )
}
