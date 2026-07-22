import { useState, useEffect } from 'react';
import { Award, CheckCircle, TrendingUp, HelpCircle, Shield, ListTodo, FileText, ArrowRight, Play, Database, Upload, CheckCircle2 } from 'lucide-react';
import { getBackendUrl } from '../config';

const CaseStudy = () => {
  const [activeTab, setActiveTab] = useState('mvp'); // 'mvp' or 'blinkit'
  
  // General MVP Case States
  const [caseStudy, setCaseStudy] = useState(null);
  const [mvpLoading, setMvpLoading] = useState(true);

  // Blinkit Case States
  const [analyzing, setAnalyzing] = useState(false);
  const [analysisResult, setAnalysisResult] = useState(null);
  const [uploading, setUploading] = useState(false);
  const [surveyResult, setSurveyResult] = useState(null);
  const [file, setFile] = useState(null);

  useEffect(() => {
    if (activeTab === 'mvp') {
      const fetchCaseStudy = async () => {
        try {
          setMvpLoading(true);
          const res = await fetch(`${getBackendUrl()}/api/v2/reports/mvp-case`);
          const data = await res.json();
          setCaseStudy(data);
        } catch (err) {
          console.error('Error fetching MVP case study', err);
        } finally {
          setMvpLoading(false);
        }
      };
      fetchCaseStudy();
    }
  }, [activeTab]);

  const runBlinkitAnalysis = async () => {
    setAnalyzing(true);
    try {
      const res = await fetch(`${getBackendUrl()}/api/v2/blinkit/analyze`, { method: 'POST' });
      const data = await res.json();
      if (res.ok) {
        setAnalysisResult(data);
      } else {
        alert(data.detail || 'Failed to analyze');
      }
    } catch (err) {
      console.error(err);
      alert('Error connecting to backend');
    }
    setAnalyzing(false);
  };

  const handleBlinkitUpload = async () => {
    if (!file) return alert('Please select a CSV file first');
    
    setUploading(true);
    const formData = new FormData();
    formData.append('file', file);

    try {
      const res = await fetch(`${getBackendUrl()}/api/v2/blinkit/upload-survey`, {
        method: 'POST',
        body: formData
      });
      const data = await res.json();
      if (res.ok) {
        setSurveyResult(data);
      } else {
        alert(data.detail || 'Failed to upload');
      }
    } catch (err) {
      console.error(err);
      alert('Error uploading file');
    }
    setUploading(false);
  };

  return (
    <div>
      <div className="page-header" style={{ textAlign: 'left', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <div>
          <h1 className="page-title text-gradient">Case Studies</h1>
          <p className="page-subtitle">Formulate and trace PM business cases, solution prioritizations, and customer discovery insights.</p>
        </div>
        
        {/* Tab Selector */}
        <div className="glass-panel" style={{ display: 'flex', padding: '0.25rem', borderRadius: '8px', gap: '0.25rem' }}>
          <button 
            onClick={() => setActiveTab('mvp')}
            style={{
              padding: '0.5rem 1rem',
              borderRadius: '6px',
              border: 'none',
              background: activeTab === 'mvp' ? 'var(--accent-primary)' : 'transparent',
              color: activeTab === 'mvp' ? '#fff' : 'var(--text-secondary)',
              cursor: 'pointer',
              fontWeight: '600',
              transition: 'all 0.2s ease'
            }}
          >
            MVP Case Study
          </button>
          <button 
            onClick={() => setActiveTab('blinkit')}
            style={{
              padding: '0.5rem 1rem',
              borderRadius: '6px',
              border: 'none',
              background: activeTab === 'blinkit' ? 'var(--accent-primary)' : 'transparent',
              color: activeTab === 'blinkit' ? '#fff' : 'var(--text-secondary)',
              cursor: 'pointer',
              fontWeight: '600',
              transition: 'all 0.2s ease'
            }}
          >
            Blinkit Cross-Sell
          </button>
        </div>
      </div>

      {/* MVP CASE STUDY CONTENT */}
      {activeTab === 'mvp' && (
        <>
          {mvpLoading ? (
            <div className="flex-center" style={{ height: '50vh', display: 'flex', justifyContent: 'center', alignItems: 'center', flexDirection: 'column', gap: '1rem' }}>
              <div className="loader" style={{ width: '40px', height: '40px', borderColor: 'rgba(99, 102, 241, 0.3)', borderTopColor: 'var(--accent-primary)' }}></div>
              <p style={{ color: 'var(--text-secondary)' }}>Compiling MVP Business Case Study...</p>
            </div>
          ) : !caseStudy || caseStudy.error ? (
            <div className="glass-card" style={{ textAlign: 'center', padding: '3rem', margin: '2rem auto', maxWidth: '600px' }}>
              <Shield size={48} color="var(--warning)" style={{ marginBottom: '1rem' }} />
              <h3>Business Case Study not ready</h3>
              <p style={{ color: 'var(--text-muted)', marginBottom: '1.5rem' }}>
                No collected intelligence dataset found. Please run the Intelligence Pipeline on the <strong>Overview</strong> tab to populate MVP business case metrics.
              </p>
            </div>
          ) : (
            <div className="grid-2" style={{ gridTemplateColumns: '7fr 5fr', gap: '2rem', textAlign: 'left' }}>
              <div style={{ display: 'flex', flexDirection: 'column', gap: '2rem' }}>
                {/* MVP Selection Banner */}
                <div className="glass-panel" style={{ borderLeft: '4px solid var(--accent-primary)', padding: '2rem' }}>
                  <span style={{ fontSize: '0.8rem', color: 'var(--accent-primary)', fontWeight: 'bold', textTransform: 'uppercase' }}>
                    Selected Product MVP
                  </span>
                  <h2 style={{ fontSize: '1.85rem', color: '#fff', margin: '0.25rem 0 0.75rem 0' }}>{caseStudy.mvp_title}</h2>
                  <p style={{ fontSize: '1.1rem', color: 'var(--text-primary)', margin: 0, fontStyle: 'italic' }}>
                    "{caseStudy.core_value_prop}"
                  </p>
                  <div style={{ marginTop: '1rem', display: 'flex', gap: '0.5rem', alignItems: 'center' }}>
                    <span className="badge badge-info">Target Profile: {caseStudy.target_persona}</span>
                  </div>
                </div>

                {/* Rationale & Evidence */}
                <div className="glass-card" style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
                  <h3 style={{ margin: 0, color: '#fff', display: 'flex', alignItems: 'center', gap: '8px' }}>
                    <FileText size={20} color="var(--accent-secondary)" /> Problem Context & Evidence
                  </h3>
                  <p style={{ fontSize: '0.9rem', color: 'var(--text-secondary)', lineHeight: '1.5', margin: 0 }}>
                    {caseStudy.problem_context}
                  </p>

                  <h3 style={{ margin: '1rem 0 0 0', color: '#fff', display: 'flex', alignItems: 'center', gap: '8px' }}>
                    <Award size={20} color="var(--accent-tertiary)" /> Why This MVP? (PM Justification)
                  </h3>
                  <p style={{ fontSize: '0.9rem', color: 'var(--text-secondary)', lineHeight: '1.5', margin: 0 }}>
                    {caseStudy.why_chosen_rationale}
                  </p>
                </div>

                {/* RICE Prioritization Table */}
                <div className="glass-card" style={{ padding: 0, overflowX: 'auto' }}>
                  <div style={{ padding: '1.25rem 1.5rem', borderBottom: '1px solid var(--border-glass)' }}>
                    <h3 style={{ margin: 0, color: '#fff' }}>RICE Prioritization Matrix</h3>
                  </div>
                  <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: '0.9rem' }}>
                    <thead>
                      <tr style={{ background: 'rgba(255,255,255,0.02)', borderBottom: '1px solid var(--border-glass)' }}>
                        <th style={{ padding: '0.75rem 1rem', textAlign: 'left', color: 'var(--text-secondary)' }}>Opportunity Solution</th>
                        <th style={{ padding: '0.75rem 1rem', textAlign: 'center', color: 'var(--text-secondary)' }}>Reach (R)</th>
                        <th style={{ padding: '0.75rem 1rem', textAlign: 'center', color: 'var(--text-secondary)' }}>Impact (I)</th>
                        <th style={{ padding: '0.75rem 1rem', textAlign: 'center', color: 'var(--text-secondary)' }}>Confidence (C)</th>
                        <th style={{ padding: '0.75rem 1rem', textAlign: 'center', color: 'var(--text-secondary)' }}>Effort (E)</th>
                        <th style={{ padding: '0.75rem 1rem', textAlign: 'center', color: 'var(--text-secondary)' }}>RICE Score</th>
                      </tr>
                    </thead>
                    <tbody>
                      {caseStudy.rice_matrix?.map((row, idx) => (
                        <tr key={idx} style={{ borderBottom: '1px solid var(--border-glass)' }}>
                          <td style={{ padding: '0.75rem 1rem', fontWeight: '500', color: '#fff' }}>{row.solution}</td>
                          <td style={{ padding: '0.75rem 1rem', textAlign: 'center' }}>{row.reach}</td>
                          <td style={{ padding: '0.75rem 1rem', textAlign: 'center' }}>{row.impact}</td>
                          <td style={{ padding: '0.75rem 1rem', textAlign: 'center' }}>{row.confidence}%</td>
                          <td style={{ padding: '0.75rem 1rem', textAlign: 'center' }}>{row.effort}</td>
                          <td style={{ padding: '0.75rem 1rem', textAlign: 'center', fontWeight: 'bold', color: 'var(--accent-primary)' }}>{Math.round(row.score)}</td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>

              {/* Sidebar Info */}
              <div style={{ display: 'flex', flexDirection: 'column', gap: '2rem' }}>
                <div className="glass-card" style={{ display: 'flex', flexDirection: 'column', gap: '1.25rem' }}>
                  <h3 style={{ margin: 0, color: '#fff', display: 'flex', alignItems: 'center', gap: '8px' }}>
                    <TrendingUp size={20} color="var(--success)" /> Success Indicators & KPIs
                  </h3>
                  
                  {caseStudy.kpis?.map((kpi, idx) => (
                    <div key={idx} style={{ paddingBottom: '1rem', borderBottom: idx < caseStudy.kpis.length - 1 ? '1px solid var(--border-glass)' : 'none' }}>
                      <strong style={{ display: 'block', color: 'var(--text-primary)', fontSize: '0.95rem' }}>{kpi.metric}</strong>
                      <span style={{ fontSize: '0.85rem', color: 'var(--text-muted)' }}>Target: {kpi.target}</span>
                      <p style={{ fontSize: '0.85rem', color: 'var(--text-secondary)', margin: '0.25rem 0 0 0' }}>{kpi.justification}</p>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          )}
        </>
      )}

      {/* BLINKIT CROSS-SELL CONTENT */}
      {activeTab === 'blinkit' && (
        <div className="grid grid-2" style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '2rem', textAlign: 'left' }}>
          {/* Step 1: Scraped Data Analysis */}
          <div className="card glass-panel" style={{ padding: '1.5rem' }}>
            <h3 style={{ display: 'flex', alignItems: 'center', gap: '8px', color: '#fff', marginBottom: '1rem' }}>
              <Database size={20} color="var(--accent-primary)" /> 1. Public Signals Analysis
            </h3>
            <p style={{ fontSize: '0.9rem', color: 'var(--text-secondary)' }}>
              Run the AI filter on Blinkit App Store and Reddit reviews to extract cross-sell exploration barriers.
            </p>
            <button 
              className="btn-primary" 
              onClick={runBlinkitAnalysis} 
              disabled={analyzing}
              style={{ marginTop: '1.5rem', width: '100%', display: 'flex', justifyContent: 'center', alignItems: 'center', gap: '0.5rem' }}
            >
              {analyzing ? 'Analyzing...' : <><Play size={16}/> Run AI Discovery Engine</>}
            </button>
            
            {analysisResult && (
              <div style={{ marginTop: '2rem', padding: '1.25rem', background: 'rgba(255,255,255,0.02)', border: '1px solid var(--border-glass)', borderRadius: '8px' }}>
                <h4 style={{ display: 'flex', alignItems: 'center', gap: '6px', color: 'var(--success)', margin: '0 0 0.5rem 0' }}>
                  <CheckCircle2 size={16} /> Analysis Success
                </h4>
                <p style={{ fontSize: '0.9rem', color: 'var(--text-secondary)' }}>
                  Filtered down to <strong>{analysisResult.filtered_count}</strong> high-signal insights.
                </p>
                
                <h5 style={{ marginTop: '1rem', color: '#fff' }}>Root Causes Found:</h5>
                <ul style={{ paddingLeft: '1.25rem', margin: '0.5rem 0 0 0', fontSize: '0.85rem', color: 'var(--text-secondary)' }}>
                  {analysisResult.insights?.root_causes?.map((cause, i) => (
                    <li key={i} style={{ marginBottom: '0.5rem' }}>
                      <strong>{cause.cause}</strong>: {cause.description}
                    </li>
                  ))}
                </ul>
              </div>
            )}
          </div>

          {/* Step 2: Primary Research Synthesis */}
          <div className="card glass-panel" style={{ padding: '1.5rem' }}>
            <h3 style={{ display: 'flex', alignItems: 'center', gap: '8px', color: '#fff', marginBottom: '1rem' }}>
              <Upload size={20} color="var(--accent-secondary)" /> 2. Primary Research Synthesis
            </h3>
            <p style={{ fontSize: '0.9rem', color: 'var(--text-secondary)' }}>
              Upload Google Form survey CSV file to synthesize and update the strategic problem statement.
            </p>
            
            <div style={{ margin: '1.5rem 0', display: 'flex', gap: '0.5rem' }}>
              <input 
                type="file" 
                accept=".csv"
                onChange={(e) => setFile(e.target.files[0])}
                style={{
                  flex: 1,
                  padding: '0.5rem',
                  background: 'rgba(0,0,0,0.2)',
                  border: '1px solid var(--border-glass)',
                  borderRadius: '6px',
                  color: '#fff',
                  fontSize: '0.85rem'
                }}
              />
              <button 
                className="btn-primary" 
                onClick={handleBlinkitUpload}
                disabled={uploading}
              >
                {uploading ? 'Uploading...' : 'Upload'}
              </button>
            </div>
            
            {surveyResult && (
              <div style={{ marginTop: '2rem', padding: '1.25rem', background: 'rgba(255,255,255,0.02)', border: '1px solid var(--border-glass)', borderRadius: '8px' }}>
                <h4 style={{ display: 'flex', alignItems: 'center', gap: '6px', color: 'var(--success)', margin: '0 0 0.5rem 0' }}>
                  <CheckCircle2 size={16} /> Synthesis Completed
                </h4>
                <p style={{ fontSize: '0.85rem', color: 'var(--text-secondary)' }}>
                  Problem statement updated successfully inside <strong>docs/Blinkit_Cross_Sell_Growth/problem_statement.md</strong>.
                </p>
                <div style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem', marginTop: '1rem' }}>
                  <div style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>SYNTHESIZED METRICS:</div>
                  <div style={{ fontSize: '0.85rem', color: 'var(--text-primary)' }}>
                    • Sample Size: <strong>{surveyResult.sample_size}</strong> respondents
                  </div>
                  <div style={{ fontSize: '0.85rem', color: 'var(--text-primary)' }}>
                    • Core Insight: <strong>{surveyResult.top_insight}</strong>
                  </div>
                </div>
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
};

export default CaseStudy;
