import React, { useState } from 'react';
import './App.css';

function App() {
  const [formData, setFormData] = useState({
    app_store_id: '',
    play_store_package: '',
    from_date: '2024-01-01',
    to_date: '2024-03-01',
    lang: 'en',
    min_word_count: 5,
    include_emojis: true
  });

  const [loading, setLoading] = useState(false);
  const [report, setReport] = useState(null);
  const [error, setError] = useState('');

  const handleInputChange = (e) => {
    const { name, value, type, checked } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: type === 'checkbox' ? checked : value
    }));
  };

  const generateReport = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');
    setReport(null);

    try {
      const response = await fetch('http://localhost:8000/api/generate-report', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(formData)
      });
      
      const data = await response.json();
      if (!response.ok) throw new Error(data.detail || 'Failed to generate report');
      
      if (data.status === 'empty') {
        setError(data.message);
      } else {
        setReport({
          themes: data.data,
          rawCount: data.raw_count,
          filteredCount: data.filtered_count,
          llmCount: data.llm_count,
          warning: data.warning
        });
      }
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const pushToMcp = async (teamCategory = null) => {
    try {
      const target = teamCategory || 'All Teams';
      alert(`Pushing ${target} report to Google Docs and Gmail MCP...`);
      
      const appName = formData.play_store_package || formData.app_store_id || 'Unknown App';
      const response = await fetch('http://localhost:8000/api/mcp-push', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          app_name: appName,
          report_data: report.themes,
          team_category: teamCategory
        })
      });
      
      const data = await response.json();
      if (response.ok) {
        alert('MCP Push Successful! Docs URL: ' + data.docs_response.doc_url);
      } else {
        throw new Error(data.detail);
      }
    } catch (err) {
      alert('MCP Push Failed: ' + err.message);
    }
  };

  // Group report by teams
  const groupedThemes = report?.themes ? report.themes.reduce((acc, theme) => {
    const team = theme.team_category || 'General Team';
    if (!acc[team]) acc[team] = [];
    acc[team].push(theme);
    return acc;
  }, {}) : {};

  return (
    <div className="container">
      <header className="header">
        <h1>Review Analyzer</h1>
        <p>AI-powered insights from public App Store and Google Play reviews.</p>
      </header>

      <main>
        <div className="form-card">
          <form onSubmit={generateReport}>
            <div className="form-grid">
              <div className="input-group">
                <label>Play Store Package Name (e.g., com.groww.app)</label>
                <input type="text" name="play_store_package" value={formData.play_store_package} onChange={handleInputChange} placeholder="com.example.app" />
              </div>
              <div className="input-group">
                <label>App Store ID (e.g., 123456789)</label>
                <input type="text" name="app_store_id" value={formData.app_store_id} onChange={handleInputChange} placeholder="123456789" />
              </div>
              
              <div className="input-group">
                <label>From Date (YYYY-MM-DD)</label>
                <input type="date" name="from_date" value={formData.from_date} onChange={handleInputChange} required />
              </div>
              <div className="input-group">
                <label>To Date (YYYY-MM-DD)</label>
                <input type="date" name="to_date" value={formData.to_date} onChange={handleInputChange} required />
              </div>


              <div className="input-group">
                <label>Minimum Word Count</label>
                <input type="number" name="min_word_count" min="0" max="100" value={formData.min_word_count} onChange={handleInputChange} />
              </div>

              <div className="input-group" style={{ justifyContent: 'center' }}>
                <label className="checkbox-group">
                  <input type="checkbox" name="include_emojis" checked={formData.include_emojis} onChange={handleInputChange} />
                  Include reviews with Emojis
                </label>
              </div>
            </div>

            <div style={{ marginTop: '2rem', textAlign: 'right' }}>
              <button type="submit" className="btn" disabled={loading}>
                {loading ? <><span className="loader"></span> Processing (approx 1 min)...</> : 'Generate Report'}
              </button>
            </div>
          </form>
        </div>

        {error && (
          <div className="form-card" style={{ borderColor: 'var(--danger)', color: 'var(--danger)' }}>
            <strong>Error: </strong> {error}
          </div>
        )}

        {report && (
          <div className="report-card">
            
            <div className="stats-banner">
              <div className="stat-box">
                <div className="stat-value purple">{report.rawCount}</div>
                <div className="stat-label">Total Scraped</div>
              </div>
              <div className="stat-box">
                <div className="stat-value green">{report.filteredCount}</div>
                <div className="stat-label">Passed Filters</div>
              </div>
              <div className="stat-box">
                <div className="stat-value blue">{report.llmCount}</div>
                <div className="stat-label">Centroids Analyzed</div>
              </div>
            </div>

            {report.warning && (
              <div className="alert-warning">
                <strong>⚠️ Note:</strong> {report.warning}
              </div>
            )}

            <h2 style={{ borderBottom: '1px solid var(--border)', paddingBottom: '1rem', marginBottom: '2rem' }}>
              Insight Report Generated Successfully
            </h2>

            {Object.keys(groupedThemes).map(team => (
              <div key={team} style={{ marginBottom: '3rem' }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1rem' }}>
                  <h3 style={{ color: 'var(--success)' }}>{team}</h3>
                  <button className="btn" style={{ padding: '0.5rem 1rem', fontSize: '0.85rem' }} onClick={() => pushToMcp(team)}>
                    Push only to {team} MCP
                  </button>
                </div>

                {groupedThemes[team].map((theme, idx) => (
                  <div key={idx} className="theme-card">
                    <div className="theme-header">
                      <h4 className="theme-title">{theme.title}</h4>
                      <span className="team-badge">{theme.team_category}</span>
                    </div>
                    <p style={{ margin: '0 0 1rem 0' }}>{theme.summary}</p>
                    
                    <div className="quote-box">
                      "{theme.quote}"
                    </div>

                    <div className="action-ideas">
                      <strong>Actionable Ideas:</strong>
                      <ul>
                        {Array.isArray(theme.action_ideas) 
                          ? theme.action_ideas.map((idea, i) => <li key={i}>{idea}</li>)
                          : <li>{theme.action_ideas}</li>
                        }
                      </ul>
                    </div>
                  </div>
                ))}
              </div>
            ))}

            <div className="mcp-actions">
              <button className="btn btn-success" style={{ width: '100%' }} onClick={() => pushToMcp(null)}>
                Final Push: Send Entire Report to Google Docs & All Emails
              </button>
            </div>
          </div>
        )}
      </main>
    </div>
  );
}

export default App;
