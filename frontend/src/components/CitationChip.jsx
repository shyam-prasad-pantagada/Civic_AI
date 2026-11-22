import React from 'react'

/**
 * CitationChip component for rendering clean, clickable, verified source links
 * with target="_blank" and rel="noopener noreferrer".
 *
 * @param {string} url - Official source URL
 * @param {string} label - Display label (e.g., Act name, portal name)
 * @param {string} type - 'act' | 'scheme' | 'gazette' | 'portal'
 * @param {string} section - Optional section reference (e.g. "Section 21")
 */
export default function CitationChip({ url, label, type = 'portal', section }) {
  if (!url) return null

  // Ensure absolute URL
  const href = url.startsWith('http://') || url.startsWith('https://') 
    ? url 
    : `https://${url}`

  let displayHost = ''
  try {
    displayHost = new URL(href).hostname.replace(/^www\./, '')
  } catch (e) {
    displayHost = label || 'Official Source'
  }

  const iconMap = {
    act: '📜',
    scheme: '🏛️',
    gazette: '📰',
    portal: '🔗',
    helpline: '📞',
  }
  const icon = iconMap[type] || '🔗'

  return (
    <a
      href={href}
      target="_blank"
      rel="noopener noreferrer"
      className="citation-chip"
      title={`Open official verified source on ${displayHost} in a new tab`}
    >
      <span className="citation-chip-icon">{icon}</span>
      <span className="citation-chip-content">
        <span className="citation-chip-label">{label || displayHost}</span>
        {section && <span className="citation-chip-section">({section})</span>}
      </span>
      <span className="citation-chip-arrow">↗</span>
    </a>
  )
}
