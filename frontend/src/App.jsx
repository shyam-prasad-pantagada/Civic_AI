import React, { useEffect } from 'react'
import { Routes, Route, useLocation } from 'react-router-dom'
import Navbar from './components/Navbar'
import Footer from './components/Footer'
import HomePage from './pages/HomePage'
import ExplainPage from './pages/ExplainPage'
import EligibilityPage from './pages/EligibilityPage'
import RightsPage from './pages/RightsPage'
import './App.css'

function ScrollToTop() {
  const { pathname } = useLocation()

  useEffect(() => {
    window.scrollTo({ top: 0, left: 0, behavior: 'instant' })
  }, [pathname])

  return null
}

export default function App() {
  return (
    <div className="app-container">
      <ScrollToTop />
      {/* Natural, calm civic ambient illumination */}
      <div className="ambient-background" aria-hidden="true">
        <div className="ambient-top-glow" />
        <div className="ambient-grid-overlay" />
      </div>

      <Navbar />
      <main className="main-content">
        <Routes>
          <Route path="/" element={<HomePage />} />
          <Route path="/explain" element={<ExplainPage />} />
          <Route path="/eligibility" element={<EligibilityPage />} />
          <Route path="/rights" element={<RightsPage />} />
        </Routes>
      </main>
      <Footer />
    </div>
  )
}
