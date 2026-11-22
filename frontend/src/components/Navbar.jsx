import React, { useState } from 'react'
import { NavLink, Link } from 'react-router-dom'
import ThemeToggle from './ThemeToggle'
import LanguageSelector from './LanguageSelector'
import Icon from './Icon'
import { useLanguage } from '../i18n'

export default function Navbar() {
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false)
  const { t } = useLanguage()

  const closeMenu = () => setMobileMenuOpen(false)

  return (
    <nav className="nav">
      <div className="nav-inner">
        {/* Brand Logo & Name */}
        <Link to="/" className="nav-brand" onClick={closeMenu}>
          <div className="nav-logo-icon">
            <Icon name="building" size={18} color="var(--primary-start)" />
          </div>
          <div className="nav-brand-title">
            <span className="brand-main">Civic_AI</span>
            <span className="brand-badge">{t('brandTagline', 'Digital Governance • India')}</span>
          </div>
        </Link>

        {/* Desktop Navigation Links */}
        <div className="nav-links">
          <NavLink 
            to="/" 
            className={({ isActive }) => `nav-link ${isActive ? 'active' : ''}`}
            end
          >
            <span>{t('navOverview', 'Overview')}</span>
          </NavLink>
          <NavLink 
            to="/explain" 
            className={({ isActive }) => `nav-link ${isActive ? 'active' : ''}`}
          >
            <span>{t('navNoticeExplainer', 'Notice Explainer')}</span>
          </NavLink>
          <NavLink 
            to="/eligibility" 
            className={({ isActive }) => `nav-link ${isActive ? 'active' : ''}`}
          >
            <span>{t('navSchemeEligibility', 'Scheme Eligibility')}</span>
          </NavLink>
          <NavLink 
            to="/rights" 
            className={({ isActive }) => `nav-link ${isActive ? 'active' : ''}`}
          >
            <span>{t('navRightsAndLaws', 'Rights & Laws')}</span>
          </NavLink>
        </div>

        {/* Action Controls, Language & Theme Toggle */}
        <div className="nav-actions">
          <LanguageSelector />

          <div className="nav-region-tag" title="Covers Central Government, 28 States & 8 Union Territories">
            <span className="india-flag-dot"></span>
            <span>{t('statesAndUts', '28 States & 8 UTs')}</span>
          </div>

          <ThemeToggle />

          <Link to="/explain" className="btn-primary nav-cta-btn" style={{ padding: '0.5rem 1rem', fontSize: '0.85rem' }}>
            <span>{t('navScanNotice', 'Scan Notice')}</span>
            <Icon name="arrow-right" size={13} />
          </Link>

          {/* Mobile Hamburger Toggle */}
          <button 
            type="button" 
            className="nav-hamburger"
            onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
            aria-label="Toggle navigation menu"
          >
            {mobileMenuOpen ? <Icon name="close" size={16} /> : <span>☰</span>}
          </button>
        </div>
      </div>

      {/* Responsive Mobile Menu Dropdown */}
      {mobileMenuOpen && (
        <div className="nav-mobile-menu">
          <NavLink 
            to="/" 
            className={({ isActive }) => `mobile-nav-link ${isActive ? 'active' : ''}`}
            onClick={closeMenu}
            end
          >
            <Icon name="gov" size={16} />
            <span>{t('navOverview', 'Overview')}</span>
          </NavLink>
          <NavLink 
            to="/explain" 
            className={({ isActive }) => `mobile-nav-link ${isActive ? 'active' : ''}`}
            onClick={closeMenu}
          >
            <Icon name="document" size={16} />
            <span>{t('navNoticeExplainer', 'Notice Explainer')}</span>
          </NavLink>
          <NavLink 
            to="/eligibility" 
            className={({ isActive }) => `mobile-nav-link ${isActive ? 'active' : ''}`}
            onClick={closeMenu}
          >
            <Icon name="target" size={16} />
            <span>{t('navSchemeEligibility', 'Scheme Eligibility')}</span>
          </NavLink>
          <NavLink 
            to="/rights" 
            className={({ isActive }) => `mobile-nav-link ${isActive ? 'active' : ''}`}
            onClick={closeMenu}
          >
            <Icon name="scale" size={16} />
            <span>{t('navRightsAndLaws', 'Rights & Laws')}</span>
          </NavLink>

          <div className="mobile-nav-footer">
            <div className="nav-region-tag" style={{ width: '100%', justifyContent: 'center' }}>
              <span className="india-flag-dot"></span>
              <span>{t('statesAndUts', '28 States & 8 UTs')}</span>
            </div>
          </div>
        </div>
      )}
    </nav>
  )
}
