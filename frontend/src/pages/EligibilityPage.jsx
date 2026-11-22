import React, { useState, useEffect, useMemo } from 'react'
import SchemeFilters from '../components/eligibility/SchemeFilters'
import SchemeCard from '../components/eligibility/SchemeCard'
import SchemeDetailModal from '../components/eligibility/SchemeDetailModal'
import EligibilityCalculatorForm from '../components/eligibility/EligibilityCalculatorForm'
import EligibilityResults from '../components/eligibility/EligibilityResults'
import SkeletonLoader from '../components/SkeletonLoader'
import Icon from '../components/Icon'
import { useLanguage } from '../i18n'

const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:8000'

const ALL_STATES_AND_UTS = [
  { code: 'ALL', name: 'All India (28 States & 8 UTs)', group: 'all' },
  { code: 'Central', name: 'Central Government (Nationwide)', group: 'central' },
  // 28 Indian States
  { code: 'AP', name: 'Andhra Pradesh', group: 'state' },
  { code: 'AR', name: 'Arunachal Pradesh', group: 'state' },
  { code: 'AS', name: 'Assam', group: 'state' },
  { code: 'BR', name: 'Bihar', group: 'state' },
  { code: 'CG', name: 'Chhattisgarh', group: 'state' },
  { code: 'GA', name: 'Goa', group: 'state' },
  { code: 'GJ', name: 'Gujarat', group: 'state' },
  { code: 'HR', name: 'Haryana', group: 'state' },
  { code: 'HP', name: 'Himachal Pradesh', group: 'state' },
  { code: 'JH', name: 'Jharkhand', group: 'state' },
  { code: 'KA', name: 'Karnataka', group: 'state' },
  { code: 'KL', name: 'Kerala', group: 'state' },
  { code: 'MP', name: 'Madhya Pradesh', group: 'state' },
  { code: 'MH', name: 'Maharashtra', group: 'state' },
  { code: 'MN', name: 'Manipur', group: 'state' },
  { code: 'ML', name: 'Meghalaya', group: 'state' },
  { code: 'MZ', name: 'Mizoram', group: 'state' },
  { code: 'NL', name: 'Nagaland', group: 'state' },
  { code: 'OD', name: 'Odisha', group: 'state' },
  { code: 'PB', name: 'Punjab', group: 'state' },
  { code: 'RJ', name: 'Rajasthan', group: 'state' },
  { code: 'SK', name: 'Sikkim', group: 'state' },
  { code: 'TN', name: 'Tamil Nadu', group: 'state' },
  { code: 'TS', name: 'Telangana', group: 'state' },
  { code: 'TR', name: 'Tripura', group: 'state' },
  { code: 'UP', name: 'Uttar Pradesh', group: 'state' },
  { code: 'UK', name: 'Uttarakhand', group: 'state' },
  { code: 'WB', name: 'West Bengal', group: 'state' },
  // 8 Union Territories
  { code: 'AN', name: 'Andaman & Nicobar Islands (UT)', group: 'ut' },
  { code: 'CH', name: 'Chandigarh (UT)', group: 'ut' },
  { code: 'DN', name: 'Dadra & Nagar Haveli and Daman & Diu (UT)', group: 'ut' },
  { code: 'DL', name: 'Delhi (NCT)', group: 'ut' },
  { code: 'JK', name: 'Jammu & Kashmir (UT)', group: 'ut' },
  { code: 'LA', name: 'Ladakh (UT)', group: 'ut' },
  { code: 'LD', name: 'Lakshadweep (UT)', group: 'ut' },
  { code: 'PY', name: 'Puducherry (UT)', group: 'ut' },
]

