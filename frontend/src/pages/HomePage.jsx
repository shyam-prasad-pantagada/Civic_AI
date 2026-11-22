import React, { useState, useEffect } from 'react'
import { Link } from 'react-router-dom'
import Icon from '../components/Icon'
import SourceBadge from '../components/SourceBadge'
import { useLanguage } from '../i18n'

const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:8000'

export default function HomePage() {
  const { t } = useLanguage()
  const [stats, setStats] = useState({
    total_schemes: 4859,
    central_schemes_count: 745,
    states_covered_count: 36,
    states_count: 28,
    uts_count: 8,
    rights_topics_count: 7,
    last_synced: '22 Nov 2026',
    deterministic_engine: true,
  })

  useEffect(() => {
    fetch(`${API_BASE}/api/stats`)
      .then((res) => (res.ok ? res.json() : null))
      .then((data) => {
        if (data) setStats(data)
      })
      .catch((err) => console.log('Stats fetch fallback to local defaults:', err))
  }, [])

  return (
    <div>
      {/* Hero Section */}
      <section className="hero-section">
        <div className="hero-pill-badge">
          <Icon name="gov" size={13} style={{ marginRight: '4px' }} />
          <span>{t('heroBadge', 'Digital Public Governance & Citizen Intelligence')}</span>
        </div>

        <h1 className="hero-title">
          <span className="gradient-text">{t('brandTitle', 'Civic_AI')}</span>
        </h1>

        <p className="hero-tagline">
          {t('heroTagline', 'Your guide to government schemes, rights & policies across India.')}
        </p>

        <p className="hero-subtext">
          {t('heroSubtext', 'Demystifying complex official circulars, computing deterministic welfare eligibility across 36 States & Union Territories (28 States + 8 UTs), and citing verified official sources in plain, accessible language.')}
        </p>

        <div className="hero-cta-group">
          <Link to="/explain" className="btn-primary" style={{ display: 'inline-flex', alignItems: 'center', gap: '6px' }}>
            <Icon name="document" size={15} />
            <span>{t('heroExplainBtn', 'Explain a Notice or Circular')}</span>
            <Icon name="arrow-right" size={13} />
          </Link>
          <Link to="/eligibility" className="btn-secondary" style={{ display: 'inline-flex', alignItems: 'center', gap: '6px' }}>
            <Icon name="target" size={15} />
            <span>{t('heroEligibilityBtn', 'Check Scheme Eligibility')}</span>
          </Link>
          <Link to="/rights" className="btn-secondary" style={{ display: 'inline-flex', alignItems: 'center', gap: '6px' }}>
            <Icon name="scale" size={15} />
            <span>{t('heroRightsBtn', 'Explore Your Rights')}</span>
          </Link>
        </div>
      </section>

      {/* Factual Live-Computed Stats Banner */}
      <section className="stats-grid">
        <div className="stat-card">
          <div className="stat-number">{stats.states_covered_count || 36}</div>
          <div className="stat-label">{t('statStatesCovered', 'States & UTs Covered')}</div>
          <div className="stat-desc">{t('statStatesDesc', `${stats.states_count || 28} States + ${stats.uts_count || 8} Union Territories`)}</div>
        </div>

        <div className="stat-card">
          <div className="stat-number">{stats.total_schemes ? stats.total_schemes.toLocaleString() : '4,859'}</div>
          <div className="stat-label">{t('statSchemesIndexed', 'Verified Schemes Indexed')}</div>
          <div className="stat-desc">{t('statSchemesDesc', 'Central + 28 States & 8 UTs')}</div>
        </div>

        <div className="stat-card">
          <div className="stat-number">{stats.rights_topics_count || 7}</div>
          <div className="stat-label">{t('statRightsTopics', 'Statutory Rights Topics')}</div>
          <div className="stat-desc">{t('statRightsDesc', 'India Code Acts & sections verified')}</div>
        </div>

        <div className="stat-card">
          <div className="stat-number">100%</div>
          <div className="stat-label">{t('statDeterministic', 'Deterministic Python Logic')}</div>
          <div className="stat-desc">{t('statDeterministicDesc', 'Zero LLM guessing on eligibility decisions')}</div>
        </div>
      </section>

      {/* Core Feature Cards */}
      <section style={{ margin: '4rem 0 2rem' }}>
        <div style={{ textAlign: 'center', marginBottom: '2.5rem' }}>
          <span className="badge badge-pill" style={{ marginBottom: '0.75rem' }}>{t('coreCapabilities', 'Core Capabilities')}</span>
          <h2 style={{ fontFamily: 'var(--font-family-heading)', fontSize: '2.2rem', fontWeight: 800 }}>
            {t('governanceMadeSimple', 'Governance Made Simple for Every Citizen')}
          </h2>
          <p style={{ color: 'var(--text-secondary)', maxWidth: '600px', margin: '0.5rem auto 0', fontSize: '0.98rem' }}>
            {t('fourPillars', 'Four pillars designed to remove the legal jargon barrier and connect citizens to their rightful benefits.')}
          </p>
        </div>

        <div className="features-grid">
          {/* Card 1 */}
          <Link to="/explain" className="card feature-card">
            <div>
              <div className="feature-header">
                <div className="feature-icon-box">
                  <Icon name="document" size={22} color="var(--primary-start)" />
                </div>
                <span className="badge badge-verified">{t('liveWebVerified', 'Live Web Verified')}</span>
              </div>
              <h3 className="feature-title">{t('feature1Title', 'Notice & Document Explainer')}</h3>
              <p className="feature-desc">
                {t('feature1Desc', 'Upload complex government circulars, gazettes, tax demands, or court notices (PDF/image). Get concise plain-language summaries, affected citizen categories, hard deadlines, and step-by-step required actions.')}
              </p>
            </div>
            <div className="feature-footer-action">
              <span>{t('feature1Action', 'Upload document to explain')}</span>
              <Icon name="arrow-right" size={13} />
            </div>
          </Link>

          {/* Card 2 */}
          <Link to="/eligibility" className="card feature-card">
            <div>
              <div className="feature-header">
                <div className="feature-icon-box">
                  <Icon name="target" size={22} color="var(--primary-start)" />
                </div>
                <span className="badge badge-verified">{t('statDeterministic', 'Deterministic Engine')}</span>
              </div>
              <h3 className="feature-title">{t('feature2Title', 'Scheme Eligibility Checker')}</h3>
              <p className="feature-desc">
                {t('feature2Desc', 'Input demographic parameters (age, state, income, occupation) to calculate exactly which welfare schemes you qualify for. Evaluated by a 100% deterministic rules engine.')}
              </p>
            </div>
            <div className="feature-footer-action">
              <span>{t('feature2Action', 'Check your scheme eligibility')}</span>
              <Icon name="arrow-right" size={13} />
            </div>
          </Link>

          {/* Card 3 */}
          <Link to="/rights" className="card feature-card">
            <div>
              <div className="feature-header">
                <div className="feature-icon-box">
                  <Icon name="scale" size={22} color="var(--primary-start)" />
                </div>
                <span className="badge badge-verified">{t('statRightsDesc', 'Statutory Citations')}</span>
              </div>
              <h3 className="feature-title">{t('feature3Title', 'Rights & Law Explorer')}</h3>
              <p className="feature-desc">
                {t('feature3Desc', 'Ask real-life legal questions in plain terms (tenancy disputes, consumer rights, RTI procedures, worker protections). Every single answer is grounded with mandatory citations to official Acts and sections from India Code.')}
              </p>
            </div>
            <div className="feature-footer-action">
              <span>{t('feature3Action', 'Ask a legal rights question')}</span>
              <Icon name="arrow-right" size={13} />
            </div>
          </Link>

          {/* Card 4 */}
          <div className="card feature-card" id="verification">
            <div>
              <div className="feature-header">
                <div className="feature-icon-box">
                  <Icon name="search" size={22} color="var(--primary-start)" />
                </div>
                <span className="badge badge-verified">
                  <span className="pulse-dot"></span>
                  {t('strictDomain', 'Official Whitelist')}
                </span>
              </div>
              <h3 className="feature-title">{t('feature4Title', 'Live Source Verification')}</h3>
              <p className="feature-desc">
                {t('feature4Desc', 'Never rely on stale circulars or outdated deadlines. Real-time verification runs against official government domain allow-lists and timestamps every fact with a freshness status badge.')}
              </p>
              <div style={{ marginTop: '1rem' }}>
                <SourceBadge 
                  status="verified" 
                  sourceName="myScheme.gov.in" 
                  sourceUrl="https://www.myscheme.gov.in" 
                  lastVerified={t('liveWebVerified', 'Verified today')} 
                />
              </div>
            </div>
            <div className="feature-footer-action" style={{ color: 'var(--accent-verified)' }}>
              <span>{t('strictDomain', 'Strict domain allow-list')}</span>
              <Icon name="check" size={13} />
            </div>
          </div>
        </div>
      </section>

      {/* Trust Framework */}
      <section style={{ margin: '4rem 0' }}>
        <div className="glass-card" style={{ padding: '2.5rem' }}>
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '2rem', flexWrap: 'wrap', gap: '1rem' }}>
            <div>
              <span className="badge badge-pill" style={{ marginBottom: '0.5rem' }}>{t('architectureStandard', 'Architecture Standard')}</span>
              <h3 style={{ fontFamily: 'var(--font-family-heading)', fontSize: '1.6rem', fontWeight: 700 }}>
                {t('trustFramework', 'The Civic Trust Framework')}
              </h3>
            </div>
            <div style={{ display: 'flex', gap: '0.5rem' }}>
              <span className="badge badge-verified">{t('zeroHallucinated', 'Zero Hallucinated Rules')}</span>
              <span className="badge badge-pill">{t('grade6Readability', 'Grade 6 Readability')}</span>
            </div>
          </div>

          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(240px, 1fr))', gap: '1.5rem' }}>
            <div style={{ padding: '1.25rem', background: 'var(--bg-surface-elevated)', borderRadius: 'var(--radius-md)', border: '1px solid var(--border-subtle)' }}>
              <div style={{ fontSize: '1.1rem', fontWeight: 700, marginBottom: '0.75rem', display: 'flex', alignItems: 'center', gap: '6px' }}>
                <span className="badge badge-verified" style={{ width: '22px', height: '22px', borderRadius: '50%', padding: 0, display: 'inline-flex', alignItems: 'center', justifyContent: 'center' }}>1</span>
                <span>{t('trust1Title', 'State Isolation')}</span>
              </div>
              <div style={{ fontWeight: 600, marginBottom: '0.35rem' }}>{t('trust1Sub', '36 Unique Registries')}</div>
              <div style={{ fontSize: '0.85rem', color: 'var(--text-secondary)', lineHeight: 1.5 }}>
                {t('trust1Desc', "India's states have distinct welfare criteria. We never blend state datasets into generic answers.")}
              </div>
            </div>

            <div style={{ padding: '1.25rem', background: 'var(--bg-surface-elevated)', borderRadius: 'var(--radius-md)', border: '1px solid var(--border-subtle)' }}>
              <div style={{ fontSize: '1.1rem', fontWeight: 700, marginBottom: '0.75rem', display: 'flex', alignItems: 'center', gap: '6px' }}>
                <span className="badge badge-verified" style={{ width: '22px', height: '22px', borderRadius: '50%', padding: 0, display: 'inline-flex', alignItems: 'center', justifyContent: 'center' }}>2</span>
                <span>{t('trust2Title', 'Deterministic Logic')}</span>
              </div>
              <div style={{ fontWeight: 600, marginBottom: '0.35rem' }}>{t('trust2Sub', 'Python Engine, Not LLM')}</div>
              <div style={{ fontSize: '0.85rem', color: 'var(--text-secondary)', lineHeight: 1.5 }}>
                {t('trust2Desc', 'Eligibility is calculated mathematically via explicit rules. The assistant only translates outcomes into accessible prose.')}
              </div>
            </div>

            <div style={{ padding: '1.25rem', background: 'var(--bg-surface-elevated)', borderRadius: 'var(--radius-md)', border: '1px solid var(--border-subtle)' }}>
              <div style={{ fontSize: '1.1rem', fontWeight: 700, marginBottom: '0.75rem', display: 'flex', alignItems: 'center', gap: '6px' }}>
                <span className="badge badge-verified" style={{ width: '22px', height: '22px', borderRadius: '50%', padding: 0, display: 'inline-flex', alignItems: 'center', justifyContent: 'center' }}>3</span>
                <span>{t('trust3Title', 'Mandatory Citations')}</span>
              </div>
              <div style={{ fontWeight: 600, marginBottom: '0.35rem' }}>{t('trust3Sub', 'Official Acts & Sections')}</div>
              <div style={{ fontSize: '0.85rem', color: 'var(--text-secondary)', lineHeight: 1.5 }}>
                {t('trust3Desc', 'Every factual claim carries an official URL and timestamp. If no official source exists, we report it explicitly.')}
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Persistent Disclaimer */}
      <div className="disclaimer">
        <div className="disclaimer-icon">
          <Icon name="scale" size={22} color="var(--primary-start)" />
        </div>
        <div className="disclaimer-text">
          <strong>{t('disclaimerTitle', 'Civic Platform Disclaimer:')}</strong> {t('disclaimerText', 'This platform provides public information only, not legal advice. Laws, government schemes, and circulars vary across states and change frequently. Always verify with official government sources or licensed legal counsel.')}
        </div>
      </div>
    </div>
  )
}
