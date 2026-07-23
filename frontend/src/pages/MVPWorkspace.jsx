import { useState, useEffect } from 'react';
import { Target, Layers, PlayCircle, Settings, CheckCircle, BarChart2, ShieldAlert, Download, FileText, Monitor, Loader2 } from 'lucide-react';
import { getBackendUrl } from '../config';

const MVPWorkspace = () => {
  const [workspace, setWorkspace] = useState(null);
  const [loading, setLoading] = useState(true);
  
  const [exportDocLoading, setExportDocLoading] = useState(false);
  const [exportDocUrl, setExportDocUrl] = useState(null);
  const [exportSlidesLoading, setExportSlidesLoading] = useState(false);
  const [exportSlidesUrl, setExportSlidesUrl] = useState(null);
  const [exportSourceLoading, setExportSourceLoading] = useState(false);

  useEffect(() => {
    const fetchWorkspace = async () => {
      try {
        setLoading(true);
        const res = await fetch(`${getBackendUrl()}/api/v2/reports/mvp-workspace`);
        const data = await res.json();
        if (data && !data.error) {
          setWorkspace(data);
        }
      } catch (err) {
        console.error('Error fetching MVP Workspace', err);
      } finally {
        setLoading(false);
      }
    };
    fetchWorkspace();
  }, []);

  const handleExportDoc = async () => {
    try {
      setExportDocLoading(true);
      const res = await fetch(`${getBackendUrl()}/api/v2/reports/strategy-deep-dive/export-doc`, { method: 'POST' });
      const resData = await res.json();
      if (res.ok) setExportDocUrl(resData.document_url);
      else alert(resData.detail || "Could not export document.");
    } catch (err) {
      alert("Error exporting document: " + err.message);
    } finally {
      setExportDocLoading(false);
    }
  };

  const handleExportSlides = async () => {
    try {
      setExportSlidesLoading(true);
      const res = await fetch(`${getBackendUrl()}/api/v2/reports/strategy-deep-dive/export-slides`, { method: 'POST' });
      const resData = await res.json();
      if (res.ok) setExportSlidesUrl(resData.presentation_url);
      else alert(resData.detail || "Could not export slides.");
    } catch (err) {
      alert("Error exporting slides: " + err.message);
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

  if (loading) return (
    <div className="flex-center" style={{ height: '80vh', flexDirection: 'column', gap: '1rem' }}>
      <Loader2 size={32} style={{ animation: 'spin 1s linear infinite', color: '#10b981' }} />
      <div style={{ color: 'var(--text-muted)' }}>Generating MVP Workspace from Deep Dive...</div>
    </div>
  );

  if (!workspace) return (
    <div className="flex-center" style={{ height: '80vh', color: 'var(--text-muted)' }}>
      No MVP Workspace available. Complete the Strategy Deep Dive & Survey Validation first.
    </div>
  );

  return (
    <div style={{ padding: '2rem 0', maxWidth: '1000px', margin: '0 auto' }}>
      
      {/* Header */}
      <div style={{ marginBottom: '2rem', borderBottom: '1px solid var(--border)', paddingBottom: '1.5rem' }}>
        <h1 style={{ margin: '0 0 0.5rem 0', color: '#fff', fontSize: '2rem' }}>Product Requirements Document</h1>
        <p style={{ margin: 0, color: 'var(--text-muted)', fontSize: '1.1rem' }}>MVP Definition & Strategy</p>
      </div>

      {/* Problem & Audience */}
      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1.5rem', marginBottom: '2rem' }}>
        <div className="stat-card">
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', color: '#ef4444', marginBottom: '1rem' }}>
            <Target size={18} /> <h3 style={{ margin: 0 }}>Core Problem</h3>
          </div>
          <p style={{ color: '#fff', lineHeight: 1.5 }}>{workspace.problem_definition?.core_problem}</p>
        </div>
        <div className="stat-card">
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', color: '#3b82f6', marginBottom: '1rem' }}>
            <Monitor size={18} /> <h3 style={{ margin: 0 }}>Target Audience</h3>
          </div>
          <p style={{ color: '#fff', lineHeight: 1.5 }}>{workspace.problem_definition?.target_user_segment}</p>
        </div>
      </div>

      {/* Why this MVP */}
      <div className="stat-card" style={{ marginBottom: '2rem' }}>
        <h3 style={{ margin: '0 0 1rem 0', color: '#fff' }}>Strategic Rationale (Why this MVP?)</h3>
        <p style={{ color: 'var(--text-muted)', lineHeight: 1.6 }}>{workspace.why_this_mvp}</p>
      </div>

      {/* MoSCoW */}
      <div style={{ marginBottom: '2.5rem' }}>
        <h2 style={{ color: '#fff', marginBottom: '1rem', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
          <Layers size={20} color="#10b981" /> Scope Prioritization (MoSCoW)
        </h2>
        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1rem' }}>
          <div style={{ background: 'var(--surface)', border: '1px solid #10b98130', borderRadius: '8px', padding: '1rem' }}>
            <h4 style={{ color: '#10b981', margin: '0 0 0.5rem 0' }}>Must Have (MVP Core)</h4>
            <ul style={{ margin: 0, paddingLeft: '1.5rem', color: 'var(--text-main)' }}>
              {workspace.moscow_prioritization?.must_have?.map((item, i) => <li key={i}>{item}</li>)}
            </ul>
          </div>
          <div style={{ background: 'var(--surface)', border: '1px solid #3b82f630', borderRadius: '8px', padding: '1rem' }}>
            <h4 style={{ color: '#3b82f6', margin: '0 0 0.5rem 0' }}>Should Have</h4>
            <ul style={{ margin: 0, paddingLeft: '1.5rem', color: 'var(--text-main)' }}>
              {workspace.moscow_prioritization?.should_have?.map((item, i) => <li key={i}>{item}</li>)}
            </ul>
          </div>
        </div>
      </div>

      {/* Features */}
      <div style={{ marginBottom: '2.5rem' }}>
        <h2 style={{ color: '#fff', marginBottom: '1rem', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
          <Settings size={20} color="#8b5cf6" /> Feature Breakdown
        </h2>
        <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
          {workspace.feature_breakdown?.map((feat, i) => (
            <div key={i} style={{ background: 'var(--surface)', padding: '1rem', borderRadius: '8px', borderLeft: '4px solid #8b5cf6' }}>
              <h4 style={{ color: '#fff', margin: '0 0 0.5rem 0' }}>{feat.feature_name}</h4>
              <p style={{ color: 'var(--text-muted)', margin: '0 0 0.5rem 0', fontSize: '0.9rem' }}>{feat.description}</p>
              <div style={{ fontSize: '0.85rem', color: '#10b981', fontWeight: 'bold' }}>Value: {feat.user_value}</div>
            </div>
          ))}
        </div>
      </div>

      {/* Wireframes */}
      <div style={{ marginBottom: '2.5rem' }}>
        <h2 style={{ color: '#fff', marginBottom: '1rem', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
          <Monitor size={20} color="#ec4899" /> UI/UX Guidelines
        </h2>
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))', gap: '1rem' }}>
          {workspace.wireframe_suggestions?.map((wire, i) => (
            <div key={i} style={{ background: 'var(--surface)', padding: '1.5rem', borderRadius: '8px', border: '1px solid #ec489930' }}>
              <h4 style={{ color: '#ec4899', margin: '0 0 1rem 0' }}>{wire.screen_name}</h4>
              <div style={{ color: 'var(--text-main)', fontSize: '0.9rem', marginBottom: '1rem' }}>
                <strong>Layout:</strong> {wire.layout_guidance}
              </div>
              <ul style={{ margin: 0, paddingLeft: '1.2rem', color: 'var(--text-muted)', fontSize: '0.85rem' }}>
                {wire.key_elements?.map((el, j) => <li key={j} style={{ marginBottom: '0.25rem' }}>{el}</li>)}
              </ul>
            </div>
          ))}
        </div>
      </div>

      {/* KPIs */}
      <div style={{ marginBottom: '2.5rem' }}>
        <h2 style={{ color: '#fff', marginBottom: '1rem', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
          <BarChart2 size={20} color="#f59e0b" /> KPI Dashboard
        </h2>
        <div className="stat-card" style={{ padding: '0' }}>
          <table style={{ width: '100%', borderCollapse: 'collapse' }}>
            <thead>
              <tr style={{ background: 'var(--surface-light)', borderBottom: '1px solid var(--border)' }}>
                <th style={{ textAlign: 'left', padding: '1rem', color: 'var(--text-muted)' }}>Metric</th>
                <th style={{ textAlign: 'left', padding: '1rem', color: 'var(--text-muted)' }}>Type</th>
                <th style={{ textAlign: 'left', padding: '1rem', color: 'var(--text-muted)' }}>Target</th>
              </tr>
            </thead>
            <tbody>
              {workspace.kpi_dashboard?.map((kpi, i) => (
                <tr key={i} style={{ borderBottom: '1px solid var(--border)' }}>
                  <td style={{ padding: '1rem', color: '#fff', fontWeight: '500' }}>{kpi.metric_name}</td>
                  <td style={{ padding: '1rem', color: 'var(--text-muted)' }}>
                    <span style={{ 
                      padding: '0.25rem 0.5rem', borderRadius: '4px', fontSize: '0.75rem',
                      background: kpi.type.includes('North Star') ? '#f59e0b20' : 'var(--surface-light)',
                      color: kpi.type.includes('North Star') ? '#f59e0b' : 'var(--text-muted)'
                    }}>{kpi.type}</span>
                  </td>
                  <td style={{ padding: '1rem', color: '#10b981' }}>{kpi.target}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* Exports */}
      <div style={{ marginTop: '4rem', paddingTop: '2rem', borderTop: '1px solid var(--border)' }}>
        <h2 style={{ color: '#fff', marginBottom: '1rem' }}>Final Deliverables</h2>
        <div style={{ display: 'flex', gap: '1rem', flexWrap: 'wrap' }}>
          <button className="btn-secondary" onClick={handleExportSource} disabled={exportSourceLoading}>
            {exportSourceLoading ? <Loader2 size={16} className="spin" /> : <Download size={16} />} 
            Download Markdown (MD)
          </button>
          
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
            <button className="btn-secondary" onClick={handleExportDoc} disabled={exportDocLoading}>
              {exportDocLoading ? <Loader2 size={16} className="spin" /> : <FileText size={16} />} 
              Generate Google Doc
            </button>
            {exportDocUrl && (
              <a href={exportDocUrl} target="_blank" rel="noreferrer" style={{ color: '#10b981', fontSize: '0.9rem', textDecoration: 'none' }}>
                Open Doc ↗
              </a>
            )}
          </div>

          <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
            <button className="btn-secondary" onClick={handleExportSlides} disabled={exportSlidesLoading}>
              {exportSlidesLoading ? <Loader2 size={16} className="spin" /> : <PlayCircle size={16} />} 
              Generate Google Slides
            </button>
            {exportSlidesUrl && (
              <a href={exportSlidesUrl} target="_blank" rel="noreferrer" style={{ color: '#10b981', fontSize: '0.9rem', textDecoration: 'none' }}>
                Open Slides ↗
              </a>
            )}
          </div>
        </div>
      </div>

    </div>
  );
};

export default MVPWorkspace;