const CATEGORY_FILTERS = [
  { id: 'all', label: 'All Categories', transKey: 'allCategories' },
  { id: 'farmer', label: '🌾 Agriculture & Farmers', transKey: 'agriculture' },
  { id: 'health', label: '🏥 Health & Healthcare', transKey: 'healthcare' },
  { id: 'woman', label: '👩 Women & Child Welfare', transKey: 'womenChild' },
  { id: 'student', label: '🎓 Education & Students', transKey: 'education' },
  { id: 'senior', label: '👴 Senior Citizens & Pension', transKey: 'seniorPension' },
  { id: 'disabled', label: '♿ Disability & Welfare', transKey: 'disability' },
  { id: 'entrepreneur', label: '💼 MSME & Self-Employed', transKey: 'msme' },
  { id: 'housing', label: '🏠 Housing & Urban', transKey: 'housing' },
  { id: 'worker', label: '👷 Workers & Labour', transKey: 'workers' },
]

const BENEFIT_TYPES = [
  { id: 'all', label: 'All Benefit Types', transKey: 'allBenefitTypes' },
  { id: 'cash', label: 'Cash / DBT', transKey: 'cashDbt' },
  { id: 'inkind', label: 'In-Kind / Material', transKey: 'inkind' },
  { id: 'composite', label: 'Composite / Subsidy', transKey: 'subsidy' },
]

