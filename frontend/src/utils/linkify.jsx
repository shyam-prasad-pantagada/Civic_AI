import React from 'react'

/**
 * Utility to parse plain text strings and automatically render any HTTP/HTTPS URLs
 * or canonical Indian government domains (*.gov.in, *.nic.in) as clean, clickable
 * hyperlinks with target="_blank" and rel="noopener noreferrer".
 *
 * Correctly strips trailing punctuation (.,;:!?) so links remain valid.
 */
export function renderClickableContent(text) {
  if (!text || typeof text !== 'string') return text

  // Regex matching full URLs (http/https) or domain patterns like abc.gov.in / abc.nic.in
  const urlRegex = /(https?:\/\/[^\s,;()]+|[a-zA-Z0-9-]+\.(?:gov\.in|nic\.in)(?:\/[^\s,;()]*)?)/gi

  const parts = []
  let lastIndex = 0
  let match

  while ((match = urlRegex.exec(text)) !== null) {
    let matchedUrl = match[0]
    const startIndex = match.index

    // Check for trailing punctuation attached to matched URL
    let trailingPunctuation = ''
    const punctMatch = matchedUrl.match(/[.,;:!?)]+$/)
    if (punctMatch) {
      trailingPunctuation = punctMatch[0]
      matchedUrl = matchedUrl.slice(0, -trailingPunctuation.length)
    }

    // Append preceding plain text
    if (startIndex > lastIndex) {
      parts.push(text.substring(lastIndex, startIndex))
    }

    // Determine normalized href
    const href = matchedUrl.startsWith('http://') || matchedUrl.startsWith('https://')
      ? matchedUrl
      : `https://${matchedUrl}`

    parts.push(
      <a
        key={`link-${startIndex}`}
        href={href}
        target="_blank"
        rel="noopener noreferrer"
        className="inline-citation-link"
        title={`Visit official government portal: ${matchedUrl}`}
      >
        <span>{matchedUrl}</span>
        <span className="inline-link-arrow">↗</span>
      </a>
    )

    if (trailingPunctuation) {
      parts.push(trailingPunctuation)
    }

    lastIndex = startIndex + match[0].length
  }

  // Append remaining text
  if (lastIndex < text.length) {
    parts.push(text.substring(lastIndex))
  }

  return parts.length > 0 ? parts : text
}

