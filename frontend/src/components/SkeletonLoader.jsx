import React from 'react'

/**
 * Reusable Skeleton Loader Component
 * 
 * Provides smooth pulsing placeholder skeletons during analysis,
 * scheme searches, and eligibility evaluation.
 */
export default function SkeletonLoader({ type = 'cards', count = 3 }) {
  if (type === 'analysis') {
    return (
      <div className="glass-card" style={{ maxWidth: '820px', margin: '3.5rem auto 0', padding: '2rem' }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '1.5rem' }}>
          <div className="skeleton-line" style={{ width: '40%', height: '28px' }} />
          <div className="skeleton-line" style={{ width: '20%', height: '24px', borderRadius: 'var(--radius-full)' }} />
        </div>
        <div className="skeleton-line" style={{ width: '100%', height: '16px', marginBottom: '0.65rem' }} />
        <div className="skeleton-line" style={{ width: '90%', height: '16px', marginBottom: '0.65rem' }} />
        <div className="skeleton-line" style={{ width: '75%', height: '16px', marginBottom: '1.5rem' }} />
        
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(220px, 1fr))', gap: '1rem', marginTop: '1.5rem' }}>
          <div className="skeleton-line" style={{ height: '80px', borderRadius: 'var(--radius-md)' }} />
          <div className="skeleton-line" style={{ height: '80px', borderRadius: 'var(--radius-md)' }} />
          <div className="skeleton-line" style={{ height: '80px', borderRadius: 'var(--radius-md)' }} />
        </div>
      </div>
    )
  }

  return (
    <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(320px, 1fr))', gap: '1.25rem' }}>
      {Array.from({ length: count }).map((_, i) => (
        <div key={i} className="card" style={{ minHeight: '200px' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '1rem' }}>
            <div className="skeleton-line" style={{ width: '35%', height: '20px', borderRadius: 'var(--radius-full)' }} />
            <div className="skeleton-line" style={{ width: '20%', height: '18px' }} />
          </div>
          <div className="skeleton-line" style={{ width: '70%', height: '24px', marginBottom: '0.5rem' }} />
          <div className="skeleton-line" style={{ width: '50%', height: '14px', marginBottom: '1rem' }} />
          <div className="skeleton-line" style={{ width: '100%', height: '14px', marginBottom: '0.4rem' }} />
          <div className="skeleton-line" style={{ width: '85%', height: '14px', marginBottom: '1.25rem' }} />
          <div className="skeleton-line" style={{ width: '100%', height: '40px', borderRadius: 'var(--radius-sm)' }} />
        </div>
      ))}
    </div>
  )
}