export default function EligibilityPage() {
  const { lang, t } = useLanguage()
  const [activeTab, setActiveTab] = useState('directory') // 'directory' | 'calculator'
  const [schemes, setSchemes] = useState([])
  const [loadingSchemes, setLoadingSchemes] = useState(true)
  const [searchQuery, setSearchQuery] = useState('')
  const [jurisdictionFilter, setJurisdictionFilter] = useState('all')
  const [schemeTypeFilter, setSchemeTypeFilter] = useState('all')
  const [selectedStateFilter, setSelectedStateFilter] = useState('ALL')
  const [selectedCategoryFilter, setSelectedCategoryFilter] = useState('all')
  const [selectedBenefitType, setSelectedBenefitType] = useState('all')
  const [selectedSchemeDetail, setSelectedSchemeDetail] = useState(null)
  const [page, setPage] = useState(1)
  const [totalSchemes, setTotalSchemes] = useState(0)
  const [hasMore, setHasMore] = useState(false)
  const [loadingMore, setLoadingMore] = useState(false)

  // Live Fallback state
  const [isLiveSearching, setIsLiveSearching] = useState(false)
  const [liveSearchStatus, setLiveSearchStatus] = useState(null)

  // Calculator state
  const [profile, setProfile] = useState({
    state: 'Central',
    age: '',
    gender: 'female',
    annual_income: '',
    category: 'all',
    land_holding_acres: '',
    disability_percentage: '',
  })
  const [targetedScheme, setTargetedScheme] = useState(null)
  const [loadingCalc, setLoadingCalc] = useState(false)
  const [calcResults, setCalcResults] = useState(null)
  const [calcError, setCalcError] = useState(null)

  const fetchSchemes = async (pageNum = 1, append = false) => {
    if (append) {
      setLoadingMore(true)
    } else {
      setLoadingSchemes(true)
    }

    try {
      const params = new URLSearchParams({
        page: String(pageNum),
        page_size: '24',
        lang: lang,
      })

      if (searchQuery.trim()) params.append('search', searchQuery.trim())
      if (schemeTypeFilter !== 'all') params.append('scheme_type', schemeTypeFilter)
      if (jurisdictionFilter !== 'all') params.append('jurisdiction', jurisdictionFilter)
      if (selectedStateFilter !== 'ALL') params.append('state', selectedStateFilter)
      if (selectedCategoryFilter !== 'all') params.append('category', selectedCategoryFilter)
      if (selectedBenefitType !== 'all') params.append('benefit_type', selectedBenefitType)

      const res = await fetch(`${API_BASE}/api/schemes?${params.toString()}`)
      if (res.ok) {
        const data = await res.json()
        if (data && typeof data === 'object' && Array.isArray(data.items)) {
          if (append) {
            setSchemes((prev) => [...prev, ...data.items])
          } else {
            setSchemes(data.items)
          }
          setTotalSchemes(data.total || 0)
          setHasMore(pageNum < (data.total_pages || 1))
          setPage(pageNum)
        } else if (Array.isArray(data)) {
          setSchemes(data)
          setTotalSchemes(data.length)
          setHasMore(false)
        }
      }
    } catch (err) {
      console.error('Failed to load schemes directory:', err)
    } finally {
      setLoadingSchemes(false)
      setLoadingMore(false)
    }
  }

  // Reload when filters or language change
  useEffect(() => {
    setPage(1)
    fetchSchemes(1, false)
  }, [lang, searchQuery, schemeTypeFilter, jurisdictionFilter, selectedStateFilter, selectedCategoryFilter, selectedBenefitType])

  const handleLoadMore = () => {
    if (!loadingMore && hasMore) {
      fetchSchemes(page + 1, true)
    }
  }

  // Live scheme count by state from active dataset
  const schemesCountByState = useMemo(() => {
    const counts = {}
    schemes.forEach((s) => {
      const st = s.state || 'Central'
      counts[st] = (counts[st] || 0) + 1
    })
    return counts
  }, [schemes])

  // Filtered schemes computation
  const filteredSchemes = useMemo(() => {
    return schemes.filter((s) => {
      if (jurisdictionFilter === 'central' && s.state !== 'Central') return false
      if (jurisdictionFilter === 'state' && s.state === 'Central') return false

      if (selectedStateFilter !== 'ALL') {
        if (s.state !== 'Central' && s.state !== selectedStateFilter) {
          const appStates = s.applicable_states || []
          if (!appStates.includes(selectedStateFilter) && !appStates.includes('All India')) {
            return false
          }
        }
      }

      if (selectedCategoryFilter !== 'all') {
        const cat = (s.category || '').toLowerCase()
        if (cat !== selectedCategoryFilter.toLowerCase()) return false
      }

      if (selectedBenefitType !== 'all') {
        const bType = (s.benefit_type || '').toLowerCase()
        if (selectedBenefitType === 'cash' && !bType.includes('cash') && !bType.includes('dbt')) return false
        if (selectedBenefitType === 'inkind' && !bType.includes('kind') && !bType.includes('subsidy')) return false
      }

      if (searchQuery.trim()) {
        const q = searchQuery.toLowerCase()
        const text = `${s.scheme_id} ${s.scheme_name} ${s.ministry || ''} ${s.summary || ''} ${(s.benefits || []).join(' ')}`.toLowerCase()
        
        // Also search regional translations
        const translations = s.translations || {}
        const transText = Object.values(translations)
          .map((t) => `${t.scheme_name || ''} ${t.summary || ''}`)
          .join(' ')
          .toLowerCase()

        if (!text.includes(q) && !transText.includes(q)) return false
      }

      return true
    })
  }, [schemes, jurisdictionFilter, selectedStateFilter, selectedCategoryFilter, selectedBenefitType, searchQuery])

  // Live Search Fallback
  const handleLiveSearch = async (queryText) => {
    const q = (queryText || searchQuery).trim()
    if (!q) return

    setIsLiveSearching(true)
    setLiveSearchStatus(`Searching official portals (myscheme.gov.in, gov.in) for "${q}"...`)

    try {
      const res = await fetch(`${API_BASE}/api/schemes/live-lookup`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          query: q,
          state: selectedStateFilter !== 'ALL' && selectedStateFilter !== 'Central' ? selectedStateFilter : null,
          category: selectedCategoryFilter !== 'all' ? selectedCategoryFilter : null,
          lang: lang,
        }),
      })

      if (res.ok) {
        const liveScheme = await res.json()
        setSchemes((prev) => {
          const exists = prev.some((s) => s.scheme_id.toUpperCase() === liveScheme.scheme_id.toUpperCase())
          return exists
            ? prev.map((s) => (s.scheme_id.toUpperCase() === liveScheme.scheme_id.toUpperCase() ? liveScheme : s))
            : [liveScheme, ...prev]
        })
        setSelectedSchemeDetail(liveScheme)
        setLiveSearchStatus(null)
      } else {
        setLiveSearchStatus('No official scheme record identified online. Please check spelling.')
        setTimeout(() => setLiveSearchStatus(null), 4000)
      }
    } catch (err) {
      console.error('Live search error:', err)
      setLiveSearchStatus('Live search encountered an error. Please retry.')
      setTimeout(() => setLiveSearchStatus(null), 4000)
    } finally {
      setIsLiveSearching(false)
    }
  }

  // Trigger evaluation from scheme card
  const handleTestEligibility = (scheme) => {
    setTargetedScheme(scheme)
    if (scheme.state && scheme.state !== 'Central') {
      setProfile((prev) => ({ ...prev, state: scheme.state, category: scheme.category || prev.category }))
    }
    setActiveTab('calculator')
    window.scrollTo({ top: 0, behavior: 'smooth' })
  }

  const handleProfileChange = (field, val) => {
    setProfile((prev) => ({ ...prev, [field]: val }))
  }

  const handleCalculateEligibility = async (e) => {
    if (e) e.preventDefault()
    setLoadingCalc(true)
    setCalcError(null)

    try {
      const payload = {
        profile: {
          age: profile.age ? parseInt(profile.age, 10) : null,
          gender: profile.gender || null,
          state: profile.state === 'Central' ? null : profile.state,
          annual_income: profile.annual_income ? parseFloat(profile.annual_income) : null,
          category: profile.category === 'all' ? null : profile.category,
          land_holding_acres: profile.land_holding_acres ? parseFloat(profile.land_holding_acres) : null,
          disability_percentage: profile.disability_percentage ? parseFloat(profile.disability_percentage) : null,
        },
        state: profile.state === 'Central' ? null : profile.state,
        scheme_category: profile.category === 'all' ? null : profile.category,
        lang: lang,
      }

      const res = await fetch(`${API_BASE}/api/eligibility?lang=${lang}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload),
      })

      if (!res.ok) {
        const err = await res.json().catch(() => ({}))
        throw new Error(err.detail || `Server error (${res.status})`)
      }

      const data = await res.json()
      setCalcResults(data)
    } catch (err) {
      console.error('Eligibility calculation error:', err)
      setCalcError(err.message || 'Failed to evaluate eligibility.')
    } finally {
      setLoadingCalc(false)
    }
  }

  return (
    <div>
      {/* Header */}
      <div className="page-header">
        <span className="badge badge-pill page-badge">
          <Icon name="gov" size={13} style={{ marginRight: '4px' }} />
          <span>{t('statesAndUts', '28 States & 8 UTs')} • {totalSchemes > 0 ? `${totalSchemes.toLocaleString()} ${t('schemesIndexedBanner', 'Schemes Indexed • Central • State/UT')}` : t('schemesIndexedBanner', 'Schemes Indexed • Central • State/UT')}</span>
        </span>
        <h1 className="page-title">
          {t('pageTitle', 'Scheme Directory & Eligibility Checker')}
        </h1>
        <p className="page-subtitle">
          {t('pageSubtitle', 'Browse verified Central & State welfare schemes across all 28 States & 8 Union Territories, or test your demographic profile against deterministic rules.')}
        </p>
      </div>

      {/* Primary Section Switcher */}
      <div style={{ display: 'flex', justifyContent: 'center', marginBottom: '2.5rem' }}>
        <div style={{ display: 'inline-flex', padding: '0.35rem', background: 'var(--bg-surface-elevated)', borderRadius: 'var(--radius-full)', border: '1px solid var(--border-card)' }}>
          <button
            type="button"
            className={`btn-secondary ${activeTab === 'directory' ? 'btn-primary' : ''}`}
            style={{ borderRadius: 'var(--radius-full)', padding: '0.55rem 1.4rem', fontSize: '0.88rem', border: 'none' }}
            onClick={() => setActiveTab('directory')}
          >
            <Icon name="search" size={14} style={{ marginRight: '6px' }} />
            <span>{t('browseSchemesTab', 'Browse & Search Schemes')}</span>
          </button>
          <button
            type="button"
            className={`btn-secondary ${activeTab === 'calculator' ? 'btn-primary' : ''}`}
            style={{ borderRadius: 'var(--radius-full)', padding: '0.55rem 1.4rem', fontSize: '0.88rem', border: 'none' }}
            onClick={() => setActiveTab('calculator')}
          >
            <Icon name="target" size={14} style={{ marginRight: '6px' }} />
            <span>{t('calculatorTab', 'Eligibility Calculator')}</span>
          </button>
        </div>
      </div>

      {/* Directory Tab View */}
      {activeTab === 'directory' && (
        <div>
          {/* Cascading Filter Controls */}
          <SchemeFilters
            searchQuery={searchQuery}
            setSearchQuery={setSearchQuery}
            jurisdictionFilter={jurisdictionFilter}
            setJurisdictionFilter={setJurisdictionFilter}
            schemeTypeFilter={schemeTypeFilter}
            setSchemeTypeFilter={setSchemeTypeFilter}
            selectedStateFilter={selectedStateFilter}
            setSelectedStateFilter={setSelectedStateFilter}
            selectedCategoryFilter={selectedCategoryFilter}
            setSelectedCategoryFilter={setSelectedCategoryFilter}
            selectedBenefitType={selectedBenefitType}
            setSelectedBenefitType={setSelectedBenefitType}
            allStates={ALL_STATES_AND_UTS}
            categories={CATEGORY_FILTERS}
            benefitTypes={BENEFIT_TYPES}
            onLiveSearch={handleLiveSearch}
            isLiveSearching={isLiveSearching}
            totalFilteredCount={totalSchemes}
          />

          {/* Live Search Status Banner */}
          {liveSearchStatus && (
            <div style={{ padding: '0.9rem 1.25rem', background: 'var(--accent-info-bg)', border: '1px solid var(--accent-info)', borderRadius: 'var(--radius-md)', marginBottom: '1.5rem', fontSize: '0.88rem', color: 'var(--text-primary)', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
              <Icon name="refresh" size={14} />
              <span>{liveSearchStatus}</span>
            </div>
          )}

          {/* Schemes Grid with Exact Count Banner */}
          {loadingSchemes ? (
            <SkeletonLoader count={6} />
          ) : schemes.length > 0 ? (
            <div>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1.25rem', flexWrap: 'wrap', gap: '0.5rem' }}>
                <span style={{ fontSize: '0.88rem', color: 'var(--text-secondary)' }}>
                  {t('showingSchemes', 'Showing')} <strong>{schemes.length.toLocaleString()}</strong> {t('of', 'of')} <strong>{totalSchemes.toLocaleString()}</strong> {t('matchingSchemes', 'matching government schemes')}
                </span>
                <span className="badge badge-pill" style={{ fontSize: '0.78rem' }}>
                  {selectedStateFilter !== 'ALL' ? `${t('state_' + selectedStateFilter, selectedStateFilter)} • ` : ''}
                  {schemeTypeFilter !== 'all'
                    ? (schemeTypeFilter === 'central' ? t('centralGovt', 'Central Schemes') : schemeTypeFilter === 'integrated' ? t('integratedScheme', 'Integrated Schemes') : schemeTypeFilter === 'multi_state' ? t('multiStateScheme', 'Multi-State') : t('stateUtSchemes', 'State / UT'))
                    : (jurisdictionFilter === 'all' ? t('allJurisdictions', 'All Jurisdictions') : jurisdictionFilter === 'central' ? t('centralGovt', 'Central Schemes') : t('stateUtSchemes', 'State / UT Specific'))}
                </span>
              </div>

              <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(340px, 1fr))', gap: '1.5rem', marginBottom: '2rem' }}>
                {schemes.map((scheme) => (
                  <SchemeCard
                    key={scheme.scheme_id}
                    scheme={scheme}
                    onOpenDetails={(s) => setSelectedSchemeDetail(s)}
                    onTestEligibility={handleTestEligibility}
                  />
                ))}
              </div>

              {/* Load More Pagination Button */}
              {hasMore && (
                <div style={{ textAlign: 'center', margin: '2rem 0' }}>
                  <button
                    type="button"
                    className="btn-primary"
                    style={{ padding: '0.65rem 1.8rem', fontSize: '0.9rem' }}
                    onClick={handleLoadMore}
                    disabled={loadingMore}
                  >
                    <span>{loadingMore ? t('loading', 'Loading...') : `${t('loadMore', 'Load More Schemes')} (${Math.max(0, totalSchemes - schemes.length).toLocaleString()} ${t('remaining', 'remaining')})`}</span>
                  </button>
                </div>
              )}
            </div>
          ) : (
            /* Empty State with Next Step Action */
            <div className="card" style={{ textAlign: 'center', padding: '3.5rem 1.5rem', maxWidth: '640px', margin: '2rem auto' }}>
              <Icon name="search" size={36} color="var(--text-muted)" style={{ marginBottom: '1rem' }} />
              <h3 style={{ fontSize: '1.25rem', fontWeight: 700, color: 'var(--text-primary)', marginBottom: '0.5rem' }}>
                {t('noSchemesFoundTitle', 'No schemes indexed yet for this selection')}
              </h3>
              <p style={{ fontSize: '0.88rem', color: 'var(--text-secondary)', marginBottom: '1.5rem', lineHeight: 1.5 }}>
                {t('noSchemesFoundSub', 'No local rules matched your filter criteria in the verified offline dataset. You can trigger a live AI search across official government portals (myscheme.gov.in / gov.in).')}
              </p>
              <button
                type="button"
                className="btn-primary"
                onClick={() => handleLiveSearch(searchQuery || selectedStateFilter)}
                disabled={isLiveSearching}
                style={{ display: 'inline-flex', alignItems: 'center', gap: '0.5rem', margin: '0 auto' }}
              >
                <Icon name="refresh" size={14} />
                <span>{t('liveAiSearchPrompt', 'Try Live AI Search for')} "{searchQuery || selectedStateFilter}"</span>
              </button>
            </div>
          )}
        </div>
      )}

      {/* Calculator Tab View */}
      {activeTab === 'calculator' && (
        <div style={{ maxWidth: '920px', margin: '0 auto' }}>
          <EligibilityCalculatorForm
            profile={profile}
            onProfileChange={handleProfileChange}
            onSubmit={handleCalculateEligibility}
            loading={loadingCalc}
            allStates={ALL_STATES_AND_UTS}
            categories={CATEGORY_FILTERS}
            targetedScheme={targetedScheme}
            onClearTargetedScheme={() => setTargetedScheme(null)}
          />

          {calcError && (
            <div style={{ padding: '1rem', background: 'var(--accent-error-bg)', border: '1px solid var(--accent-error)', borderRadius: 'var(--radius-md)', color: 'var(--accent-error)', marginBottom: '1.5rem' }}>
              <strong>Error: </strong> {calcError}
            </div>
          )}

          {loadingCalc && <SkeletonLoader count={3} />}

          {calcResults && (
            <EligibilityResults
              results={calcResults}
              onOpenDetails={(item) => setSelectedSchemeDetail(item)}
            />
          )}
        </div>
      )}

      {/* Policy Details Modal (Rendered via React Portal) */}
      {selectedSchemeDetail && (
        <SchemeDetailModal
          scheme={selectedSchemeDetail}
          onClose={() => setSelectedSchemeDetail(null)}
          onTestEligibility={handleTestEligibility}
          selectedStateFilter={selectedStateFilter}
        />
      )}
    </div>
  )
}
