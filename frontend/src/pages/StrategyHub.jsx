import { useState, useEffect } from 'react';
import { 
  Brain, 
  ChevronDown, 
  ChevronRight, 
  Loader2, 
  AlertTriangle, 
  Target, 
  Users, 
  Lightbulb, 
  Presentation, 
  CheckCircle2, 
  FileText, 
  ArrowLeft, 
  ArrowRight,
  Award,
  TrendingUp,
  Shield,
  Database,
  Upload,
  Play,
  Download
} from 'lucide-react';
import { getBackendUrl } from '../config';

const PHASE_META = {
  1: { label: 'Planning & Processing', icon: <Target size={18} />, color: '#f97316', steps: ['step_1', 'step_2'] },
  2: { label: 'Behavioral Discovery', icon: <Users size={18} />, color: '#8b5cf6', steps: ['step_4', 'step_8'] },
  3: { label: 'Evidence Traceability', icon: <Lightbulb size={18} />, color: '#06b6d4', steps: ['step_13'] },
  4: { label: 'Solution Generation', icon: <Presentation size={18} />, color: '#10b981', steps: ['step_14'] },
};

const renderValue = (value) => {
  if (value === null || value === undefined) return null;
  if (typeof value === 'string') return <p style={{ margin: '0.25rem 0', color: 'var(--text-secondary)', fontSize: '0.9rem', lineHeight: '1.6' }}>{value}</p>;
  if (typeof value === 'number' || typeof value === 'boolean') return <span style={{ color: 'var(--accent-primary)', fontWeight: 'bold' }}>{String(value)}</span>;
  if (Array.isArray(value)) {
    return (
      <ul style={{ margin: '0.5rem 0', paddingLeft: '1.25rem', display: 'flex', flexDirection: 'column', gap: '0.35rem' }}>
        {value.map((item, idx) => (
          <li key={idx} style={{ color: 'var(--text-secondary)', fontSize: '0.85rem', lineHeight: '1.5' }}>
            {typeof item === 'object' ? renderObject(item) : String(item)}
          </li>
        ))}
      </ul>
    );
  }
  if (typeof value === 'object') return renderObject(value);
  return <span>{String(value)}</span>;
};

const formatKey = (key) => key.replace(/_/g, ' ').replace(/\b\w/g, c => c.toUpperCase());

const renderObject = (obj) => {
  if (!obj || typeof obj !== 'object') return null;
  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
      {Object.entries(obj).map(([key, val]) => {
        if (key === 'error') return <p key={key} style={{ color: 'var(--error)', fontStyle: 'italic' }}>{val}</p>;
        return (
          <div key={key}>
            <strong style={{ color: 'var(--text-primary)', fontSize: '0.8rem', textTransform: 'uppercase', letterSpacing: '0.5px', display: 'block', marginBottom: '0.25rem' }}>
              {formatKey(key)}
            </strong>
            {renderValue(val)}
          </div>
        );
      })}
    </div>
  );
};

const StepCard = ({ stepId, stepData, isOpen, onToggle }) => {
  const isFailed = stepData?.status === 'failed';

  return (
    <div style={{
      background: 'var(--bg-secondary)',
      borderRadius: '10px',
      border: `1px solid ${isFailed ? 'rgba(239,68,68,0.3)' : 'var(--border-glass)'}`,
      overflow: 'hidden',
      transition: 'all 0.2s ease',
    }}>
      <button
        onClick={onToggle}
        style={{
          width: '100%',
          display: 'flex',
          alignItems: 'center',
          gap: '0.75rem',
          padding: '1rem 1.25rem',
          background: 'transparent',
          border: 'none',
          cursor: 'pointer',
          textAlign: 'left',
          color: '#fff',
        }}
      >
        {isOpen ? <ChevronDown size={16} /> : <ChevronRight size={16} />}
        <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)', fontFamily: 'monospace' }}>{stepId.replace('_', ' ').toUpperCase()}</span>
        <span style={{ flex: 1, fontSize: '0.95rem', fontWeight: '600' }}>{stepData?.title}</span>
        {isFailed ? (
          <AlertTriangle size={16} color="var(--error)" />
        ) : (
          <CheckCircle2 size={16} color="var(--success)" />
        )}
      </button>
      {isOpen && (
        <div style={{ padding: '0 1.25rem 1.25rem 1.25rem', borderTop: '1px solid var(--border-glass)', textAlign: 'left' }}>
          <div style={{ marginTop: '1rem' }}>
            {stepData?.data ? renderObject(stepData.data) : <p style={{ color: 'var(--text-muted)' }}>No data</p>}
          </div>
        </div>
      )}
    </div>
  );
};

