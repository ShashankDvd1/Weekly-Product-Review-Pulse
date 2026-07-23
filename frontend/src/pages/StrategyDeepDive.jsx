import { useState, useEffect } from 'react';
import { Brain, ChevronDown, ChevronRight, Loader2, AlertTriangle, Target, Users, Lightbulb, Presentation, CheckCircle2, FileText, ArrowLeft, ArrowRight, Download } from 'lucide-react';
import { getBackendUrl } from '../config';

const PHASE_META = {
  1: { label: 'Problem Discovery', icon: <Target size={18} />, color: '#f97316', steps: ['step_1', 'step_2', 'step_3', 'step_4'] },
  2: { label: 'Behavioral & Market Analysis', icon: <Users size={18} />, color: '#8b5cf6', steps: ['step_5', 'step_6', 'step_7', 'step_8', 'step_9'] },
  3: { label: 'Strategic Opportunity', icon: <Lightbulb size={18} />, color: '#06b6d4', steps: ['step_10', 'step_11', 'step_12', 'step_13'] },
  4: { label: 'Solutions & Presentation', icon: <Presentation size={18} />, color: '#10b981', steps: ['step_14', 'step_15', 'step_16'] },
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

const StrategyDeepDive = () => {
  const [data, setData] = useState(null);
  const [boardPresentation, setBoardPresentation] = useState(null);
  const [activeTab, setActiveTab] = useState('steps');
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
  const [totalSteps, setTotalSteps] = useState(17);

  const handleExportDoc = async () => {
    try {
      setExportLoading(true);
      const res = await fetch(`${getBackendUrl()}/api/v2/reports/strategy-deep-dive/export-doc`, {
        method: 'POST'
      });
      const resData = await res.json();
      if (resData.doc_url) {
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
      if (resData.presentation_url) {
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
      const res = await fetch(`${getBackendUrl()}/api/v2/reports/strategy-deep-dive/export-source`);
      const resData = await res.json();
      if (res.ok) {
        const jsonStr = JSON.stringify(resData.source_json, null, 2);
        const blob = new Blob([jsonStr], { type: "application/json" });
        const href = URL.createObjectURL(blob);
        const link = document.createElement("a");
        link.href = href;
        link.download = "executive_presentation_source.json";
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
          setBoardPresentation(result.board_presentation);
          setLoading(false);
        } else if (result.status === 'failed') {
          clearInterval(interval);
          setLoading(false);
          alert("Strategy deep dive analysis failed. Check console.");
        }
      } catch (err) {
        clearInterval(interval);
        setLoading(false);
        console.error('Polling failed:', err);
      }
    }, 2000);
  };

  useEffect(() => {
    const checkStatus = async () => {
      try {
        const res = await fetch(`${getBackendUrl()}/api/v2/reports/strategy-deep-dive`);
        const result = await res.json();
        
        if (result.logs) setLogs(result.logs);
        if (result.completed_steps !== undefined) setCompletedSteps(result.completed_steps);
        if (result.total_steps !== undefined) setTotalSteps(result.total_steps);

        if (result.status === 'completed') {
          setData(result.result);
          setBoardPresentation(result.board_presentation);
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

  const toggleStep = (stepId) => {
    setOpenSteps(prev => ({ ...prev, [stepId]: !prev[stepId] }));
  };

  const progress = totalSteps > 0 ? (completedSteps / totalSteps) * 100 : 0;

  return (
    <div>
      <div className="page-header" style={{ textAlign: 'left', display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: '1rem' }}>
        <div>
          <h1 className="page-title text-gradient" style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
            <Brain size={32} /> Strategy Deep Dive
          </h1>
          <p className="page-subtitle">
            A 16-step Principal PM / Strategy Consultant analysis framework applying first-principles thinking, behavioral science, and competitive strategy.
          </p>
        </div>
        {data && data.steps && (
          <div style={{ display: 'flex', gap: '0.75rem' }}>
            <button 
              className="btn-primary" 
              onClick={handleExportDoc} 
              disabled={exportLoading}
              style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}
            >
              {exportLoading ? <Loader2 size={18} style={{ animation: 'spin 1s linear infinite' }} /> : <FileText size={18} />}
              {exportLoading ? 'Generating Doc...' : 'Export to Google Doc'}
            </button>
            <button 
              className="btn-primary" 
              onClick={handleExportSlides} 
              disabled={exportSlidesLoading}
              style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', background: 'linear-gradient(135deg, #f59e0b, #d97706)' }}
            >
              {exportSlidesLoading ? <Loader2 size={18} style={{ animation: 'spin 1s linear infinite' }} /> : <Presentation size={18} />}
              {exportSlidesLoading ? 'Generating Slides...' : 'Export to Google Slides'}
            </button>
            <button 
              className="btn-secondary" 
              onClick={handleExportSource} 
              disabled={exportSourceLoading}
              style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', color: '#fff', borderColor: '#3b82f6', background: 'rgba(59, 130, 246, 0.1)' }}
            >
              {exportSourceLoading ? <Loader2 size={18} style={{ animation: 'spin 1s linear infinite' }} /> : <Download size={18} />}
              {exportSourceLoading ? 'Generating...' : 'Download Source (JSON)'}
            </button>
          </div>
        )}
      </div>

      {exportDocUrl && (
        <div className="glass-panel" style={{ marginBottom: '1.5rem', padding: '1.25rem', background: 'rgba(16, 185, 129, 0.1)', border: '1px solid rgba(16, 185, 129, 0.3)', textAlign: 'left', borderRadius: '8px' }}>
          <h4 style={{ color: 'var(--success)', margin: '0 0 0.4rem 0', display: 'flex', alignItems: 'center', gap: '6px' }}>
            ✅ Google Doc Exported Successfully!
          </h4>
          <p style={{ margin: 0, color: 'var(--text-secondary)', fontSize: '0.9rem' }}>
            Live Google Doc: <a href={exportDocUrl} target="_blank" rel="noopener noreferrer" style={{ color: 'var(--accent-primary)', fontWeight: 'bold' }}>{exportDocUrl}</a>
          </p>
        </div>
      )}

      {exportSlidesUrl && (
        <div className="glass-panel" style={{ marginBottom: '1.5rem', padding: '1.25rem', background: 'rgba(16, 185, 129, 0.1)', border: '1px solid rgba(16, 185, 129, 0.3)', textAlign: 'left', borderRadius: '8px' }}>
          <h4 style={{ color: 'var(--success)', margin: '0 0 0.4rem 0', display: 'flex', alignItems: 'center', gap: '6px' }}>
            ✅ Google Slides Exported Successfully!
          </h4>
          <p style={{ margin: 0, color: 'var(--text-secondary)', fontSize: '0.9rem' }}>
            Live Presentation: <a href={exportSlidesUrl} target="_blank" rel="noopener noreferrer" style={{ color: 'var(--accent-primary)', fontWeight: 'bold' }}>{exportSlidesUrl}</a>
          </p>
        </div>
      )}

      {!triggered && (
        <div className="glass-card" style={{ textAlign: 'center', padding: '3rem', maxWidth: '700px', margin: '2rem auto' }}>
          <Brain size={56} color="var(--accent-primary)" style={{ marginBottom: '1.5rem' }} />
          <h2 style={{ color: '#fff', marginBottom: '0.5rem' }}>Ready to Run Deep Strategy Analysis</h2>
          <p style={{ color: 'var(--text-secondary)', marginBottom: '2rem', fontSize: '0.95rem', lineHeight: '1.6' }}>
            This will execute 16 sequential analytical steps using your collected signals data.
            The analysis covers Problem Discovery, Behavioral Analysis, Market Research, Solution Generation, and Executive Presentation.
            <br /><br />
            <strong style={{ color: 'var(--warning)' }}>⏱ Estimated time: 5-8 minutes</strong> (due to Groq API rate limits between steps)
          </p>
          <button className="btn-primary" onClick={handleRun} style={{ padding: '0.75rem 2rem', fontSize: '1rem', display: 'inline-flex', alignItems: 'center', gap: '0.5rem' }}>
            <Brain size={20} /> Run Strategy Deep Dive
          </button>
        </div>
      )}

      {triggered && (loading || (data && data.steps)) && (
        <>
          {/* Progress Bar */}
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

          {/* Console Log UI */}
          {loading && (
            <div style={{
              background: '#121214',
              color: '#4ade80',
              fontFamily: 'monospace',
              padding: '1.25rem',
              borderRadius: '8px',
              border: '1px solid var(--border-glass)',
              maxHeight: '280px',
              overflowY: 'auto',
              textAlign: 'left',
              marginBottom: '2rem',
              boxShadow: 'inset 0 2px 8px rgba(0, 0, 0, 0.8)',
              fontSize: '0.85rem',
              display: 'flex',
              flexDirection: 'column',
              gap: '0.35rem'
            }}>
              <div style={{ color: 'var(--text-muted)', borderBottom: '1px solid rgba(255,255,255,0.05)', paddingBottom: '0.5rem', marginBottom: '0.5rem', display: 'flex', justifyContent: 'space-between' }}>
                <span>🖥️ ANALYSIS ENGINE CONSOLE OUTPUT</span>
                <span style={{ display: 'flex', alignItems: 'center', gap: '0.25rem' }}>
                  <Loader2 size={12} style={{ animation: 'spin 1s linear infinite' }} /> Processing...
                </span>
              </div>
              {logs.map((log, index) => (
                <div key={index} style={{ whiteSpace: 'pre-wrap', lineHeight: '1.4' }}>
                  {log}
                </div>
              ))}
            </div>
          )}
        </>
      )}

      {data && data.steps && !loading && (
        <>
          {/* Tab Selector */}
          {boardPresentation && (
            <div style={{ display: 'flex', gap: '1rem', borderBottom: '1px solid var(--border-glass)', marginBottom: '1.5rem' }}>
              <button 
                onClick={() => setActiveTab('steps')}
                style={{
                  background: 'transparent',
                  border: 'none',
                  borderBottom: activeTab === 'steps' ? '2px solid var(--accent-primary)' : '2px solid transparent',
                  padding: '0.75rem 1rem',
                  color: activeTab === 'steps' ? '#fff' : 'var(--text-muted)',
                  cursor: 'pointer',
                  fontWeight: activeTab === 'steps' ? 'bold' : 'normal',
                  fontSize: '0.95rem'
                }}
              >
                Step Details (16 Steps)
              </button>
              <button 
                onClick={() => setActiveTab('slides')}
                style={{
                  background: 'transparent',
                  border: 'none',
                  borderBottom: activeTab === 'slides' ? '2px solid var(--accent-primary)' : '2px solid transparent',
                  padding: '0.75rem 1rem',
                  color: activeTab === 'slides' ? '#fff' : 'var(--text-muted)',
                  cursor: 'pointer',
                  fontWeight: activeTab === 'slides' ? 'bold' : 'normal',
                  fontSize: '0.95rem'
                }}
              >
                Board Presentation (10 Slides)
              </button>
            </div>
          )}

          {activeTab === 'steps' ? (
            <>
              {/* Phase Groups */}
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
            </>
          ) : (
            /* Board presentation viewer */
            boardPresentation && boardPresentation.slides && (
              <div className="grid-2" style={{ gridTemplateColumns: '7fr 3fr', gap: '2rem' }}>
                {/* Slide Canvas Column */}
                <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
                  {/* Slide Frame (16:9 Aspect Ratio) */}
                  <div className="glass-panel" style={{ 
                    aspectRatio: '16/9', 
                    background: 'linear-gradient(135deg, #0b1329, #14213d)', 
                    border: `2px solid rgba(255,255,255,0.08)`, 
                    borderRadius: '16px',
                    padding: '2.5rem',
                    display: 'flex',
                    flexDirection: 'column',
                    position: 'relative',
                    boxShadow: '0 15px 35px rgba(0,0,0,0.6)',
                    textAlign: 'left',
                    overflow: 'hidden'
                  }}>
                    {/* Top brand indicator */}
                    <div style={{ position: 'absolute', top: '12px', right: '20px', display: 'flex', alignItems: 'center', gap: '6px' }}>
                      <span style={{ width: '8px', height: '8px', borderRadius: '50%', background: boardPresentation.primary_color || '#3b82f6' }}></span>
                      <span style={{ fontSize: '0.7rem', color: '#94a3b8', textTransform: 'uppercase', letterSpacing: '1px', fontWeight: 'bold' }}>
                        {boardPresentation.presentation_theme || 'BOARD STUDY'}
                      </span>
                    </div>

                    {/* Slide Body */}
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
                            <div style={{ display: 'flex', flexDirection: 'column', justifyContent: 'center', gap: '0.65rem' }}>
                              {entries.slice(0, 4).map(([key, val]) => {
                                const label = key.replace(/_/g, ' ').replace(/\b\w/g, c => c.toUpperCase());
                                return (
                                  <div key={key} style={{ 
                                    background: 'rgba(255,255,255,0.02)', 
                                    padding: '0.6rem 0.8rem', 
                                    borderRadius: '8px', 
                                    border: `1px solid rgba(255,255,255,0.05)`,
                                    borderLeft: `3px solid ${brandColor}`
                                  }}>
                                    <strong style={{ color: '#fff', fontSize: '0.7rem', textTransform: 'uppercase', display: 'block', marginBottom: '0.15rem' }}>{label}</strong>
                                    {Array.isArray(val) ? (
                                      <ul style={{ margin: 0, paddingLeft: '1.1rem', fontSize: '0.8rem', color: '#94a3b8', lineHeight: '1.4' }}>
                                        {val.map((item, idx) => <li key={idx}>{item}</li>)}
                                      </ul>
                                    ) : (
                                      <span style={{ fontSize: '0.8rem', color: '#94a3b8', lineHeight: '1.4' }}>{val}</span>
                                    )}
                                  </div>
                                );
                              })}
                            </div>
                          </div>
                        );
                      })()}
                    </div>

                    {/* Slide Footer */}
                    <div style={{ display: 'flex', justifyContent: 'space-between', borderTop: `1px solid rgba(255,255,255,0.08)`, paddingTop: '0.75rem', marginTop: '1rem', fontSize: '0.75rem', color: '#64748b' }}>
                      <span>Pulse Intelligence — CPO Board Presentation</span>
                      <span>McKinsey Storytelling Flow</span>
                    </div>
                  </div>

                  {/* Navigation Controls */}
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

                {/* Presenter Speaker Notes Column */}
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
                      <p style={{ color: 'var(--text-muted)' }}>No presenter notes compiled for this slide.</p>
                    )}
                  </div>
                </div>
              </div>
            )
          )}
        </>
      )}
      <style>{`@keyframes spin { from { transform: rotate(0deg); } to { transform: rotate(360deg); } }`}</style>
    </div>
  );
};

export default StrategyDeepDive;
