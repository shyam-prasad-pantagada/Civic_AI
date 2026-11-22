import React, { useState } from 'react'
import Icon from './Icon'
import { useLanguage } from '../i18n'

const INDIAN_STATES = [
  'Central', 'DL', 'MH', 'KA', 'UP', 'TN', 'WB', 'GJ', 'RJ', 'KL', 'TS', 'BR', 'MP', 'AP', 'PB', 'HR'
]

const DOC_TYPES = ['circular', 'scheme', 'gazette', 'legal', 'tax']

export default function UploadCard({ onAnalyze, isLoading }) {
  const { t } = useLanguage()
  const [activeTab, setActiveTab] = useState('upload') // 'upload' | 'paste'
  const [dragOver, setDragOver] = useState(false)
  const [selectedFile, setSelectedFile] = useState(null)
  const [pastedText, setPastedText] = useState('')
  const [selectedState, setSelectedState] = useState('Central')
  const [docType, setDocType] = useState('circular')

  const handleDragOver = (e) => {
    e.preventDefault()
    setDragOver(true)
  }

  const handleDragLeave = () => {
    setDragOver(false)
  }

  const MAX_FILE_SIZE_BYTES = 50 * 1024 * 1024 // 50MB

  const handleDrop = (e) => {
    e.preventDefault()
    setDragOver(false)
    if (e.dataTransfer.files && e.dataTransfer.files.length > 0) {
      const file = e.dataTransfer.files[0]
      if (file.size > MAX_FILE_SIZE_BYTES) {
        alert(t('fileSizeLimit', 'File size exceeds 50MB limit.'))
        return
      }
      setSelectedFile(file)
    }
  }

  const handleFileChange = (e) => {
    if (e.target.files && e.target.files.length > 0) {
      const file = e.target.files[0]
      if (file.size > MAX_FILE_SIZE_BYTES) {
        alert(t('fileSizeLimit', 'File size exceeds 50MB limit.'))
        return
      }
      setSelectedFile(file)
    }
  }

  const handleSubmit = () => {
    if (activeTab === 'upload') {
      if (!selectedFile) return
      onAnalyze({
        mode: 'upload',
        file: selectedFile,
        state: selectedState,
        docType: docType,
      })
    } else {
      if (!pastedText.trim()) return
      onAnalyze({
        mode: 'paste',
        text: pastedText,
        state: selectedState,
        docType: docType,
      })
    }
  }

  return (
    <div className="glass-card" style={{ maxWidth: '820px', margin: '0 auto' }}>
      {/* Top Header & State / Type Bar */}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1.5rem', flexWrap: 'wrap', gap: '1rem' }}>
        <div style={{ display: 'flex', gap: '0.5rem', background: 'var(--bg-surface-elevated)', padding: '0.25rem', borderRadius: 'var(--radius-full)', border: '1px solid var(--border-card)' }}>
          <button 
            type="button"
            className={`btn-secondary ${activeTab === 'upload' ? 'btn-primary' : ''}`}
            style={{ padding: '0.45rem 1.1rem', fontSize: '0.85rem', borderRadius: 'var(--radius-full)', display: 'inline-flex', alignItems: 'center', gap: '6px' }}
            onClick={() => setActiveTab('upload')}
          >
            <Icon name="document" size={14} />
            <span>{t('uploadTab', 'Upload File (PDF/Image)')}</span>
          </button>
          <button 
            type="button"
            className={`btn-secondary ${activeTab === 'paste' ? 'btn-primary' : ''}`}
            style={{ padding: '0.45rem 1.1rem', fontSize: '0.85rem', borderRadius: 'var(--radius-full)', display: 'inline-flex', alignItems: 'center', gap: '6px' }}
            onClick={() => setActiveTab('paste')}
          >
            <Icon name="copy" size={14} />
            <span>{t('pasteTab', 'Paste Text')}</span>
          </button>
        </div>

        <div style={{ display: 'flex', gap: '0.75rem', flexWrap: 'wrap' }}>
          <select 
            className="select" 
            style={{ width: 'auto', padding: '0.45rem 2.2rem 0.45rem 0.85rem', fontSize: '0.85rem' }}
            value={selectedState}
            onChange={(e) => setSelectedState(e.target.value)}
          >
            {INDIAN_STATES.map((st) => (
              <option key={st} value={st}>
                {t(`state_${st}`, st === 'Central' ? 'Central / All India' : st)}
              </option>
            ))}
          </select>

          <select 
            className="select" 
            style={{ width: 'auto', padding: '0.45rem 2.2rem 0.45rem 0.85rem', fontSize: '0.85rem' }}
            value={docType}
            onChange={(e) => setDocType(e.target.value)}
          >
            {DOC_TYPES.map((dt) => (
              <option key={dt} value={dt}>
                {t(`docType_${dt}`, dt)}
              </option>
            ))}
          </select>
        </div>
      </div>

      {/* Main Upload Zone or Text Area */}
      {activeTab === 'upload' ? (
        <div>
          <div 
            className={`upload-zone ${dragOver ? 'active' : ''}`}
            onDragOver={handleDragOver}
            onDragLeave={handleDragLeave}
            onDrop={handleDrop}
            onClick={() => document.getElementById('file-upload-input').click()}
          >
            <input 
              id="file-upload-input" 
              type="file" 
              accept=".pdf,.png,.jpg,.jpeg,.webp" 
              style={{ display: 'none' }} 
              onChange={handleFileChange}
            />
            <div className="upload-icon-wrapper">
              <Icon name="document" size={32} color="var(--primary-start)" />
            </div>
            <div className="upload-title">
              {selectedFile ? selectedFile.name : t('dropDocument', 'Drop your government document here, or browse files')}
            </div>
            <div className="upload-subtitle">
              {t('dropSubtitle', 'Supports official PDFs, Gazette scans, circular photos (PNG/JPG). Max 50MB (up to 100 pages).')}
            </div>
            <div style={{ display: 'inline-flex', gap: '0.5rem', alignItems: 'center' }}>
              <span className="badge badge-pill">{t('textExtract', 'PyMuPDF Text Extract')}</span>
              <span className="badge badge-pill">{t('multimodalOcr', 'AI Multimodal OCR')}</span>
            </div>
          </div>

          {selectedFile && (
            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginTop: '1rem', padding: '0.75rem 1rem', background: 'var(--bg-surface-elevated)', borderRadius: 'var(--radius-md)', border: '1px solid var(--border-subtle)' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
                <Icon name="document" size={18} color="var(--primary-start)" />
                <div>
                  <div style={{ fontSize: '0.9rem', fontWeight: 600 }}>{selectedFile.name}</div>
                  <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>
                    {(selectedFile.size / 1024 / 1024).toFixed(2)} MB
                  </div>
                </div>
              </div>
              <button 
                type="button" 
                onClick={(e) => { e.stopPropagation(); setSelectedFile(null); }}
                style={{ background: 'none', border: 'none', color: 'var(--accent-error)', cursor: 'pointer', fontSize: '0.85rem' }}
              >
                {t('removeFile', 'Remove')}
              </button>
            </div>
          )}
        </div>
      ) : (
        <div>
          <div style={{ marginBottom: '0.6rem' }}>
            <span style={{ fontSize: '0.82rem', color: 'var(--text-secondary)' }}>
              {t('pasteLabel', 'Enter or paste text from circular, notification, or order:')}
            </span>
          </div>
          <textarea 
            className="textarea" 
            rows="6"
            placeholder={t('pastePlaceholder', 'Paste raw notice text, gazette excerpt, government order paragraph or scheme conditions here...')}
            value={pastedText}
            onChange={(e) => setPastedText(e.target.value)}
          />
          <div style={{ display: 'flex', justifyContent: 'space-between', marginTop: '0.5rem', fontSize: '0.78rem', color: 'var(--text-muted)' }}>
            <span>{t('pasteHelper', 'Auto-detects deadlines, affected citizen groups, and statutory acts')}</span>
            <span>{pastedText.length} {t('characters', 'characters')}</span>
          </div>
        </div>
      )}

      {/* Action Footer */}
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginTop: '1.75rem', paddingTop: '1.25rem', borderTop: '1px solid var(--border-subtle)', flexWrap: 'wrap', gap: '1rem' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.6rem' }}>
          <span className="badge badge-verified">{t('grade6Readability', 'Grade 6 Readability')}</span>
          <span style={{ fontSize: '0.82rem', color: 'var(--text-muted)' }}>{t('docAnalysisTitle', 'Structured plain-language civic summary')}</span>
        </div>

        <button 
          type="button" 
          className="btn-primary"
          onClick={handleSubmit}
          disabled={isLoading || (activeTab === 'upload' && !selectedFile) || (activeTab === 'paste' && !pastedText.trim())}
          style={{ display: 'inline-flex', alignItems: 'center', gap: '6px' }}
        >
          <span>{isLoading ? t('analyzingBtn', 'Analyzing Document...') : t('explainNoticeBtn', 'Explain Notice')}</span>
          <Icon name="arrow-right" size={13} />
        </button>
      </div>
    </div>
  )
}
