import React, { useState, useEffect, useRef } from 'react'
import Icon from './Icon'
import { useLanguage } from '../i18n'

export default function LanguageSelector() {
  const [isOpen, setIsOpen] = useState(false)
  const { lang, setLang, supportedLanguages, currentLanguage } = useLanguage()
  const dropdownRef = useRef(null)

  useEffect(() => {
    const handleClickOutside = (e) => {
      if (dropdownRef.current && !dropdownRef.current.contains(e.target)) {
        setIsOpen(false)
      }
    }
    document.addEventListener('mousedown', handleClickOutside)
    return () => document.removeEventListener('mousedown', handleClickOutside)
  }, [])

  return (
    <div className="lang-selector-wrapper" ref={dropdownRef} style={{ position: 'relative' }}>
      <button
        type="button"
        className="nav-region-tag"
        style={{
          cursor: 'pointer',
          background: 'var(--bg-surface-elevated)',
          display: 'inline-flex',
          alignItems: 'center',
          gap: '6px',
          padding: '0.4rem 0.75rem',
          border: '1px solid var(--border-card)',
          borderRadius: 'var(--radius-full)',
        }}
        onClick={() => setIsOpen(!isOpen)}
        title="Multilingual Indian Policy Engine (12 Official Languages Enabled)"
        aria-label="Select language"
      >
        <Icon name="globe" size={14} color="var(--accent-info)" />
        <span style={{ fontWeight: 700, fontSize: '0.82rem' }}>
          {lang.toUpperCase()}
        </span>
        <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>
          {currentLanguage ? currentLanguage.native : 'English'}
        </span>
        <Icon name="chevron-down" size={11} color="var(--text-muted)" />
      </button>

      {isOpen && (
        <div
          className="glass-card"
          style={{
            position: 'absolute',
            top: 'calc(100% + 8px)',
            right: 0,
            width: '280px',
            maxHeight: '380px',
            overflowY: 'auto',
            padding: '0.65rem',
            zIndex: 1100,
            boxShadow: '0 15px 35px -5px rgba(0, 0, 0, 0.4)',
            border: '1px solid var(--border-card)',
            background: 'var(--bg-card)',
            borderRadius: 'var(--radius-md)',
          }}
        >
          <div
            style={{
              fontSize: '0.72rem',
              textTransform: 'uppercase',
              letterSpacing: '0.08em',
              color: 'var(--text-muted)',
              padding: '0.35rem 0.65rem 0.5rem',
              fontWeight: 700,
              display: 'flex',
              justifyContent: 'space-between',
              alignItems: 'center',
            }}
          >
            <span>Select Language (12 Active)</span>
            <span style={{ fontSize: '0.65rem', color: 'var(--accent-verified)' }}>✓ Multilingual</span>
          </div>

          <div style={{ display: 'flex', flexDirection: 'column', gap: '0.25rem' }}>
            {supportedLanguages.map((item) => {
              const isSelected = lang === item.code

              return (
                <button
                  key={item.code}
                  type="button"
                  onClick={() => {
                    setLang(item.code)
                    setIsOpen(false)
                  }}
                  style={{
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'space-between',
                    padding: '0.5rem 0.75rem',
                    borderRadius: 'var(--radius-sm)',
                    border: 'none',
                    background: isSelected ? 'var(--primary-gradient)' : 'transparent',
                    color: isSelected ? '#ffffff' : 'var(--text-primary)',
                    cursor: 'pointer',
                    fontSize: '0.85rem',
                    textAlign: 'left',
                    width: '100%',
                    transition: 'all var(--transition-fast)',
                  }}
                >
                  <div style={{ display: 'flex', flexDirection: 'column' }}>
                    <span style={{ fontWeight: isSelected ? 700 : 600 }}>
                      {item.native}
                    </span>
                    <span
                      style={{
                        fontSize: '0.72rem',
                        color: isSelected ? 'rgba(255,255,255,0.85)' : 'var(--text-muted)',
                      }}
                    >
                      {item.name}
                    </span>
                  </div>

                  {isSelected && (
                    <Icon name="check" size={14} color="#ffffff" />
                  )}
                </button>
              )
            })}
          </div>
        </div>
      )}
    </div>
  )
}
