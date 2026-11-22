import React, { useState } from 'react'
import Icon from '../Icon'
import { useLanguage } from '../../i18n'

export default function SchemeFilters({
  searchQuery,
  setSearchQuery,
  jurisdictionFilter,
  setJurisdictionFilter,
  schemeTypeFilter = 'all',
  setSchemeTypeFilter,
  selectedStateFilter,
  setSelectedStateFilter,
  selectedCategoryFilter,
  setSelectedCategoryFilter,
  selectedBenefitType,
  setSelectedBenefitType,
  allStates,
  categories,
  benefitTypes,
  onLiveSearch,
  isLiveSearching,
  schemesCountByState = {},
  totalFilteredCount = 0,
  lastSyncedDate = '22 Nov 2026',
}) {
  const [mobileFiltersOpen, setMobileFiltersOpen] = useState(false)
  const { t } = useLanguage()

  return (
    <div className="glass-card scheme-filters-container" style={{ marginBottom: '2rem' }}>
      {/* Search Bar */}
      <div style={{ display: 'flex', gap: '0.65rem', alignItems: 'center', marginBottom: '1.25rem', flexWrap: 'wrap' }}>
        <div style={{ position: 'relative', flex: 1, minWidth: '240px' }}>
          <span style={{ position: 'absolute', left: '0.85rem', top: '50%', transform: 'translateY(-50%)', color: 'var(--text-muted)' }}>
            <Icon name="search" size={16} />
          </span>
          <input
            type="text"
            className="input"
            style={{ paddingLeft: '2.4rem' }}
            placeholder={t('searchPlaceholder', 'Search verified welfare schemes by keyword, ministry, benefits, or acronym...')}
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            onKeyDown={(e) => e.key === 'Enter' && onLiveSearch(searchQuery)}
          />
        </div>

        <button
          type="button"
          className="btn-primary"
          onClick={() => onLiveSearch(searchQuery)}
          disabled={isLiveSearching || !searchQuery.trim()}
          title="Search live government portals if not indexed locally"
        >
          <span>{isLiveSearching ? t('searching', 'Searching...') : t('liveSearch', 'AI Live Search')}</span>
          <Icon name="refresh" size={13} />
        </button>

        {/* Mobile Filter Toggle */}
        <button
          type="button"
          className="btn-secondary mobile-filter-toggle"
          onClick={() => setMobileFiltersOpen(!mobileFiltersOpen)}
          style={{ display: 'none' }}
        >
          <Icon name="filter" size={14} />
          <span>{t('filters', 'Filters')}</span>
        </button>
      </div>

      {/* Cascading Filter Controls */}
      <div className={`scheme-filter-grid ${mobileFiltersOpen ? 'mobile-filters-active' : ''}`}>
        {/* Governance Scope & State Row */}
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: '1rem', marginBottom: '1rem' }}>
          {/* Four-Tier Governance Classification Pills */}
          <div style={{ display: 'flex', gap: '0.4rem', background: 'var(--bg-surface-elevated)', padding: '0.3rem', borderRadius: 'var(--radius-full)', border: '1px solid var(--border-card)', flexWrap: 'wrap' }}>
            {[
              { id: 'all', labelKey: 'allJurisdictions', defaultLabel: 'All Schemes' },
              { id: 'central', labelKey: 'centralGovt', defaultLabel: 'Central' },
              { id: 'state', labelKey: 'stateUtSchemes', defaultLabel: 'State / UT' },
              { id: 'integrated', labelKey: 'integratedScheme', defaultLabel: 'Integrated' },
              { id: 'multi_state', labelKey: 'multiStateScheme', defaultLabel: 'Multi-State' },
            ].map((j) => (
              <button
                key={j.id}
                type="button"
                className={`btn-secondary ${schemeTypeFilter === j.id ? 'btn-primary' : ''}`}
                style={{
                  padding: '0.35rem 0.85rem',
                  fontSize: '0.8rem',
                  borderRadius: 'var(--radius-full)',
                  border: 'none',
                }}
                onClick={() => {
                  if (setSchemeTypeFilter) setSchemeTypeFilter(j.id)
                  if (j.id === 'all' || j.id === 'central' || j.id === 'state') {
                    setJurisdictionFilter(j.id)
                  }
                }}
              >
                {t(j.labelKey, j.defaultLabel)}
              </button>
            ))}
          </div>

          {/* State / UT Selector with Exact Live Accurate Count Badge */}
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.6rem', flexWrap: 'wrap' }}>
            <span style={{ fontSize: '0.82rem', color: 'var(--text-muted)', fontWeight: 600 }}>
              {t('stateUtLabel', 'State / UT:')}
            </span>
            <select
              className="select"
              style={{ width: 'auto', minWidth: '220px', padding: '0.35rem 1.8rem 0.35rem 0.75rem', fontSize: '0.82rem' }}
              value={selectedStateFilter}
              onChange={(e) => setSelectedStateFilter(e.target.value)}
            >
              <option value="ALL">{t('state_ALL', 'All India (28 States & 8 UTs)')}</option>
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

            {/* Live Count Display Badge */}
            <span
              className="badge badge-verified"
              style={{ fontSize: '0.74rem', padding: '0.25rem 0.6rem' }}
              title={t('verifiedLocalData', 'Verified coverage from local data index')}
            >
              <Icon name="check" size={11} style={{ marginRight: '3px' }} />
              {selectedStateFilter === 'ALL'
                ? `${t('statesUtsCount', '28 States & 8 UTs')} • ${totalFilteredCount.toLocaleString()} ${t('schemesIndexed', 'schemes indexed')}`
                : `${totalFilteredCount.toLocaleString()} ${t('schemesIndexed', 'schemes indexed')} • ${t('syncedDate', 'Synced')} ${lastSyncedDate}`}
            </span>
          </div>
        </div>

        {/* Categories Pills */}
        <div style={{ marginBottom: '1rem' }}>
          <div style={{ fontSize: '0.76rem', textTransform: 'uppercase', letterSpacing: '0.06em', color: 'var(--text-muted)', marginBottom: '0.45rem', fontWeight: 700 }}>
            {t('category', 'Target Beneficiary Category')}
          </div>
          <div style={{ display: 'flex', flexWrap: 'wrap', gap: '0.4rem' }}>
            {categories.map((c) => (
              <button
                key={c.id}
                type="button"
                onClick={() => setSelectedCategoryFilter(c.id)}
                className={`quick-query-btn ${selectedCategoryFilter === c.id ? 'active' : ''}`}
                style={{
                  padding: '0.35rem 0.75rem',
                  fontSize: '0.78rem',
                  background: selectedCategoryFilter === c.id ? 'var(--primary-gradient)' : 'var(--bg-surface-elevated)',
                  color: selectedCategoryFilter === c.id ? '#ffffff' : 'var(--text-secondary)',
                  border: '1px solid var(--border-card)',
                  borderRadius: 'var(--radius-full)',
                }}
              >
                {t(c.transKey, c.label)}
              </button>
            ))}
          </div>
        </div>

        {/* Benefit Type Selector */}
        <div>
          <div style={{ fontSize: '0.76rem', textTransform: 'uppercase', letterSpacing: '0.06em', color: 'var(--text-muted)', marginBottom: '0.45rem', fontWeight: 700 }}>
            {t('allBenefitTypes', 'Benefit Delivery Type')}
          </div>
          <div style={{ display: 'flex', flexWrap: 'wrap', gap: '0.4rem' }}>
            {benefitTypes.map((b) => (
              <button
                key={b.id}
                type="button"
                onClick={() => setSelectedBenefitType(b.id)}
                className={`quick-query-btn ${selectedBenefitType === b.id ? 'active' : ''}`}
                style={{
                  padding: '0.3rem 0.65rem',
                  fontSize: '0.75rem',
                  background: selectedBenefitType === b.id ? 'var(--accent-info-bg)' : 'transparent',
                  color: selectedBenefitType === b.id ? 'var(--accent-info)' : 'var(--text-muted)',
                  border: `1px solid ${selectedBenefitType === b.id ? 'var(--accent-info)' : 'var(--border-subtle)'}`,
                  borderRadius: 'var(--radius-sm)',
                }}
              >
                {t(b.transKey, b.label)}
              </button>
            ))}
          </div>
        </div>
      </div>
    </div>
  )
}
