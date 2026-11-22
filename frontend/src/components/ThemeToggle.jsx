import React, { useEffect, useState } from 'react'
import Icon from './Icon'

const THEME_COLORS = {
  dark: '#07040d',
  light: '#F8FAFC',
}

export default function ThemeToggle() {
  const [theme, setTheme] = useState('dark')

  const applyTheme = (targetTheme) => {
    setTheme(targetTheme)
    document.documentElement.setAttribute('data-theme', targetTheme)
    localStorage.setItem('civic_ai_theme', targetTheme)

    // Update <meta name="theme-color"> dynamically
    let metaTag = document.querySelector('meta[name="theme-color"]')
    if (!metaTag) {
      metaTag = document.createElement('meta')
      metaTag.name = 'theme-color'
      document.head.appendChild(metaTag)
    }
    metaTag.setAttribute('content', THEME_COLORS[targetTheme] || THEME_COLORS.dark)
  }

  useEffect(() => {
    // 1. Check localStorage first
    const savedTheme = localStorage.getItem('civic_ai_theme')
    if (savedTheme === 'light' || savedTheme === 'dark') {
      applyTheme(savedTheme)
    } else {
      // 2. Fall back to system preference
      const prefersLight = window.matchMedia && window.matchMedia('(prefers-color-scheme: light)').matches
      const initialTheme = prefersLight ? 'light' : 'dark'
      applyTheme(initialTheme)
    }
  }, [])

  const toggleTheme = () => {
    const nextTheme = theme === 'dark' ? 'light' : 'dark'
    applyTheme(nextTheme)
  }

  return (
    <button
      type="button"
      className="theme-toggle-btn"
      onClick={toggleTheme}
      aria-label={`Switch to ${theme === 'dark' ? 'light' : 'dark'} mode`}
      title={`Switch to ${theme === 'dark' ? 'light' : 'dark'} mode`}
    >
      <div className="theme-toggle-track">
        <span className={`theme-icon ${theme === 'dark' ? 'active' : ''}`} style={{ display: 'flex', alignItems: 'center' }}>
          <Icon name="moon" size={11} color="var(--accent-info)" />
        </span>
        <span className={`theme-icon ${theme === 'light' ? 'active' : ''}`} style={{ display: 'flex', alignItems: 'center' }}>
          <Icon name="sun" size={11} color="#f59e0b" />
        </span>
        <div className={`theme-toggle-thumb ${theme}`} />
      </div>
    </button>
  )
}
