import React from 'react'
import { Link } from 'react-router-dom'
import Icon from './Icon'
import { useLanguage } from '../i18n'

export default function Footer() {
  const { t } = useLanguage()

  return (
    <footer className="footer">
      <div className="footer-inner">
        {/* Main Footer Content Grid */}
        <div className="footer-top">
          {/* Brand Info Column */}
          <div className="footer-brand">
            <Link to="/" className="footer-brand-title">
              <span className="footer-brand-icon">
                <Icon name="building" size={20} color="var(--primary-start)" />
              </span>
              <span className="brand-main">{t('brandTitle', 'Civic AI')}</span>
            </Link>
            <p className="footer-desc">
              {t('footerDesc', 'Digital Public Governance portal empowering Indian citizens with plain-language explanations of government notices, 100% deterministic welfare scheme eligibility, and verified statutory rights across all 28 States & 8 Union Territories.')}
            </p>
            <div className="footer-badges">
              <span className="badge badge-verified">
                <Icon name="check" size={13} style={{ marginRight: '4px' }} />
                {t('indexedBadge', '28 States & 8 UTs Indexed')}
              </span>
              <span className="badge badge-pill">
                {t('zeroBiasBadge', 'Zero Decision Bias')}
              </span>
            </div>
          </div>

          {/* Links Columns Group */}
          <div className="footer-links-group">
            {/* Column 1: Core Modules */}
            <div className="footer-col">
              <h4 className="footer-col-title">{t('coreModules', 'Core Modules')}</h4>
              <Link to="/explain" className="footer-link">
                <Icon name="document" size={14} color="var(--text-muted)" />
                <span>{t('navNoticeExplainer', 'Notice Explainer')}</span>
              </Link>
              <Link to="/eligibility" className="footer-link">
                <Icon name="search" size={14} color="var(--text-muted)" />
                <span>{t('browseSchemesTab', 'Scheme Directory')}</span>
              </Link>
              <Link to="/eligibility" className="footer-link">
                <Icon name="target" size={14} color="var(--text-muted)" />
                <span>{t('calculatorTab', 'Eligibility Checker')}</span>
              </Link>
              <Link to="/rights" className="footer-link">
                <Icon name="scale" size={14} color="var(--text-muted)" />
                <span>{t('navRightsAndLaws', 'Rights & Local Laws')}</span>
              </Link>
            </div>

            {/* Column 2: Official Sources */}
            <div className="footer-col">
              <h4 className="footer-col-title">{t('officialSources', 'Official Sources')}</h4>
              <a 
                href="https://www.indiacode.nic.in" 
                target="_blank" 
                rel="noopener noreferrer" 
                className="footer-link"
              >
                <Icon name="gov" size={14} color="var(--text-muted)" />
                <span>India Code (Acts)</span>
                <Icon name="external" size={11} color="var(--text-muted)" />
              </a>
              <a 
                href="https://www.myscheme.gov.in" 
                target="_blank" 
                rel="noopener noreferrer" 
                className="footer-link"
              >
                <Icon name="target" size={14} color="var(--text-muted)" />
                <span>myScheme National Portal</span>
                <Icon name="external" size={11} color="var(--text-muted)" />
              </a>
              <a 
                href="https://egazette.gov.in" 
                target="_blank" 
                rel="noopener noreferrer" 
                className="footer-link"
              >
                <Icon name="document" size={14} color="var(--text-muted)" />
                <span>The Gazette of India</span>
                <Icon name="external" size={11} color="var(--text-muted)" />
              </a>
              <a 
                href="https://nalsa.gov.in" 
                target="_blank" 
                rel="noopener noreferrer" 
                className="footer-link"
              >
                <Icon name="scale" size={14} color="var(--text-muted)" />
                <span>NALSA Legal Aid (15100)</span>
                <Icon name="external" size={11} color="var(--text-muted)" />
              </a>
              <a 
                href="https://data.gov.in" 
                target="_blank" 
                rel="noopener noreferrer" 
                className="footer-link"
              >
                <Icon name="external" size={14} color="var(--text-muted)" />
                <span>Open Government Data</span>
                <Icon name="external" size={11} color="var(--text-muted)" />
              </a>
            </div>

            {/* Column 3: Platform Architecture */}
            <div className="footer-col">
              <h4 className="footer-col-title">{t('civicArchitecture', 'Civic Architecture')}</h4>
              <div className="footer-spec-item">
                <span className="spec-label">Engine:</span>
                <span className="spec-val">{t('statDeterministic', '100% Deterministic Python')}</span>
              </div>
              <div className="footer-spec-item">
                <span className="spec-label">Language:</span>
                <span className="spec-val">{t('grade6Readability', 'Grade 6 Plain Language')}</span>
              </div>
              <div className="footer-spec-item">
                <span className="spec-label">Jurisdiction:</span>
                <span className="spec-val">{t('statesAndUts', 'Central + 28 States & 8 UTs')}</span>
              </div>
              <div className="footer-spec-item">
                <span className="spec-label">Sources:</span>
                <span className="spec-val">{t('strictDomain', 'Strictly *.gov.in / *.nic.in')}</span>
              </div>
            </div>
          </div>
        </div>

        {/* Legal Disclaimer Box */}
        <div className="disclaimer">
          <div className="disclaimer-icon">
            <Icon name="scale" size={22} color="var(--primary-start)" />
          </div>
          <div className="disclaimer-text">
            <strong>{t('statutoryDisclaimer', 'Statutory Legal Disclaimer:')}</strong> {t('statutoryDisclaimerText', 'Civic AI is an educational digital public infrastructure project providing public scheme intelligence and statutory rights explanations based on official publications. It does not provide formal legal representation or substitute for licensed legal counsel. For free government legal assistance, contact the National Legal Services Authority (NALSA) toll-free helpline at 15100.')}
          </div>
        </div>

        {/* Footer Bottom Bar */}
        <div className="footer-bottom">
          <div className="footer-bottom-left">
            <span>© {new Date().getFullYear()} <strong>{t('brandTitle', 'Civic AI')}</strong> • {t('copyrightText', 'Digital Public Governance & Citizen Intelligence')}</span>
          </div>
          <div className="footer-bottom-right">
            <span className="system-status-indicator">
              <span className="status-dot"></span>
              {t('allStatesActive', 'All 28 States, 8 UTs & Central Engine Active')}
            </span>
            <span className="version-pill">v0.1.0 Beta</span>
          </div>
        </div>
      </div>
    </footer>
  )
}
