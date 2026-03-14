import { useState } from 'react'
import './App.css'

function App() {
  const [file, setFile] = useState(null)
  const [loading, setLoading] = useState(false)
  const [result, setResult] = useState(null)
  const [error, setError] = useState(null)

  const handleFileChange = (e) => {
    setFile(e.target.files[0])
    setError(null)
    setResult(null)
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    if (!file) {
      setError('Please select a file')
      return
    }

    setLoading(true)
    setError(null)

    const formData = new FormData()
    formData.append('file', file)

    try {
      const response = await fetch('http://localhost:5000/api/parse-resume', {
        method: 'POST',
        body: formData,
      })

      const data = await response.json()

      if (!response.ok) {
        throw new Error(data.error || 'Failed to parse resume')
      }

      setResult(data)
    } catch (err) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="app">
      <header>
        <h1>AI Resume Parser</h1>
        <p>Extract structured data and generate interview questions</p>
      </header>

      <main>
        <form onSubmit={handleSubmit} className="upload-form">
          <div className="file-input-wrapper">
            <input
              type="file"
              accept=".pdf,.docx"
              onChange={handleFileChange}
              id="file-input"
            />
            <label htmlFor="file-input" className="file-label">
              {file ? file.name : 'Choose a resume (PDF or DOCX)'}
            </label>
          </div>
          <button type="submit" disabled={loading || !file}>
            {loading ? 'Processing...' : 'Parse Resume'}
          </button>
        </form>

        {error && <div className="error">{error}</div>}

        {result && (
          <div className="results">
            <section className="parsed-data">
              <h2>Parsed Data</h2>
              <pre>{JSON.stringify(result.parsed_resume, null, 2)}</pre>
            </section>

            <section className="questions">
              <h2>Interview Questions</h2>
              <div className="questions-grid">
                <div className="question-section">
                  <h3>Technical Questions</h3>
                  <ul>
                    {result.questions.technical?.map((q, i) => (
                      <li key={i}>{q}</li>
                    ))}
                  </ul>
                </div>
                <div className="question-section">
                  <h3>Behavioral Questions</h3>
                  <ul>
                    {result.questions.behavioral?.map((q, i) => (
                      <li key={i}>{q}</li>
                    ))}
                  </ul>
                </div>
              </div>
            </section>
          </div>
        )}
      </main>
    </div>
  )
}

export default App
