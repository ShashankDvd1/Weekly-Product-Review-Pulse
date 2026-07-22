import { useState, useEffect } from 'react';
import { Activity, MessageSquare, AlertTriangle, TrendingUp, RefreshCw, Users, Terminal, Send, Play, CheckCircle2, Calendar, Search, Layers } from 'lucide-react';
import { PieChart, Pie, Cell, ResponsiveContainer, Tooltip } from 'recharts';
import { getBackendUrl } from '../config';

const Dashboard = () => {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [pipelineRunning, setPipelineRunning] = useState(false);
  const [pipelineLogs, setPipelineLogs] = useState([]);
  const [pipelineStatus, setPipelineStatus] = useState(null);

  // Poll pipeline status if running
  useEffect(() => {
    let intervalId;
    if (pipelineRunning) {
      intervalId = setInterval(async () => {
        try {
          const res = await fetch(`${getBackendUrl()}/api/v2/pipeline/status`);
          const statusData = await res.json();
          setPipelineStatus(statusData.status);
          setPipelineLogs(statusData.progress || []);
          
          if (statusData.status === 'complete' || statusData.status === 'idle') {
            setPipelineRunning(false);
            clearInterval(intervalId);
            await fetchDashboardData();
            alert("Intelligence Pipeline Run Complete!");
          }
        } catch (err) {
          console.error("Error fetching pipeline status", err);
        }
      }, 2000);
    }
    return () => clearInterval(intervalId);
  }, [pipelineRunning]);

  // Default to 30 days ago to keep pipeline executions fast and clean
  const thirtyDaysAgo = new Date();
  thirtyDaysAgo.setDate(thirtyDaysAgo.getDate() - 30);
  const defaultFrom = thirtyDaysAgo.toISOString().split('T')[0];
  const defaultTo = new Date().toISOString().split('T')[0];

  const [dateRangeOption, setDateRangeOption] = useState('30days'); // '7days', '14days', '30days', 'custom'
  const [fromDate, setFromDate] = useState(defaultFrom);
  const [toDate, setToDate] = useState(defaultTo);

  // App Selection state for quick runs
  const [selectedApps, setSelectedApps] = useState({
    zepto: true,
    blinkit: true,
    swiggy_instamart: true
  });

  // AI Prompt Mode Ingestion states
  const [promptMode, setPromptMode] = useState('quick'); // 'quick' or 'ai_prompt'
  const [prompt, setPrompt] = useState('');
  const [parsing, setParsing] = useState(false);
  const [parsedConfig, setParsedConfig] = useState(null);

  useEffect(() => {
    if (dateRangeOption === 'custom') return;
    
    const today = new Date();
    const toStr = today.toISOString().split('T')[0];
    
    let days = 30;
    if (dateRangeOption === '7days') days = 7;
    else if (dateRangeOption === '14days') days = 14;
    else if (dateRangeOption === '30days') days = 30;
    
    const pastDate = new Date();
    pastDate.setDate(today.getDate() - days);
    const fromStr = pastDate.toISOString().split('T')[0];
    
    // eslint-disable-next-line
    setFromDate(fromStr);
    setToDate(toStr);
  }, [dateRangeOption]);

  useEffect(() => {
    fetchDashboardData();
  }, []);

  async function fetchDashboardData() {
    try {
      // Check if pipeline is running in the background
      const statusRes = await fetch(`${getBackendUrl()}/api/v2/pipeline/status`);
      const statusData = await statusRes.json();
      if (statusData.status === 'collecting' || statusData.status === 'analyzing') {
        setPipelineRunning(true);
        setPipelineStatus(statusData.status);
        setPipelineLogs(statusData.progress || []);
      }

      const response = await fetch(`${getBackendUrl()}/api/v2/dashboard/overview`);
      if (!response.ok) throw new Error('Failed to fetch dashboard data');
      const result = await response.json();
      setData(result);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const [problemStatement, setProblemStatement] = useState(
    "Users stick to repetitive buying habits and rarely explore new categories like electronics, toys, or beauty."
  );

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

  const handleLaunchAIPipeline = async () => {
    if (!parsedConfig) return;

    setPipelineRunning(true);
    setPipelineLogs(["[SYSTEM] Initiating AI custom intelligence run..."]);
    
    try {
      const res = await fetch(`${getBackendUrl()}/api/v2/pipeline/run`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          ...parsedConfig,
          problem_statement: problemStatement
        })
      });
      if (!res.ok) throw new Error("Pipeline run encountered a server error");
      const result = await res.json();
      setPipelineLogs(result.progress || []);
    } catch (err) {
      setError(err.message);
      setPipelineRunning(false);
    }
  };

  const handleRunPipeline = async () => {
    const appsToRun = Object.keys(selectedApps).filter(key => selectedApps[key]);
    if (appsToRun.length === 0) {
      alert("Please select at least one app to analyze.");
      return;
    }

    const confirm = window.confirm(`This will trigger a collection and analysis pipeline for [${appsToRun.join(', ')}] from ${fromDate} to ${toDate}. Continue?`);
    if (!confirm) return;
    
    try {
      setPipelineRunning(true);
      setPipelineLogs(["[SYSTEM] Initiating intelligence run with custom problem statement..."]);
      const response = await fetch(`${getBackendUrl()}/api/v2/pipeline/run`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          apps: appsToRun,
          from_date: fromDate,
          to_date: toDate,
          include_reddit: true,
          problem_statement: problemStatement
        })
      });
      if (!response.ok) throw new Error('Pipeline failed to initiate');
    } catch (err) {
      alert("Error: " + err.message);
      setPipelineRunning(false);
    }
  };

  if (loading && !data) return (
    <div className="flex-center" style={{ height: '80vh', display: 'flex', justifyContent: 'center', alignItems: 'center', flexDirection: 'column', gap: '1rem' }}>
      <div className="loader" style={{ width: '40px', height: '40px', borderColor: 'rgba(99, 102, 241, 0.3)', borderTopColor: 'var(--accent-primary)' }}></div>
      <p style={{ color: 'var(--text-secondary)' }}>Loading Intelligence Overview...</p>
    </div>
  );

  if (error) return (
    <div className="glass-card" style={{ borderColor: 'var(--danger)', margin: '2rem' }}>
      <h3 style={{ color: 'var(--danger)', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
        <AlertTriangle /> Error
      </h3>
      <p>{error}</p>
      <button className="btn-secondary" onClick={fetchDashboardData} style={{ marginTop: '1rem' }}>Retry</button>
    </div>
  );

  // Formatting Sentiment Data for Chart
  const sentData = data?.sentiment_summary ? [
    { name: 'Positive', value: data.sentiment_summary.positive_pct, color: 'var(--success)' },
    { name: 'Neutral', value: data.sentiment_summary.neutral_pct, color: 'var(--info)' },
    { name: 'Negative', value: data.sentiment_summary.negative_pct, color: 'var(--danger)' }
  ] : [];

  return (
    <div>
      <div className="page-header" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1.5rem' }}>
        <div>
          <h1 className="page-title text-gradient">Pulse Dashboard</h1>
          <p className="page-subtitle">Configure pipelines, monitor ingestion runs, and track overall commerce indicators.</p>
          {data?.date_range?.from_date && (
            <p style={{ fontSize: '0.85rem', color: 'var(--text-muted)', marginTop: '0.25rem' }}>
              Dataset coverage: <strong>{data.date_range.from_date}</strong> to <strong>{data.date_range.to_date}</strong>
            </p>
          )}
        </div>
      </div>

      {/* SETUP & INGESTION CONTROL PANEL */}
      <div className="glass-card" style={{ marginBottom: '1.5rem', padding: '1.5rem', textAlign: 'left' }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', borderBottom: '1px solid var(--border-glass)', paddingBottom: '0.75rem', marginBottom: '1.25rem' }}>
          <h3 style={{ margin: 0, color: '#fff', display: 'flex', alignItems: 'center', gap: '8px' }}>
            <Terminal size={18} color="var(--accent-primary)" /> Ingestion Settings & Control
          </h3>
          <div className="glass-panel" style={{ display: 'flex', padding: '0.2rem', borderRadius: '6px', gap: '0.2rem' }}>
            <button
              onClick={() => setPromptMode('quick')}
              style={{
                padding: '0.35rem 0.75rem', borderRadius: '4px', border: 'none', fontSize: '0.75rem', fontWeight: 'bold',
                background: promptMode === 'quick' ? 'var(--accent-primary)' : 'transparent',
                color: promptMode === 'quick' ? '#fff' : 'var(--text-secondary)',
                cursor: 'pointer', transition: 'all 0.2s ease'
              }}
            >
              Quick Setup
            </button>
            <button
              onClick={() => setPromptMode('ai_prompt')}
              style={{
                padding: '0.35rem 0.75rem', borderRadius: '4px', border: 'none', fontSize: '0.75rem', fontWeight: 'bold',
                background: promptMode === 'ai_prompt' ? 'var(--accent-primary)' : 'transparent',
                color: promptMode === 'ai_prompt' ? '#fff' : 'var(--text-secondary)',
                cursor: 'pointer', transition: 'all 0.2s ease'
              }}
            >
              AI Ingestion Prompt
            </button>
          </div>
        </div>

        {/* QUICK SETTINGS SUBPANEL */}
        {promptMode === 'quick' ? (
          <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
            <div style={{ display: 'flex', flexWrap: 'wrap', gap: '1.5rem', alignItems: 'center' }}>
              <div style={{ display: 'flex', flexDirection: 'column', gap: '0.35rem' }}>
                <span style={{ fontSize: '0.75rem', color: 'var(--text-secondary)', textTransform: 'uppercase', letterSpacing: '0.5px', fontWeight: 'bold' }}>Target Apps</span>
                <div style={{ display: 'flex', alignItems: 'center', gap: '1rem', background: 'var(--bg-secondary)', border: '1px solid var(--border-glass)', borderRadius: '6px', padding: '0.4rem 0.8rem', fontSize: '0.85rem' }}>
                  <label style={{ display: 'flex', alignItems: 'center', gap: '0.3rem', cursor: 'pointer', color: '#fff' }}>
                    <input type="checkbox" checked={selectedApps.zepto} onChange={(e) => setSelectedApps(prev => ({ ...prev, zepto: e.target.checked }))} /> Zepto
                  </label>
                  <label style={{ display: 'flex', alignItems: 'center', gap: '0.3rem', cursor: 'pointer', color: '#fff' }}>
                    <input type="checkbox" checked={selectedApps.blinkit} onChange={(e) => setSelectedApps(prev => ({ ...prev, blinkit: e.target.checked }))} /> Blinkit
                  </label>
                  <label style={{ display: 'flex', alignItems: 'center', gap: '0.3rem', cursor: 'pointer', color: '#fff' }}>
                    <input type="checkbox" checked={selectedApps.swiggy_instamart} onChange={(e) => setSelectedApps(prev => ({ ...prev, swiggy_instamart: e.target.checked }))} /> Swiggy Instamart
                  </label>
                </div>
              </div>

              <div style={{ display: 'flex', flexDirection: 'column', gap: '0.35rem' }}>
                <span style={{ fontSize: '0.75rem', color: 'var(--text-secondary)', textTransform: 'uppercase', letterSpacing: '0.5px', fontWeight: 'bold' }}>Date Range</span>
                <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', fontSize: '0.9rem' }}>
                  <select
                    value={dateRangeOption}
                    onChange={(e) => setDateRangeOption(e.target.value)}
                    style={{ background: 'var(--bg-secondary)', border: '1px solid var(--border-glass)', borderRadius: '6px', color: '#fff', padding: '0.4rem 0.8rem', fontFamily: 'inherit', outline: 'none', cursor: 'pointer' }}
                  >
                    <option value="7days">1 Week</option>
                    <option value="14days">2 Weeks</option>
                    <option value="30days">1 Month</option>
                    <option value="custom">Custom Range</option>
                  </select>
                  {dateRangeOption === 'custom' && (
                    <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', paddingLeft: '0.5rem' }}>
                      <input type="date" value={fromDate} onChange={(e) => setFromDate(e.target.value)} style={{ background: 'var(--bg-secondary)', border: '1px solid var(--border-glass)', borderRadius: '4px', color: '#fff', padding: '0.3rem 0.5rem', fontFamily: 'inherit' }} />
                      <span style={{ color: 'var(--text-secondary)' }}>to</span>
                      <input type="date" value={toDate} onChange={(e) => setToDate(e.target.value)} style={{ background: 'var(--bg-secondary)', border: '1px solid var(--border-glass)', borderRadius: '4px', color: '#fff', padding: '0.3rem 0.5rem', fontFamily: 'inherit' }} />
                    </div>
                  )}
                </div>
              </div>

              <button className="btn-primary" onClick={handleRunPipeline} disabled={pipelineRunning} style={{ marginLeft: 'auto', padding: '0.6rem 1.5rem', display: 'flex', alignItems: 'center', gap: '6px' }}>
                {pipelineRunning ? <div className="loader" style={{ width: '16px', height: '16px', borderTopColor: '#fff' }}></div> : <Play size={16} />}
                Launch Ingestion
              </button>
            </div>
          </div>
        ) : (
          /* AI PROMPT INGESTION SUBPANEL */
          <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
            <form onSubmit={handleParsePrompt} style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
              <textarea 
                value={prompt}
                onChange={(e) => setPrompt(e.target.value)}
                placeholder="e.g. 'Fetch Zepto reviews for the last 14 days and search reddit for grocery checkout errors'"
                disabled={parsing || pipelineRunning}
                style={{ 
                  width: '100%', minHeight: '80px', background: 'var(--bg-secondary)', 
                  border: '1px solid var(--border-glass)', borderRadius: '8px', color: '#fff', 
                  padding: '0.75rem', fontFamily: 'inherit', resize: 'vertical', fontSize: '0.9rem'
                }}
              />
              <button type="submit" className="btn-primary" disabled={parsing || pipelineRunning || !prompt.trim()} style={{ alignSelf: 'flex-end', padding: '0.4rem 1.2rem', display: 'flex', alignItems: 'center', gap: '6px' }}>
                {parsing ? <RefreshCw className="loader" size={14} /> : <Send size={14} />}
                Parse Ingestion Request
              </button>
            </form>

            {parsedConfig && (
              <div style={{ padding: '1rem', background: 'rgba(16, 185, 129, 0.05)', border: '1px solid rgba(16, 185, 129, 0.2)', borderRadius: '8px', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <div style={{ fontSize: '0.85rem', color: '#cbd5e1' }}>
                  <strong>Ingestion Plan:</strong> Apps: {parsedConfig.apps.join(', ')} | Range: {parsedConfig.from_date} to {parsedConfig.to_date} | Reddit: {parsedConfig.include_reddit ? 'Yes' : 'No'}
                </div>
                <button className="btn-primary" onClick={handleLaunchAIPipeline} disabled={pipelineRunning} style={{ background: 'var(--success)', padding: '0.4rem 1rem', display: 'flex', alignItems: 'center', gap: '6px' }}>
                  <Play size={14} /> Run AI Plan
                </button>
              </div>
            )}
          </div>
        )}
      </div>

      {/* Problem Statement Control Bar */}
      <div className="glass-card" style={{ marginBottom: '1.5rem', padding: '1rem 1.25rem', background: 'rgba(99, 102, 241, 0.05)', border: '1px solid rgba(99, 102, 241, 0.2)' }}>
        <label style={{ display: 'block', fontSize: '0.85rem', fontWeight: 600, color: 'var(--accent-primary)', marginBottom: '0.4rem' }}>
          🎯 Target Problem Statement / Strategic Focus:
        </label>
        <input 
          type="text" 
          value={problemStatement} 
          onChange={(e) => setProblemStatement(e.target.value)} 
          placeholder="e.g. Why do users stick to grocery categories and avoid exploring electronics or beauty?"
          style={{
            width: '100%',
            background: 'var(--bg-secondary)',
            border: '1px solid var(--border-glass)',
            borderRadius: '6px',
            color: '#fff',
            padding: '0.6rem 0.85rem',
            fontSize: '0.9rem',
            fontFamily: 'inherit',
            outline: 'none'
          }}
        />
        <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)', display: 'block', marginTop: '0.35rem' }}>
          This problem statement anchors all AI reasoning engines (Theme Detection, Category Barriers, Personas, JTBD, Opportunities & Survey Generation).
        </span>
      </div>

      {/* Real-time Pipeline Console */}
      {(pipelineRunning || pipelineLogs.length > 0) && (
        <div className="glass-card" style={{ 
          marginBottom: '2rem', 
          background: '#07070a', 
          border: '1px solid #1f1f2e', 
          fontFamily: 'monospace',
          padding: '1.25rem',
          borderRadius: '8px',
          animation: 'fadeIn 0.3s ease-out'
        }}>
          <div style={{ 
            display: 'flex', 
            justifyContent: 'space-between', 
            alignItems: 'center', 
            borderBottom: '1px solid #1f1f2e', 
            paddingBottom: '0.75rem', 
            marginBottom: '1rem' 
          }}>
            <span style={{ color: 'var(--text-muted)', fontSize: '0.85rem', display: 'flex', alignItems: 'center', gap: '8px' }}>
              <span style={{ display: 'inline-block', width: '8px', height: '8px', borderRadius: '50%', backgroundColor: pipelineRunning ? 'var(--accent-primary)' : 'var(--success)' }}></span>
              Pipeline Console Logs
            </span>
            <div style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
              {pipelineRunning && <span style={{ color: '#cbd5e1', fontSize: '0.85rem', animation: 'pulse 1.5s infinite' }}>Analyzing signals in real-time...</span>}
              {pipelineLogs.length > 0 && (
                <div style={{ display: 'flex', gap: '1rem' }}>
                  <button 
                    onClick={() => {
                      navigator.clipboard.writeText(pipelineLogs.join('\n'));
                      alert("Console logs copied to clipboard!");
                    }} 
                    style={{ background: 'transparent', border: 'none', color: 'var(--accent-primary)', cursor: 'pointer', fontSize: '0.85rem', fontWeight: 'bold' }}
                  >
                    📋 Copy Logs
                  </button>
                  <button 
                    onClick={() => setPipelineLogs([])} 
                    style={{ background: 'transparent', border: 'none', color: 'var(--text-muted)', cursor: 'pointer', fontSize: '0.85rem' }}
                  >
                    Clear Console
                  </button>
                </div>
              )}
            </div>
          </div>

          <div style={{ 
            maxHeight: '200px', 
            overflowY: 'auto', 
            display: 'flex', 
            flexDirection: 'column', 
            gap: '0.4rem', 
            fontSize: '0.85rem', 
            color: '#38bdf8',
            textAlign: 'left'
          }}>
            {pipelineLogs.map((log, index) => (
              <div key={index} style={{ 
                color: log.includes('❌') ? 'var(--danger)' : log.includes('✅') ? 'var(--success)' : '#cbd5e1' 
              }}>
                {log}
              </div>
            ))}
          </div>
        </div>
      )}

      {/* KPI Stats */}
      <div className="grid-4" style={{ marginBottom: '2rem' }}>
        <div className="glass-card stat-card">
          <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '1rem' }}>
            <span style={{ color: 'var(--text-secondary)' }}>Total Signals</span>
            <MessageSquare size={20} color="var(--accent-primary)" />
          </div>
          <h2 style={{ fontSize: '2.5rem', margin: 0 }}>{data?.total_signals || 0}</h2>
          <p style={{ color: 'var(--success)', fontSize: '0.85rem', display: 'flex', alignItems: 'center', gap: '4px', marginTop: '0.5rem' }}>
            <TrendingUp size={14} /> Active Dataset
          </p>
        </div>

        <div className="glass-card stat-card">
          <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '1rem' }}>
            <span style={{ color: 'var(--text-secondary)' }}>Themes Detected</span>
            <Activity size={20} color="var(--accent-secondary)" />
          </div>
          <h2 style={{ fontSize: '2.5rem', margin: 0 }}>{data?.top_themes?.length || 0}</h2>
          <p style={{ color: 'var(--text-muted)', fontSize: '0.85rem', marginTop: '0.5rem' }}>
            Across all sources
          </p>
        </div>

        <div className="glass-card stat-card">
          <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '1rem' }}>
            <span style={{ color: 'var(--text-secondary)' }}>Barriers Found</span>
            <AlertTriangle size={20} color="var(--warning)" />
          </div>
          <h2 style={{ fontSize: '2.5rem', margin: 0 }}>{data?.top_barriers?.length || 0}</h2>
          <p style={{ color: 'var(--text-muted)', fontSize: '0.85rem', marginTop: '0.5rem' }}>
            Preventing exploration
          </p>
        </div>

        <div className="glass-card stat-card">
          <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '1rem' }}>
            <span style={{ color: 'var(--text-secondary)' }}>Personas Gen.</span>
            <Users size={20} color="var(--accent-tertiary)" />
          </div>
          <h2 style={{ fontSize: '2.5rem', margin: 0 }}>{data?.personas_count || 0}</h2>
          <p style={{ color: 'var(--text-muted)', fontSize: '0.85rem', marginTop: '0.5rem' }}>
            Behavioral archetypes
          </p>
        </div>
      </div>

      <div className="grid-2">
        {/* Sentiment Chart */}
        <div className="glass-card" style={{ display: 'flex', flexDirection: 'column' }}>
          <h3 style={{ marginBottom: '1rem', borderBottom: '1px solid var(--border-glass)', paddingBottom: '0.5rem' }}>Overall Sentiment</h3>
          <div style={{ flex: 1, minHeight: '250px' }}>
            {sentData.length > 0 ? (
              <ResponsiveContainer width="100%" height="100%">
                <PieChart>
                  <Pie
                    data={sentData}
                    cx="50%"
                    cy="50%"
                    innerRadius={60}
                    outerRadius={80}
                    paddingAngle={5}
                    dataKey="value"
                  >
                    {sentData.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={entry.color} />
                    ))}
                  </Pie>
                  <Tooltip 
                    contentStyle={{ backgroundColor: 'var(--bg-secondary)', border: '1px solid var(--border-glass)', borderRadius: '8px' }}
                    itemStyle={{ color: '#fff' }}
                  />
                </PieChart>
              </ResponsiveContainer>
            ) : (
              <div style={{ height: '100%', display: 'flex', alignItems: 'center', justifyContent: 'center', color: 'var(--text-muted)' }}>
                No sentiment data available
              </div>
            )}
          </div>
          <div style={{ display: 'flex', justifyContent: 'center', gap: '1.5rem', marginTop: '1rem' }}>
            {sentData.map(d => (
              <div key={d.name} style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                <div style={{ width: '12px', height: '12px', borderRadius: '50%', backgroundColor: d.color }}></div>
                <span style={{ fontSize: '0.85rem', color: 'var(--text-secondary)' }}>{d.name} ({d.value}%)</span>
              </div>
            ))}
          </div>
        </div>

        {/* Source Distribution */}
        <div className="glass-card">
          <h3 style={{ marginBottom: '1rem', borderBottom: '1px solid var(--border-glass)', paddingBottom: '0.5rem' }}>Data Sources</h3>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem', marginTop: '1.5rem' }}>
            {data?.signals_by_source && Object.entries(data.signals_by_source).map(([source, count]) => (
              <div key={source}>
                <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '0.5rem' }}>
                  <span style={{ textTransform: 'capitalize' }}>{source.replace('_', ' ')}</span>
                  <span style={{ color: 'var(--text-secondary)' }}>{count} signals</span>
                </div>
                <div style={{ width: '100%', height: '8px', backgroundColor: 'rgba(255,255,255,0.1)', borderRadius: '4px', overflow: 'hidden' }}>
                  <div style={{ 
                    width: `${(count / data.total_signals) * 100}%`, 
                    height: '100%', 
                    background: 'var(--gradient-brand)',
                    borderRadius: '4px'
                  }}></div>
                </div>
              </div>
            ))}
          </div>
          
          <h3 style={{ margin: '2rem 0 1rem 0', borderBottom: '1px solid var(--border-glass)', paddingBottom: '0.5rem' }}>App Coverage</h3>
          <div style={{ display: 'flex', flexWrap: 'wrap', gap: '0.5rem' }}>
            {data?.signals_by_app && Object.entries(data.signals_by_app).map(([app, count]) => (
              <div key={app} style={{ background: 'rgba(255,255,255,0.05)', padding: '0.5rem 1rem', borderRadius: '20px', fontSize: '0.85rem' }}>
                <span style={{ textTransform: 'capitalize', color: 'var(--text-primary)' }}>{app.replace('_', ' ')}</span>
                <span style={{ color: 'var(--text-muted)', marginLeft: '0.5rem' }}>{count}</span>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
};

export default Dashboard;
