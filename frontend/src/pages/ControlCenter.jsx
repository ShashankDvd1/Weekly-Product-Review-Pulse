import React, { useState, useEffect } from 'react';
import { Terminal, Send, Play, CheckCircle2, AlertTriangle, Calendar, Search, Layers, RefreshCw } from 'lucide-react';
import { getBackendUrl } from '../config';

const ControlCenter = () => {
  const [prompt, setPrompt] = useState('');
  const [parsing, setParsing] = useState(false);
  const [parsedConfig, setParsedConfig] = useState(null);
  const [running, setRunning] = useState(false);
  const [pipelineStatus, setPipelineStatus] = useState(null);
  const [logs, setLogs] = useState([]);
  const [error, setError] = useState(null);

  // Poll pipeline status if running
  useEffect(() => {
    let intervalId;
    if (running) {
      intervalId = setInterval(async () => {
        try {
          const res = await fetch(`${getBackendUrl()}/api/v2/pipeline/status`);
          const statusData = await res.json();
          setPipelineStatus(statusData.status);
          setLogs(statusData.progress || []);
          
          if (statusData.status === 'complete' || statusData.status === 'idle') {
            setRunning(false);
            clearInterval(intervalId);
            alert("Intelligence Pipeline Run Complete!");
          }
        } catch (err) {
          console.error("Error fetching pipeline status", err);
        }
      }, 2000);
    }
    return () => clearInterval(intervalId);
  }, [running]);

  const handleParsePrompt = async (e) => {
    e.preventDefault();
    if (!prompt.trim()) return;

    setParsing(true);
    setError(null);
    setParsedConfig(null);

    try {
      const res = await fetch(`${getBackendUrl()}/api/v2/pipeline/parse-prompt`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ prompt })
      });
      if (!res.ok) throw new Error("Failed to parse prompt command");
      const config = await res.json();
      setParsedConfig(config);
    } catch (err) {
      setError(err.message);
    } finally {
      setParsing(false);
    }
  };

  const handleLaunchPipeline = async () => {
    if (!parsedConfig) return;

    setRunning(true);
    setLogs(["[SYSTEM] Initiating custom intelligence run..."]);
    
    try {
      const res = await fetch(`${getBackendUrl()}/api/v2/pipeline/run`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(parsedConfig)
      });
      if (!res.ok) throw new Error("Pipeline run encountered a server error");
      const result = await res.json();
      setLogs(result.progress || []);
    } catch (err) {
      setError(err.message);
      setRunning(false);
    }
  };

  return (
    <div>
      <div className="page-header">
        <h1 className="page-title text-gradient">Pipeline Control Center</h1>
        <p className="page-subtitle">Configure and run data ingestion using natural language prompts.</p>
      </div>

      <div className="grid-2">
        {/* Input Column */}
        <div style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
          <div className="glass-card">
            <h3 style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '1rem', color: '#fff' }}>
              <Terminal size={20} color="var(--accent-primary)" /> Ingestion Prompt Bar
            </h3>
            <p style={{ color: 'var(--text-secondary)', fontSize: '0.9rem', marginBottom: '1rem' }}>
              Describe what app reviews, Reddit topics, or dates you want the pipeline to ingest. 
              You can paste full Play Store/App Store URLs directly.
            </p>
            
            <form onSubmit={handleParsePrompt} style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
              <textarea 
                value={prompt}
                onChange={(e) => setPrompt(e.target.value)}
                placeholder="e.g. 'Fetch Zepto and Blinkit reviews for the last 30 days and search reddit for instant grocery delivery keywords'"
                disabled={parsing || running}
                style={{ 
                  width: '100%', minHeight: '120px', background: 'var(--bg-secondary)', 
                  border: '1px solid var(--border-glass)', borderRadius: '8px', color: '#fff', 
                  padding: '1rem', fontFamily: 'inherit', resize: 'vertical'
                }}
              />
              
              <button 
                type="submit" 
                className="btn-primary" 
                disabled={parsing || running || !prompt.trim()}
                style={{ alignSelf: 'flex-end' }}
              >
                {parsing ? <RefreshCw className="loader" size={16} /> : <Send size={16} />}
                {parsing ? 'Compiling Command...' : 'Parse Command'}
              </button>
            </form>
          </div>

          {/* Configuration Preview Card */}
          {parsedConfig && (
            <div className="glass-card" style={{ borderLeft: '4px solid var(--success)', animation: 'fadeIn 0.3s ease-out' }}>
              <h3 style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '1.5rem', color: '#fff' }}>
                <CheckCircle2 size={20} color="var(--success)" /> Command Compiled Successfully
              </h3>

              <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem', fontSize: '0.95rem' }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
                  <Layers size={16} color="var(--text-muted)" />
                  <span style={{ color: 'var(--text-secondary)' }}>Target Apps:</span>
                  <strong style={{ color: '#fff' }}>{parsedConfig.apps.join(', ') || 'Custom (Link-based)'}</strong>
                </div>

                {parsedConfig.play_store_package && (
                  <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', paddingLeft: '1.5rem' }}>
                    <span style={{ fontSize: '0.85rem', color: 'var(--text-muted)' }}>Play Store Package:</span>
                    <code style={{ fontSize: '0.85rem', color: 'var(--accent-secondary)' }}>{parsedConfig.play_store_package}</code>
                  </div>
                )}

                {parsedConfig.app_store_id && (
                  <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', paddingLeft: '1.5rem' }}>
                    <span style={{ fontSize: '0.85rem', color: 'var(--text-muted)' }}>App Store ID:</span>
                    <code style={{ fontSize: '0.85rem', color: 'var(--accent-secondary)' }}>{parsedConfig.app_store_id}</code>
                  </div>
                )}

                <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
                  <Calendar size={16} color="var(--text-muted)" />
                  <span style={{ color: 'var(--text-secondary)' }}>Date Range:</span>
                  <strong style={{ color: '#fff' }}>{parsedConfig.from_date} to {parsedConfig.to_date}</strong>
                </div>

                <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
                  <Search size={16} color="var(--text-muted)" />
                  <span style={{ color: 'var(--text-secondary)' }}>Reddit Search:</span>
                  <strong style={{ color: '#fff' }}>{parsedConfig.include_reddit ? 'Enabled' : 'Disabled'}</strong>
                </div>

                {parsedConfig.include_reddit && parsedConfig.reddit_search_terms?.length > 0 && (
                  <div style={{ display: 'flex', flexWrap: 'wrap', gap: '0.5rem', paddingLeft: '1.5rem' }}>
                    {parsedConfig.reddit_search_terms.map((term, i) => (
                      <span key={i} className="badge" style={{ background: 'rgba(255,255,255,0.05)', color: 'var(--text-secondary)' }}>
                        "{term}"
                      </span>
                    ))}
                  </div>
                )}
              </div>

              <div style={{ marginTop: '2rem', display: 'flex', justifyContent: 'flex-end' }}>
                <button className="btn-primary" onClick={handleLaunchPipeline} disabled={running} style={{ background: 'var(--success)' }}>
                  <Play size={16} /> Launch Ingestion Pipeline
                </button>
              </div>
            </div>
          )}

          {error && (
            <div className="glass-card" style={{ borderColor: 'var(--danger)', color: 'var(--danger)' }}>
              <h3 style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', color: 'var(--danger)', marginBottom: '0.5rem' }}>
                <AlertTriangle size={20} /> Error
              </h3>
              <p>{error}</p>
            </div>
          )}
        </div>

        {/* Live Logs / Terminal Column */}
        <div style={{ display: 'flex', flexDirection: 'column' }}>
          <div className="glass-card" style={{ 
            flex: 1, minHeight: '400px', display: 'flex', flexDirection: 'column', 
            background: '#07070a', border: '1px solid #1f1f2e', fontFamily: 'monospace'
          }}>
            <div style={{ 
              display: 'flex', justifyContent: 'space-between', alignItems: 'center', 
              borderBottom: '1px solid #1f1f2e', paddingBottom: '0.75rem', marginBottom: '1rem' 
            }}>
              <span style={{ color: 'var(--text-muted)', fontSize: '0.85rem' }}>Pipeline Console</span>
              {running && <span className="badge badge-info" style={{ animation: 'pulse 1.5s infinite' }}>running</span>}
            </div>

            <div style={{ 
              flex: 1, overflowY: 'auto', display: 'flex', flexDirection: 'column', 
              gap: '0.5rem', fontSize: '0.9rem', color: '#38bdf8' 
            }}>
              {logs.length === 0 ? (
                <div style={{ color: '#4b5563', fontStyle: 'italic', display: 'flex', height: '100%', alignItems: 'center', justifyContent: 'center' }}>
                  No execution logs yet. Launch the pipeline to view real-time logs.
                </div>
              ) : (
                logs.map((log, index) => (
                  <div key={index} style={{ 
                    color: log.includes('❌') ? 'var(--danger)' : log.includes('✅') ? 'var(--success)' : '#cbd5e1' 
                  }}>
                    {log}
                  </div>
                ))
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ControlCenter;
