import React from 'react'
import ReactDOM from 'react-dom/client'
import App from './App.tsx'
import './index.css'

class ErrorBoundary extends React.Component<{children: React.ReactNode}, {hasError: boolean, error: any}> {
  constructor(props: any) {
    super(props)
    this.state = { hasError: false, error: null }
  }
  static getDerivedStateFromError(error: any) {
    return { hasError: true, error }
  }
  componentDidCatch(error: any, errorInfo: any) {
    console.error("Interface Error:", error, errorInfo)
  }
  render() {
    if (this.state.hasError) {
      return (
        <div style={{ background: '#020617', color: '#f87171', minHeight: '100vh', padding: 40, fontFamily: 'monospace' }}>
          <h1 style={{ color: '#ef4444', fontSize: 24 }}>⚠️ Interface Recovered</h1>
          <pre style={{ background: '#0f172a', padding: 16, borderRadius: 8, border: '1px solid #334155' }}>
            {String(this.state.error?.stack || this.state.error)}
          </pre>
          <button onClick={() => window.location.reload()} style={{ marginTop: 20, padding: '10px 20px', background: '#38bdf8', color: '#000', border: 'none', borderRadius: 6, cursor: 'pointer', fontWeight: 'bold' }}>
            🔄 Reload Interface
          </button>
        </div>
      )
    }
    return this.props.children
  }
}

ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <ErrorBoundary>
      <App />
    </ErrorBoundary>
  </React.StrictMode>,
)
