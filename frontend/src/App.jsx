import { useState, useRef, useEffect } from 'react'
import './App.css'

const API_BASE = 'https://resume-hi9z.onrender.com/api'

const progressSteps = [
  { key: 'uploading', message: 'Uploading resume...' },
  { key: 'extracting', message: 'Extracting text from resume...' },
  { key: 'parsing', message: 'Analyzing resume content...' },
  { key: 'generating', message: 'Generating interview questions...' },
  { key: 'complete', message: 'Ready!' },
]

const skillColors = [
  '#3b82f6', '#10b981', '#f59e0b', '#ef4444', '#8b5cf6',
  '#ec4899', '#06b6d4', '#84cc16', '#f97316', '#6366f1'
]

function App() {
  const [file, setFile] = useState(null)
  const [dragActive, setDragActive] = useState(false)
  const [loading, setLoading] = useState(false)
  const [progressStep, setProgressStep] = useState(0)
  const [result, setResult] = useState(null)
  const [error, setError] = useState(null)
  const [chatMessages, setChatMessages] = useState([])
  const [chatInput, setChatInput] = useState('')
  const [isTyping, setIsTyping] = useState(false)
  const chatEndRef = useRef(null)
  const fileInputRef = useRef(null)

  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [chatMessages, isTyping])

  const handleDrag = (e) => {
    e.preventDefault()
    e.stopPropagation()
    if (e.type === 'dragenter' || e.type === 'dragover') {
      setDragActive(true)
    } else if (e.type === 'dragleave') {
      setDragActive(false)
    }
  }

  const handleDrop = (e) => {
    e.preventDefault()
    e.stopPropagation()
    setDragActive(false)
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      handleFile(e.dataTransfer.files[0])
    }
  }

  const handleFile = (selectedFile) => {
    if (selectedFile && (selectedFile.type === 'application/pdf' || 
        selectedFile.type === 'application/vnd.openxmlformats-officedocument.wordprocessingml.document')) {
      setFile(selectedFile)
      setError(null)
      setResult(null)
      setChatMessages([])
    } else {
      setError('Please upload a PDF or DOCX file')
    }
  }

  const handleFileChange = (e) => {
    if (e.target.files && e.target.files[0]) {
      handleFile(e.target.files[0])
    }
  }

  const simulateProgress = async () => {
    for (let i = 0; i < progressSteps.length - 1; i++) {
      setProgressStep(i)
      await new Promise(resolve => setTimeout(resolve, 800 + Math.random() * 400))
    }
    setProgressStep(progressSteps.length - 1)
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    if (!file) {
      setError('Please select a file')
      return
    }

    setLoading(true)
    setError(null)
    setProgressStep(0)
    simulateProgress()

    const formData = new FormData()
    formData.append('file', file)

    try {
      const response = await fetch(`${API_BASE}/parse-resume`, {
        method: 'POST',
        body: formData,
      })

      const data = await response.json()

      if (!response.ok) {
        throw new Error(data.error || 'Failed to parse resume')
      }

      setResult(data)
      
      setChatMessages([{
        role: 'assistant',
        content: `I've parsed your resume and generated interview questions. You can now:\n\n• Ask for harder or easier versions of questions\n• Focus on specific skills\n• Request model answers\n• Practice a full interview simulation\n• Ask anything about your resume\n\nWhat would you like to do?`
      }])
    } catch (err) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  const handleSendMessage = async () => {
    if (!chatInput.trim() || isTyping) return

    const userMessage = chatInput.trim()
    setChatInput('')
    
    setChatMessages(prev => [...prev, { role: 'user', content: userMessage }])
    setIsTyping(true)

    try {
      const response = await fetch(`${API_BASE}/chat`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          message: userMessage,
          resume_context: result?.parsed_resume || {},
          conversation_history: chatMessages
        })
      })

      const data = await response.json()

      if (!response.ok) {
        throw new Error(data.error || 'Failed to get response')
      }

      setChatMessages(prev => [...prev, { role: 'assistant', content: data.response }])
    } catch (err) {
      setChatMessages(prev => [...prev, { 
        role: 'assistant', 
        content: `Sorry, I encountered an error: ${err.message}` 
      }])
    } finally {
      setIsTyping(false)
    }
  }

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      handleSendMessage()
    }
  }

  const getSkillColor = (index) => skillColors[index % skillColors.length]

  const renderSkills = () => {
    const skills = result?.parsed_resume?.skills || []
    if (!skills.length) return null

    return (
      <div className="skills-section">
        <h3 className="section-title">Detected Skills</h3>
        <div className="skills-grid">
          {skills.map((skill, index) => (
            <span 
              key={index} 
              className="skill-tag"
              style={{ backgroundColor: getSkillColor(index) }}
            >
              {skill}
            </span>
          ))}
        </div>
      </div>
    )
  }

  const renderQuestions = () => {
    const questions = result?.questions
    if (!questions) return null

    return (
      <div className="questions-container">
        <div className="question-section">
          <h3 className="section-title">
            <span className="section-icon">⚡</span>
            Technical Questions
          </h3>
          <div className="questions-grid">
            {questions.technical?.map((q, i) => (
              <div key={i} className="question-card">
                <span className="question-number">{i + 1}</span>
                <p className="question-text">{q}</p>
              </div>
            ))}
          </div>
        </div>

        <div className="question-section">
          <h3 className="section-title">
            <span className="section-icon">💼</span>
            Behavioral Questions
          </h3>
          <div className="questions-grid">
            {questions.behavioral?.map((q, i) => (
              <div key={i} className="question-card behavioral">
                <span className="question-number">{i + 1}</span>
                <p className="question-text">{q}</p>
              </div>
            ))}
          </div>
        </div>
      </div>
    )
  }

  const renderChat = () => {
    if (!result) return null

    return (
      <div className="chat-section">
        <div className="chat-header">
          <h3 className="section-title">
            <span className="section-icon">💬</span>
            Interview Assistant
          </h3>
          <p className="chat-subtitle">Ask anything about your interview preparation</p>
        </div>
        
        <div className="chat-messages">
          {chatMessages.map((msg, index) => (
            <div key={index} className={`message ${msg.role}`}>
              <div className="message-avatar">
                {msg.role === 'user' ? '👤' : '🤖'}
              </div>
              <div className="message-content">
                {msg.content.split('\n').map((line, i) => (
                  <p key={i}>{line}</p>
                ))}
              </div>
            </div>
          ))}
          {isTyping && (
            <div className="message assistant typing">
              <div className="message-avatar">🤖</div>
              <div className="typing-indicator">
                <span></span>
                <span></span>
                <span></span>
              </div>
            </div>
          )}
          <div ref={chatEndRef} />
        </div>

        <div className="chat-input-container">
          <input
            type="text"
            className="chat-input"
            placeholder="Ask about harder questions, model answers, skill focus..."
            value={chatInput}
            onChange={(e) => setChatInput(e.target.value)}
            onKeyPress={handleKeyPress}
            disabled={isTyping}
          />
          <button 
            className="send-button" 
            onClick={handleSendMessage}
            disabled={isTyping || !chatInput.trim()}
          >
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <path d="M22 2L11 13M22 2l-7 20-4-9-9-4 20-7z" />
            </svg>
          </button>
        </div>
      </div>
    )
  }

  return (
    <div className="app">
      <header className="header">
        <div className="header-content">
          <div className="logo">
            <span className="logo-icon">📄</span>
            <h1>AI Resume Parser</h1>
          </div>
          <p className="tagline">Transform your resume into interview success</p>
        </div>
      </header>

      <main className="main">
        <section 
          className={`upload-section ${dragActive ? 'drag-active' : ''} ${file ? 'has-file' : ''}`}
          onDragEnter={handleDrag}
          onDragLeave={handleDrag}
          onDragOver={handleDrag}
          onDrop={handleDrop}
        >
          {!file ? (
            <div 
              className="upload-area"
              onClick={() => fileInputRef.current?.click()}
            >
              <div className="upload-icon">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5">
                  <path d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" />
                </svg>
              </div>
              <h3>Drop your resume here</h3>
              <p>or click to browse</p>
              <span className="file-types">PDF • DOCX</span>
            </div>
          ) : (
            <div className="file-selected">
              <div className="file-info">
                <span className="file-icon">📎</span>
                <span className="file-name">{file.name}</span>
              </div>
              <button 
                className="change-file"
                onClick={(e) => {
                  e.stopPropagation()
                  setFile(null)
                  setResult(null)
                  setChatMessages([])
                }}
              >
                Change file
              </button>
            </div>
          )}
          
          <input
            ref={fileInputRef}
            type="file"
            accept=".pdf,.docx"
            onChange={handleFileChange}
            className="file-input"
          />

          {loading && (
            <div className="progress-container">
              <div className="progress-steps">
                {progressSteps.map((step, index) => (
                  <div 
                    key={step.key} 
                    className={`progress-step ${index <= progressStep ? 'active' : ''} ${index < progressStep ? 'completed' : ''}`}
                  >
                    <div className="step-indicator">
                      {index < progressStep ? '✓' : index + 1}
                    </div>
                    <span className="step-message">{step.message}</span>
                  </div>
                ))}
              </div>
              <div className="progress-bar">
                <div 
                  className="progress-fill"
                  style={{ width: `${((progressStep + 1) / progressSteps.length) * 100}%` }}
                ></div>
              </div>
            </div>
          )}

          <button 
            className="parse-button"
            onClick={handleSubmit}
            disabled={loading || !file}
          >
            {loading ? (
              <>
                <span className="spinner"></span>
                Processing...
              </>
            ) : (
              <>
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                  <path d="M13 10V3L4 14h7v7l9-11h-7z" />
                </svg>
                Parse Resume
              </>
            )}
          </button>
        </section>

        {error && (
          <div className="error-message">
            <span>⚠️</span> {error}
          </div>
        )}

        {result && (
          <div className="results">
            {renderSkills()}
            {renderQuestions()}
            {renderChat()}
          </div>
        )}
      </main>
    </div>
  )
}

export default App
