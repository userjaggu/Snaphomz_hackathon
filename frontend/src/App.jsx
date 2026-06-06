import { useState } from 'react'
import axios from 'axios'
import './App.css'

function App() {
  const [zipCode, setZipCode] = useState('')
  const [report, setReport] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  const handleGenerate = async () => {
    setLoading(true)
    setError('')
    try {
      const response = await axios.post('http://localhost:8000/generate-report', {
        zip_code: zipCode
      })
      setReport(response.data)
    } catch (err) {
      setError('Failed to generate report. Please try again.')
      console.error(err)
    }
    setLoading(false)
  }

  const handleDownload = async () => {
    if (!report) return
    try {
      const response = await axios.post('http://localhost:8000/download-report', report, {
        responseType: 'blob'
      })
      const url = window.URL.createObjectURL(new Blob([response.data]))
      const link = document.createElement('a')
      link.href = url
      link.setAttribute('download', `SnapReport_${report.zip_code}.pdf`)
      document.body.appendChild(link)
      link.click()
      link.remove()
    } catch (err) {
      console.error('Download failed', err)
      alert("Failed to download PDF")
    }
  }

  return (
    <div style={{ maxWidth: '800px', margin: '0 auto', padding: '20px', fontFamily: 'sans-serif' }}>
      <header style={{ borderBottom: '2px solid #eee', marginBottom: '20px', paddingBottom: '10px' }}>
        <h1 style={{ color: '#2c3e50', margin: 0 }}>SnapReport by Snaphomz</h1>
        <p style={{ color: '#7f8c8d' }}>Generate AI-powered market reports in seconds.</p>
      </header>
      
      <div style={{ display: 'flex', gap: '10px', marginBottom: '20px' }}>
        <input 
          type="text" 
          value={zipCode}
          onChange={(e) => setZipCode(e.target.value)}
          placeholder="Enter ZIP Code (e.g. 90210)"
          style={{ padding: '10px', fontSize: '16px', flex: '1', borderRadius: '4px', border: '1px solid #ccc' }}
        />
        <button 
          onClick={handleGenerate} 
          disabled={loading || !zipCode}
          style={{ padding: '10px 20px', fontSize: '16px', backgroundColor: '#3498db', color: 'white', border: 'none', cursor: 'pointer', borderRadius: '4px' }}
        >
          {loading ? 'Generating...' : 'Generate Report'}
        </button>
      </div>

      {error && <div style={{ color: 'red', marginBottom: '20px' }}>{error}</div>}

      {report && (
        <div style={{ border: '1px solid #ddd', padding: '20px', borderRadius: '5px' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '20px' }}>
            <h2 style={{ margin: 0 }}>Market Report for {report.zip_code}</h2>
            <button 
              onClick={handleDownload}
              style={{ padding: '10px 15px', backgroundColor: '#2ecc71', color: 'white', border: 'none', cursor: 'pointer', borderRadius: '4px', fontWeight: 'bold' }}
            >
              Download PDF
            </button>
          </div>
          
          <div style={{ display: 'flex', flexWrap: 'wrap', gap: '10px', marginBottom: '20px' }}>
            {Object.entries(report.market_data).map(([key, value]) => (
              <div key={key} style={{ background: '#f8f9fa', padding: '15px 10px', borderRadius: '5px', textAlign: 'center', border: '1px solid #eee', flex: '1 1 130px' }}>
                <div style={{ fontSize: '12px', color: '#7f8c8d', marginBottom: '5px' }}>{key}</div>
                <div style={{ fontSize: '18px', fontWeight: 'bold', color: '#2c3e50' }}>{value}</div>
              </div>
            ))}
          </div>

          <div>
            <h3 style={{ marginTop: '30px', borderBottom: '1px solid #eee', paddingBottom: '10px' }}>AI Insights</h3>
            <div style={{ whiteSpace: 'pre-wrap', lineHeight: '1.6', color: '#34495e', background: '#f4f6f7', padding: '20px', borderRadius: '5px' }}>
              {report.ai_insights}
            </div>
          </div>
        </div>
      )}
    </div>
  )
}

export default App