const StrategyHub = () => {
  const [activeTab, setActiveTab] = useState('steps'); // 'steps', 'slides', 'case_study'
  
  // Strategy states
  const [data, setData] = useState(null);
  const [boardPresentation, setBoardPresentation] = useState(null);
  const [currentSlideIndex, setCurrentSlideIndex] = useState(0);
  const [loading, setLoading] = useState(false);
  const [openSteps, setOpenSteps] = useState({});
  const [triggered, setTriggered] = useState(false);

  const [exportLoading, setExportLoading] = useState(false);
  const [exportDocUrl, setExportDocUrl] = useState(null);

  const [exportSlidesLoading, setExportSlidesLoading] = useState(false);
  const [exportSlidesUrl, setExportSlidesUrl] = useState(null);

  const [exportSourceLoading, setExportSourceLoading] = useState(false);

  const [logs, setLogs] = useState([]);
  const [completedSteps, setCompletedSteps] = useState(0);
  const [totalSteps, setTotalSteps] = useState(9);

  // Case study states
  const [caseStudy, setCaseStudy] = useState(null);
  const [caseLoading, setCaseLoading] = useState(true);
  const [analyzing, setAnalyzing] = useState(false);
  const [analysisResult, setAnalysisResult] = useState(null);
  const [uploading, setUploading] = useState(false);
  const [surveyResult, setSurveyResult] = useState(null);
  const [file, setFile] = useState(null);
  const [generatingForm, setGeneratingForm] = useState(false);
  const [generatedFormUrl, setGeneratedFormUrl] = useState(null);

  const toggleStep = (stepId) => {
    setOpenSteps(prev => ({
      ...prev,
      [stepId]: !prev[stepId]
    }));
  };

  const progress = Math.min(100, Math.round((completedSteps / totalSteps) * 100));

  const handleExportDoc = async () => {
    try {
      setExportLoading(true);
      const res = await fetch(`${getBackendUrl()}/api/v2/reports/strategy-deep-dive/export-doc`, {
        method: 'POST'
      });
      const resData = await res.json();
      if (res.ok) {
        setExportDocUrl(resData.doc_url);
      } else {
        alert(resData.detail || "Could not export document.");
      }
    } catch (err) {
      alert("Error exporting document: " + err.message);
    } finally {
      setExportLoading(false);
    }
  };

  const handleExportSlides = async () => {
    try {
      setExportSlidesLoading(true);
      const res = await fetch(`${getBackendUrl()}/api/v2/reports/strategy-deep-dive/export-slides`, {
        method: 'POST'
      });
      const resData = await res.json();
      if (res.ok) {
        setExportSlidesUrl(resData.presentation_url);
      } else {
        alert(resData.detail || "Could not export presentation.");
      }
    } catch (err) {
      alert("Error exporting presentation: " + err.message);
    } finally {
      setExportSlidesLoading(false);
    }
  };

  const handleExportSource = async () => {
    try {
      setExportSourceLoading(true);
      const res = await fetch(`${getBackendUrl()}/api/v2/reports/strategy-deep-dive/export-markdown`);
      const resData = await res.json();
      if (res.ok) {
        const mdContent = resData.markdown_content;
        const blob = new Blob([mdContent], { type: "text/markdown" });
        const href = URL.createObjectURL(blob);
        const link = document.createElement("a");
        link.href = href;
        link.download = "strategy_deep_dive_report.md";
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
        URL.revokeObjectURL(href);
      } else {
        alert(resData.detail || "Could not export presentation source.");
      }
    } catch (err) {
      alert("Error exporting presentation source: " + err.message);
    } finally {
      setExportSourceLoading(false);
    }
  };

  const startPolling = () => {
    const interval = setInterval(async () => {
      try {
        const res = await fetch(`${getBackendUrl()}/api/v2/reports/strategy-deep-dive`);
        const result = await res.json();
        
        if (result.logs) setLogs(result.logs);
        if (result.completed_steps !== undefined) setCompletedSteps(result.completed_steps);
        if (result.total_steps !== undefined) setTotalSteps(result.total_steps);

        if (result.status === 'completed') {
          clearInterval(interval);
          setData(result.result);
          if (result.board_presentation) {
            setBoardPresentation(result.board_presentation);
          }
          setLoading(false);
          setActiveTab('slides');
        } else if (result.status === 'awaiting_survey') {
          clearInterval(interval);
          setData(result.result);
          if (result.board_presentation) {
            setBoardPresentation(result.board_presentation);
          }
          setLoading(false);
        }
      } catch (err) {
        clearInterval(interval);
        setLoading(false);
        console.error('Polling failed:', err);
      }
    }, 2000);
  };

  // Check strategy status on mount
  useEffect(() => {
    const checkStatus = async () => {
      try {
        const res = await fetch(`${getBackendUrl()}/api/v2/reports/strategy-deep-dive`);
        const result = await res.json();
        
        if (result.logs) setLogs(result.logs);
        if (result.completed_steps !== undefined) setCompletedSteps(result.completed_steps);
        if (result.total_steps !== undefined) setTotalSteps(result.total_steps);

        if (result.status === 'completed' || result.status === 'awaiting_survey') {
          setData(result.result);
          if (result.board_presentation) {
            setBoardPresentation(result.board_presentation);
          }
          setTriggered(true);
        } else if (result.status === 'running') {
          setTriggered(true);
          setLoading(true);
          startPolling();
        }
      } catch (err) {
        console.error('Failed to check strategy deep dive status on mount:', err);
      }
    };
    checkStatus();
  }, []);

  // Fetch Case study details when data is present (deep dive completed)
  useEffect(() => {
    if (data) {
      const fetchCaseStudy = async () => {
        try {
          setCaseLoading(true);
          const res = await fetch(`${getBackendUrl()}/api/v2/reports/mvp-case`);
          const data = await res.json();
          setCaseStudy(data);
        } catch (err) {
          console.error('Error fetching MVP case study', err);
        } finally {
          setCaseLoading(false);
        }
      };
      fetchCaseStudy();
    }
  }, [data]);

  const handleRun = async () => {
    setLoading(true);
    setTriggered(true);
    setLogs(["[SYSTEM] Requesting Strategy Deep Dive run in background..."]);
    try {
      const res = await fetch(`${getBackendUrl()}/api/v2/reports/strategy-deep-dive`);
      const result = await res.json();
      
      if (result.logs) setLogs(result.logs);
      
      if (result.status === 'completed') {
        setData(result.result);
        setBoardPresentation(result.board_presentation);
        setLoading(false);
      } else {
        startPolling();
      }
    } catch (err) {
      console.error('Strategy deep dive failed:', err);
      setLoading(false);
    }
  };
  const handleForceRun = async () => {
    if (!window.confirm("Are you sure you want to delete the cached strategy report and execute a fresh Strategy Deep Dive? This will take 5-8 minutes.")) {
      return;
    }
    setLoading(true);
    setTriggered(true);
    setLogs(["[SYSTEM] Deleting cache and requesting fresh Strategy Deep Dive run in background..."]);
    try {
      const res = await fetch(`${getBackendUrl()}/api/v2/reports/strategy-deep-dive/run`, {
        method: 'POST'
      });
      const result = await res.json();
      if (res.ok) {
        setCompletedSteps(0);
        setData(null);
        setBoardPresentation(null);
        startPolling();
      } else {
        alert(result.detail || 'Failed to start fresh run');
        setLoading(false);
      }
    } catch (err) {
      console.error('Force run strategy deep dive failed:', err);
      setLoading(false);
    }
  };


  const handleNextSlide = () => {
    if (boardPresentation && currentSlideIndex < boardPresentation.slides.length - 1) {
      setCurrentSlideIndex(prev => prev + 1);
    }
  };

  const handlePrevSlide = () => {
    if (currentSlideIndex > 0) {
      setCurrentSlideIndex(prev => prev - 1);
    }
  };

  const runDiscoveryAnalysis = async () => {
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

  const handleSurveyUpload = async () => {
    if (!file) return alert('Please select a CSV file first');
    
    setUploading(true);
    const formData = new FormData();
    formData.append('file', file);

    try {
      const res = await fetch(`${getBackendUrl()}/api/v2/surveys/upload`, {
        method: 'POST',
        body: formData
      });
      const data = await res.json();
      if (res.ok) {
        setSurveyResult(data);
        alert("Survey analyzed! Resuming Strategy Deep Dive Phase 2.");
        startPolling();
      } else {
        alert(data.detail || 'Failed to upload');
      }
    } catch (err) {
      console.error(err);
      alert('Error uploading file');
    }
    setUploading(false);
  };

  const handleGenerateForm = async () => {
    if (!data) return alert("Please run the Strategy Deep Dive analysis first to load data.");
    setGeneratingForm(true);
    try {
      const coreProblem = data.steps?.step_1?.data?.core_problem_restatement || "Understanding category exploration barriers";
      const solution = data.steps?.step_14?.data?.innovative?.title || "Cross-sell engine, discovery banners, navigation tabs";
      const description = data.steps?.step_14?.data?.innovative?.description || "Improving category conversion and basket discovery";
      const targetSegment = data.steps?.step_5?.data?.behavioral_factors?.[0]?.factor || "Quick commerce buyers";

      const res = await fetch(`${getBackendUrl()}/api/v2/research/generate-form`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          product_name: "Quick Commerce Platform Ingestion",
          problem_statement: coreProblem,
          product_description: description,
          target_segment: targetSegment,
          key_features: solution,
          assumptions: "Users hesitate to explore non-grocery categories due to trust and quality fears"
        })
      });
      const resData = await res.json();
      if (res.ok) {
        if (resData.form_url) {
          setGeneratedFormUrl(resData.form_url);
        } else {
          alert("Survey generated fallback successfully saved.");
        }
      } else {
        alert(resData.detail || "Failed to generate Google Form.");
      }
    } catch (err) {
      alert("Error generating form: " + err.message);
    } finally {
      setGeneratingForm(false);
    }
  };

  return (
    <div>
      <div className="page-header" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <div>
          <h1 className="page-title text-gradient">Strategy & Case Study</h1>
          <p className="page-subtitle">Formulate, reason, and trace product strategy frameworks and CPO board presentations.</p>
        </div>

        <div style={{ display: 'flex', gap: '1rem', alignItems: 'center' }}>
          {triggered && !loading && (
            <button 
              className="btn-secondary" 
              onClick={handleForceRun}
              style={{ display: 'flex', alignItems: 'center', gap: '0.35rem', color: '#f59e0b', borderColor: '#f59e0b', padding: '0.5rem 1.1rem', fontSize: '0.85rem', cursor: 'pointer', borderRadius: '6px', background: 'rgba(245, 158, 11, 0.05)' }}
            >
              <Play size={14} /> Re-run Deep Dive
            </button>
          )}

          {/* Tab switcher */}
          <div className="glass-panel" style={{ display: 'flex', padding: '0.25rem', borderRadius: '8px', gap: '0.25rem' }}>
            <button 
              onClick={() => setActiveTab('steps')}
              style={{
                padding: '0.5rem 1rem', borderRadius: '6px', border: 'none',
                background: activeTab === 'steps' ? 'var(--accent-primary)' : 'transparent',
                color: activeTab === 'steps' ? '#fff' : 'var(--text-secondary)',
                cursor: 'pointer', fontWeight: '600', transition: 'all 0.2s ease'
              }}
            >
              16-Step Analysis
            </button>
            <button 
              onClick={() => setActiveTab('slides')}
              style={{
                padding: '0.5rem 1rem', borderRadius: '6px', border: 'none',
                background: activeTab === 'slides' ? 'var(--accent-primary)' : 'transparent',
                color: activeTab === 'slides' ? '#fff' : 'var(--text-secondary)',
                cursor: 'pointer', fontWeight: '600', transition: 'all 0.2s ease',
                opacity: boardPresentation ? 1 : 0.5
              }}
              disabled={!boardPresentation}
            >
              Board Presentation (10 Slides)
            </button>
          </div>
        </div>
      </div>

      {/* Export Action Bar (Visible if strategy completed and steps/slides tab is open) */}
      {data && (
        <div style={{ display: 'flex', justifyContent: 'flex-end', gap: '1rem', marginBottom: '1.5rem', flexWrap: 'wrap' }}>
          <button 
            className="btn-primary" 
            onClick={handleGenerateForm} 
            disabled={generatingForm}
            style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', background: 'linear-gradient(135deg, #8b5cf6, #7c3aed)' }}
          >
            {generatingForm ? <Loader2 size={18} style={{ animation: 'spin 1s linear infinite' }} /> : <Upload size={18} />}
            {generatingForm ? 'Generating Form...' : '⚡ Generate Google Form Survey'}
          </button>

          <button 
            className="btn-secondary" 
            onClick={handleExportDoc} 
            disabled={exportLoading}
            style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', cursor: 'pointer', borderRadius: '6px' }}
          >
            {exportLoading ? <Loader2 size={18} style={{ animation: 'spin 1s linear infinite' }} /> : <FileText size={18} />}
            {exportLoading ? 'Exporting Doc...' : '📝 Export Google Doc'}
          </button>

          <button 
            className="btn-secondary" 
            onClick={handleExportSlides} 
            disabled={exportSlidesLoading}
            style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', cursor: 'pointer', borderRadius: '6px' }}
          >
            {exportSlidesLoading ? <Loader2 size={18} style={{ animation: 'spin 1s linear infinite' }} /> : <Presentation size={18} />}
            {exportSlidesLoading ? 'Exporting Slides...' : '📊 Export Google Slides'}
          </button>

          <button 
            className="btn-secondary" 
            onClick={handleExportSource} 
            disabled={exportSourceLoading}
            style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', cursor: 'pointer', borderRadius: '6px' }}
          >
            {exportSourceLoading ? <Loader2 size={18} style={{ animation: 'spin 1s linear infinite' }} /> : <Download size={18} />}
            {exportSourceLoading ? 'Downloading...' : '⬇️ Download Markdown'}
          </button>
        </div>
      )}

      {exportDocUrl && activeTab !== 'case_study' && (
        <div className="glass-panel" style={{ marginBottom: '1.5rem', padding: '1.25rem', background: 'rgba(16, 185, 129, 0.1)', border: '1px solid rgba(16, 185, 129, 0.3)', textAlign: 'left', borderRadius: '8px' }}>
          <h4 style={{ color: 'var(--success)', margin: '0 0 0.4rem 0', display: 'flex', alignItems: 'center', gap: '6px' }}>
            ✅ Google Doc Exported Successfully!
          </h4>
          <p style={{ margin: 0, color: 'var(--text-secondary)', fontSize: '0.9rem' }}>
            Live Google Doc: <a href={exportDocUrl} target="_blank" rel="noopener noreferrer" style={{ color: 'var(--accent-primary)', fontWeight: 'bold' }}>{exportDocUrl}</a>
          </p>
        </div>
      )}

      {exportSlidesUrl && activeTab !== 'case_study' && (
        <div className="glass-panel" style={{ marginBottom: '1.5rem', padding: '1.25rem', background: 'rgba(16, 185, 129, 0.1)', border: '1px solid rgba(16, 185, 129, 0.3)', textAlign: 'left', borderRadius: '8px' }}>
          <h4 style={{ color: 'var(--success)', margin: '0 0 0.4rem 0', display: 'flex', alignItems: 'center', gap: '6px' }}>
            ✅ Google Slides Exported Successfully!
          </h4>
          <p style={{ margin: 0, color: 'var(--text-secondary)', fontSize: '0.9rem' }}>
            Live Presentation: <a href={exportSlidesUrl} target="_blank" rel="noopener noreferrer" style={{ color: 'var(--accent-primary)', fontWeight: 'bold' }}>{exportSlidesUrl}</a>
          </p>
        </div>
      )}

      {generatedFormUrl && (
        <div className="glass-panel" style={{ marginBottom: '1.5rem', padding: '1.25rem', background: 'rgba(139, 92, 246, 0.1)', border: '1px solid rgba(139, 92, 246, 0.3)', textAlign: 'left', borderRadius: '8px' }}>
          <h4 style={{ color: '#a78bfa', margin: '0 0 0.4rem 0', display: 'flex', alignItems: 'center', gap: '6px' }}>
            ✅ Google Form Survey Created Successfully!
          </h4>
          <p style={{ margin: 0, color: 'var(--text-secondary)', fontSize: '0.9rem' }}>
            Live Google Form: <a href={generatedFormUrl} target="_blank" rel="noopener noreferrer" style={{ color: 'var(--accent-primary)', fontWeight: 'bold' }}>{generatedFormUrl}</a>
          </p>
        </div>
      )}

      {/* RENDER STEPS TAB */}
      {activeTab === 'steps' && (
        <>
          {!triggered && (
            <div className="glass-card" style={{ textAlign: 'center', padding: '3rem', maxWidth: '700px', margin: '2rem auto' }}>
              <Brain size={56} color="var(--accent-primary)" style={{ marginBottom: '1.5rem' }} />
              <h2 style={{ color: '#fff', marginBottom: '0.5rem' }}>Ready to Run Deep Strategy Analysis</h2>
              <p style={{ color: 'var(--text-secondary)', marginBottom: '2rem', fontSize: '0.95rem', lineHeight: '1.6' }}>
                This will execute 17 sequential analytical steps (including CPO Board Presentation Synthesis) using your collected signals.
                <br /><br />
                <strong style={{ color: 'var(--warning)' }}>⏱ Estimated time: 5-8 minutes</strong> (due to API rate limit limits between steps)
              </p>
              <button className="btn-primary" onClick={handleRun} style={{ padding: '0.75rem 2rem', fontSize: '1rem', display: 'inline-flex', alignItems: 'center', gap: '0.5rem' }}>
                <Brain size={20} /> Run Strategy Deep Dive
              </button>
            </div>
          )}

          {triggered && (loading || (data && data.steps)) && (
            <>
              <div style={{ marginBottom: '2rem', padding: '0 0.5rem' }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '0.5rem' }}>
                  <span style={{ color: 'var(--text-secondary)', fontSize: '0.85rem' }}>Analysis Progress</span>
                  <span style={{ color: 'var(--accent-primary)', fontWeight: 'bold', fontSize: '0.85rem' }}>
                    {completedSteps}/{totalSteps} steps complete
                  </span>
                </div>
                <div style={{ height: '6px', background: 'var(--bg-secondary)', borderRadius: '3px', overflow: 'hidden' }}>
                  <div style={{ height: '100%', width: `${progress}%`, background: 'linear-gradient(90deg, var(--accent-primary), var(--accent-secondary))', borderRadius: '3px', transition: 'width 0.5s ease' }} />
                </div>
              </div>

              {triggered && logs.length > 0 && (
                <div style={{
                  background: '#121214', color: '#4ade80', fontFamily: 'monospace', padding: '1.25rem', borderRadius: '8px',
                  border: '1px solid var(--border-glass)', maxHeight: '280px', overflowY: 'auto', textAlign: 'left', marginBottom: '2rem',
                  boxShadow: 'inset 0 2px 8px rgba(0, 0, 0, 0.8)', fontSize: '0.85rem', display: 'flex', flexDirection: 'column', gap: '0.35rem'
                }}>
                  <div style={{ color: 'var(--text-muted)', borderBottom: '1px solid rgba(255,255,255,0.05)', paddingBottom: '0.5rem', marginBottom: '0.5rem', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                    <span>🖥️ ANALYSIS ENGINE CONSOLE OUTPUT</span>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
                      <button 
                        onClick={() => {
                          navigator.clipboard.writeText(logs.join('\n'));
                          alert('Console logs copied to clipboard!');
                        }}
                        style={{
                          background: 'rgba(255, 255, 255, 0.08)', border: '1px solid rgba(255, 255, 255, 0.15)',
                          color: '#fff', padding: '2px 8px', borderRadius: '4px', cursor: 'pointer', fontSize: '0.75rem'
                        }}
                      >
                        📋 Copy Logs
                      </button>
                      <span style={{ display: 'flex', alignItems: 'center', gap: '0.25rem', color: loading ? '#f59e0b' : '#10b981' }}>
                        {loading ? (
                          <>
                            <Loader2 size={12} style={{ animation: 'spin 1s linear infinite' }} /> Processing...
                          </>
                        ) : (
                          "✅ Analysis Complete"
                        )}
                      </span>
                    </div>
                  </div>
                  {logs.map((log, index) => (
                    <div key={index} style={{ whiteSpace: 'pre-wrap', lineHeight: '1.4' }}>{log}</div>
                  ))}
                </div>
              )}
            </>
          )}

          {data && data.steps && !loading && (
            <>
              {[1, 2, 3, 4].map(phaseNum => {
                const phase = PHASE_META[phaseNum];
                return (
                  <div key={phaseNum} style={{ marginBottom: '2.5rem' }}>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', marginBottom: '1rem', paddingBottom: '0.5rem', borderBottom: `2px solid ${phase.color}30` }}>
                      <div style={{ background: `${phase.color}20`, padding: '0.4rem', borderRadius: '6px', color: phase.color }}>
                        {phase.icon}
                      </div>
                      <h2 style={{ margin: 0, fontSize: '1.1rem', color: '#fff' }}>Phase {phaseNum}: {phase.label}</h2>
                      <span style={{ marginLeft: 'auto', fontSize: '0.75rem', color: 'var(--text-muted)' }}>
                        {phase.steps.filter(sid => data.steps[sid]?.status === 'complete').length}/{phase.steps.length} steps
                      </span>
                    </div>

                    <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
                      {phase.steps.map(stepId => (
                        data.steps[stepId] ? (
                          <StepCard
                            key={stepId}
                            stepId={stepId}
                            stepData={data.steps[stepId]}
                            isOpen={!!openSteps[stepId]}
                            onToggle={() => toggleStep(stepId)}
                          />
                        ) : null
                      ))}
                    </div>
                  </div>
                );
              })}

              {/* Survey Validation Section after Phase 3 if it's completed */}
              {data.steps?.step_13?.status === 'complete' && (
                <div style={{ marginBottom: '2.5rem', background: 'var(--surface)', padding: '1.5rem', borderRadius: '8px', border: '1px solid #10b98130' }}>
                  <h2 style={{ margin: '0 0 1rem 0', color: '#10b981' }}>User Validation & Survey Integration</h2>
                  <p style={{ color: 'var(--text-muted)', marginBottom: '1.5rem' }}>
                    Phase 1 (Discovery) is complete. To proceed to Phase 2 (Solutioning), upload user survey data (CSV/Excel) to validate our hypotheses.
                  </p>
                  
                  <div style={{ display: 'flex', gap: '1rem', alignItems: 'center', marginBottom: '1.5rem' }}>
                    <input 
                      type="file" 
                      accept=".csv, .xlsx, .xls"
                      onChange={(e) => setFile(e.target.files[0])}
                      style={{ color: 'var(--text-main)', background: 'var(--surface-light)', padding: '0.5rem', borderRadius: '4px', border: '1px solid var(--border)' }}
                    />
                    <button 
                      className="btn-primary" 
                      onClick={handleSurveyUpload}
                      disabled={uploading || !file}
                    >
                      {uploading ? <Loader2 size={16} style={{ animation: 'spin 1s linear infinite' }} /> : <Upload size={16} />}
                      Analyze Survey Responses
                    </button>
                  </div>

                  {data.survey_validation && (
                    <div style={{ background: 'var(--surface-light)', padding: '1rem', borderRadius: '6px', borderLeft: '4px solid #10b981' }}>
                      <h3 style={{ margin: '0 0 0.5rem 0', color: '#fff' }}>Validation Complete!</h3>
                      <p style={{ color: 'var(--text-main)', margin: '0 0 1rem 0' }}>{data.survey_validation.updated_problem_statement}</p>
                      
                      <div style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
                        {data.survey_validation.validation_matrix?.map((item, i) => (
                          <div key={i} style={{ background: 'var(--surface)', padding: '0.75rem', borderRadius: '4px', display: 'flex', flexDirection: 'column', gap: '0.25rem' }}>
                            <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                              <strong style={{ color: '#fff' }}>Insight:</strong>
                              <span style={{ 
                                color: item.status === 'Confirmed' ? '#10b981' : item.status === 'Contradicted' ? '#ef4444' : '#3b82f6',
                                fontWeight: 'bold'
                              }}>
                                {item.status}
                              </span>
                            </div>
                            <span style={{ color: 'var(--text-muted)' }}>{item.original_insight}</span>
                            <span style={{ color: 'var(--text-main)', fontSize: '0.9rem' }}>↳ {item.survey_evidence}</span>
                          </div>
                        ))}
                      </div>
                    </div>
                  )}
                </div>
              )}


            </>
          )}
        </>
      )}

      {/* RENDER BOARD SLIDES TAB */}
      {activeTab === 'slides' && boardPresentation && boardPresentation.slides && (
        <div className="grid-2" style={{ gridTemplateColumns: '7fr 3fr', gap: '2rem' }}>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
            <div className="glass-panel" style={{ 
              minHeight: '440px', background: 'linear-gradient(135deg, #0b1329, #14213d)', border: `2px solid rgba(255,255,255,0.08)`, 
              borderRadius: '16px', padding: '2.5rem', display: 'flex', flexDirection: 'column', position: 'relative',
              boxShadow: '0 15px 35px rgba(0,0,0,0.6)', textAlign: 'left', overflow: 'hidden'
            }}>
              <div style={{ position: 'absolute', top: '12px', right: '20px', display: 'flex', alignItems: 'center', gap: '6px' }}>
                <span style={{ width: '8px', height: '8px', borderRadius: '50%', background: boardPresentation.primary_color || '#3b82f6' }}></span>
                <span style={{ fontSize: '0.7rem', color: '#94a3b8', textTransform: 'uppercase', letterSpacing: '1px', fontWeight: 'bold' }}>
                  {boardPresentation.presentation_theme || 'BOARD STUDY'}
                </span>
              </div>

              <div style={{ flex: 1, display: 'flex', flexDirection: 'column', justifyContent: 'center' }}>
                {(() => {
                  const activeSlide = boardPresentation.slides[currentSlideIndex];
                  if (!activeSlide) return null;
                  const skipKeys = ["title", "headline", "slide_number", "type", "speaker_notes"];
                  const entries = Object.entries(activeSlide).filter(([k]) => !skipKeys.includes(k));
                  const brandColor = boardPresentation.primary_color || '#3b82f6';
                  
                  return (
                    <div style={{ display: 'grid', gridTemplateColumns: '1.2fr 1fr', gap: '1.5rem', height: '100%', overflowY: 'auto' }}>
                      <div style={{ display: 'flex', flexDirection: 'column', justifyContent: 'center', gap: '1rem' }}>
                        <span style={{ fontSize: '0.8rem', color: brandColor, textTransform: 'uppercase', letterSpacing: '2px', fontWeight: 'bold' }}>
                          Slide {activeSlide.slide_number}: {activeSlide.title}
                        </span>
                        <h2 style={{ fontSize: '1.75rem', color: '#fff', margin: 0, fontWeight: '800', lineHeight: '1.2' }}>
                          {activeSlide.headline}
                        </h2>
                      </div>
                      <div style={{ display: 'flex', flexDirection: 'column', gap: '0.65rem', overflowY: 'auto', maxHeight: '330px', paddingRight: '0.5rem' }}>
                        {entries.slice(0, 4).map(([key, val]) => {
                          const label = key.replace(/_/g, ' ').replace(/\b\w/g, c => c.toUpperCase());
                          return (
                            <div key={key} style={{ 
                              background: 'rgba(255,255,255,0.02)', padding: '0.6rem 0.8rem', borderRadius: '8px', 
                              border: `1px solid rgba(255,255,255,0.05)`, borderLeft: `3px solid ${brandColor}`
                            }}>
                              <strong style={{ color: '#fff', fontSize: '0.7rem', textTransform: 'uppercase', display: 'block', marginBottom: '0.15rem' }}>{label}</strong>
                              {renderValue(val)}
                            </div>
                          );
                        })}
                      </div>
                    </div>
                  );
                })()}
              </div>

              <div style={{ display: 'flex', justifyContent: 'space-between', borderTop: `1px solid rgba(255,255,255,0.08)`, paddingTop: '0.75rem', marginTop: '1rem', fontSize: '0.75rem', color: '#64748b' }}>
                <span>Pulse Intelligence — CPO Board Presentation</span>
                <span>McKinsey Storytelling Flow</span>
              </div>
            </div>

            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginTop: '0.5rem' }}>
              <button className="btn-secondary" onClick={handlePrevSlide} disabled={currentSlideIndex === 0}>
                <ArrowLeft size={16} /> Back
              </button>
              <span style={{ color: 'var(--text-secondary)', fontSize: '0.9rem' }}>
                Slide {currentSlideIndex + 1} / {boardPresentation.slides.length}
              </span>
              <button className="btn-secondary" onClick={handleNextSlide} disabled={currentSlideIndex === boardPresentation.slides.length - 1}>
                Next <ArrowRight size={16} />
              </button>
            </div>
          </div>

          <div className="glass-panel" style={{ background: '#090e18', border: '1px solid #1e293b', borderRadius: '12px', padding: '1.5rem', display: 'flex', flexDirection: 'column', gap: '1.25rem', height: 'fit-content', textAlign: 'left' }}>
            <h3 style={{ borderBottom: '1px solid #1e293b', paddingBottom: '0.5rem', color: '#fff', fontSize: '1.1rem', margin: 0 }}>
              🎙️ Presenter Speaker Notes
            </h3>
            <div style={{ display: 'flex', flexDirection: 'column', gap: '1.25rem', fontSize: '0.9rem', overflowY: 'auto', maxHeight: '420px' }}>
              {boardPresentation.slides[currentSlideIndex]?.speaker_notes ? (
                <p style={{ color: '#cbd5e1', margin: 0, lineHeight: '1.4', fontStyle: 'italic' }}>
                  "{boardPresentation.slides[currentSlideIndex].speaker_notes}"
                </p>
              ) : (
                <p style={{ color: 'var(--text-muted)' }}>No presenter notes compiled.</p>
              )}
            </div>
          </div>
        </div>
      )}
      <style>{`@keyframes spin { from { transform: rotate(0deg); } to { transform: rotate(360deg); } }`}</style>
    </div>
  );
};

export default StrategyHub;
