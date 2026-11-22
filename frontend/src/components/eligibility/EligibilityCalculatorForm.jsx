import React from 'react'
import Icon from '../Icon'
import { useLanguage } from '../../i18n'

export default function EligibilityCalculatorForm({
  profile,
  onProfileChange,
  onSubmit,
  loading,
  allStates,
  categories,
  targetedScheme = null,
  onClearTargetedScheme,
}) {
  const { t } = useLanguage()

  return (
    <div className="glass-card" style={{ marginBottom: '2.5rem' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1.25rem', borderBottom: '1px solid var(--border-subtle)', paddingBottom: '0.85rem', flexWrap: 'wrap', gap: '0.75rem' }}>
        <div>
          <span style={{ fontSize: '0.82rem', textTransform: 'uppercase', letterSpacing: '0.08em', color: 'var(--accent-info)', fontWeight: 700 }}>
            {t('calcHeader', 'Deterministic Eligibility Calculator')}
          </span>
          <h2 style={{ fontSize: '1.35rem', fontWeight: 800, color: 'var(--text-primary)', marginTop: '0.2rem' }}>
            {t('calcSubheader', 'Check Which Government Schemes You Qualify For')}
          </h2>
        </div>

        <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
          <span className="badge badge-verified" style={{ fontSize: '0.74rem' }}>
            <Icon name="check" size={11} style={{ marginRight: '3px' }} />
            {t('zeroBias', 'Zero AI Decision Bias')}
          </span>
        </div>
      </div>

      {targetedScheme && (
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', padding: '0.75rem 1rem', background: 'var(--accent-info-bg)', borderRadius: 'var(--radius-sm)', border: '1px solid var(--accent-info)', marginBottom: '1.25rem' }}>
          <div style={{ fontSize: '0.85rem', color: 'var(--text-primary)' }}>
            {t('evaluatingFor', 'Evaluating your specific eligibility for:')} <strong>{targetedScheme.scheme_name}</strong>
          </div>
          <button
            type="button"
            onClick={onClearTargetedScheme}
            style={{ background: 'none', border: 'none', color: 'var(--text-muted)', cursor: 'pointer', fontSize: '0.82rem' }}
          >
            {t('clearTarget', 'Clear Target ✕')}
          </button>
        </div>
      )}

      <form onSubmit={onSubmit}>
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(220px, 1fr))', gap: '1.1rem', marginBottom: '1.5rem' }}>
          {/* State / UT */}
          <div>
            <label style={{ display: 'block', fontSize: '0.82rem', fontWeight: 600, color: 'var(--text-secondary)', marginBottom: '0.35rem' }}>
              {t('stateResidence', 'State of Residence')} *
            </label>
            <select
              className="select"
              value={profile.state}
              onChange={(e) => onProfileChange('state', e.target.value)}
            >
              <option value="Central">{t('state_Central', 'Central Government (Nationwide)')}</option>
              <optgroup label={t('statesGroup', '28 States')}>
                {allStates.filter((s) => s.group === 'state' || (!['ALL', 'Central'].includes(s.code) && !['AN', 'CH', 'DN', 'DL', 'JK', 'LA', 'LD', 'PY'].includes(s.code))).map((s) => (
                  <option key={s.code} value={s.code}>
                    {t('state_' + s.code, s.name)}
                  </option>
                ))}
              </optgroup>
              <optgroup label={t('utsGroup', '8 Union Territories')}>
                {allStates.filter((s) => s.group === 'ut' || ['AN', 'CH', 'DN', 'DL', 'JK', 'LA', 'LD', 'PY'].includes(s.code)).map((s) => (
                  <option key={s.code} value={s.code}>
                    {t('state_' + s.code, s.name)}
                  </option>
                ))}
              </optgroup>
            </select>
          </div>

          {/* Age */}
          <div>
            <label style={{ display: 'block', fontSize: '0.82rem', fontWeight: 600, color: 'var(--text-secondary)', marginBottom: '0.35rem' }}>
              {t('applicantAge', 'Applicant Age (Years)')} *
            </label>
            <input
              type="number"
              className="input"
              min="0"
              max="120"
              placeholder="e.g. 35"
              value={profile.age}
              onChange={(e) => onProfileChange('age', e.target.value)}
              required
            />
          </div>

          {/* Gender */}
          <div>
            <label style={{ display: 'block', fontSize: '0.82rem', fontWeight: 600, color: 'var(--text-secondary)', marginBottom: '0.35rem' }}>
              {t('gender', 'Gender')}
            </label>
            <select
              className="select"
              value={profile.gender}
              onChange={(e) => onProfileChange('gender', e.target.value)}
            >
              <option value="female">{t('female', 'Female')}</option>
              <option value="male">{t('male', 'Male')}</option>
              <option value="transgender">{t('transgender', 'Transgender')}</option>
              <option value="other">{t('other', 'Other / Any')}</option>
            </select>
          </div>

          {/* Annual Family Income */}
          <div>
            <label style={{ display: 'block', fontSize: '0.82rem', fontWeight: 600, color: 'var(--text-secondary)', marginBottom: '0.35rem' }}>
              {t('annualIncome', 'Annual Family Income (₹)')}
            </label>
            <input
              type="number"
              className="input"
              min="0"
              step="5000"
              placeholder="e.g. 150000"
              value={profile.annual_income}
              onChange={(e) => onProfileChange('annual_income', e.target.value)}
            />
          </div>

          {/* Category */}
          <div>
            <label style={{ display: 'block', fontSize: '0.82rem', fontWeight: 600, color: 'var(--text-secondary)', marginBottom: '0.35rem' }}>
              {t('occupation', 'Occupation / Category')}
            </label>
            <select
              className="select"
              value={profile.category}
              onChange={(e) => onProfileChange('category', e.target.value)}
            >
              {categories.map((c) => (
                <option key={c.id} value={c.id}>
                  {c.transKey ? t(c.transKey, c.label) : c.label}
                </option>
              ))}
            </select>
          </div>

          {/* Land Holding */}
          <div>
            <label style={{ display: 'block', fontSize: '0.82rem', fontWeight: 600, color: 'var(--text-secondary)', marginBottom: '0.35rem' }}>
              {t('agriLand', 'Agricultural Land (Acres)')}
            </label>
            <input
              type="number"
              className="input"
              min="0"
              step="0.5"
              placeholder="e.g. 2.5 (leave blank if 0)"
              value={profile.land_holding_acres}
              onChange={(e) => onProfileChange('land_holding_acres', e.target.value)}
            />
          </div>

          {/* Disability % */}
          <div>
            <label style={{ display: 'block', fontSize: '0.82rem', fontWeight: 600, color: 'var(--text-secondary)', marginBottom: '0.35rem' }}>
              {t('disabilityPercent', 'Disability Percentage (if applicable)')}
            </label>
            <input
              type="number"
              className="input"
              min="0"
              max="100"
              placeholder="e.g. 40 (leave blank if none)"
              value={profile.disability_percentage}
              onChange={(e) => onProfileChange('disability_percentage', e.target.value)}
            />
          </div>
        </div>

        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', paddingTop: '1rem', borderTop: '1px solid var(--border-subtle)', flexWrap: 'wrap', gap: '1rem' }}>
          <div style={{ fontSize: '0.78rem', color: 'var(--text-muted)' }}>
            {t('calcDisclaimer', '* Evaluated strictly in pure Python without LLM guessing (SPEC.md Section 3.2).')}
          </div>

          <button
            type="submit"
            className="btn-primary"
            disabled={loading}
            style={{ padding: '0.65rem 1.4rem' }}
          >
            <span>{loading ? t('evaluatingRules', 'Evaluating Rules...') : t('calcMyEligibility', 'Calculate My Eligibility')}</span>
            <Icon name="arrow-right" size={13} />
          </button>
        </div>
      </form>
    </div>
  )
}
