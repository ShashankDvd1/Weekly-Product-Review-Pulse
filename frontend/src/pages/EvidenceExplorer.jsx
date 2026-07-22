import { useState, useEffect } from 'react';
import { FileText, Link, Search } from 'lucide-react';
import { getBackendUrl } from '../config';

const EvidenceExplorer = () => {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const response = await fetch(`${getBackendUrl()}/api/v2/analyze/themes`);
        const result = await response.json();
        setData(result);
      } finally {
        setLoading(false);
      }
    };
    fetchData();
  }, []);

  if (loading) return <div className="loader" style={{ margin: '2rem auto', display: 'block' }}></div>;

  return (
    <div>
      <div className="page-header">
        <h1 className="page-title text-gradient">Evidence Explorer</h1>
        <p className="page-subtitle">Trace every AI insight back to its original verbatim source data.</p>
      </div>

      <div style={{ display: 'flex', flexDirection: 'column', gap: '2rem' }}>
        {data?.themes?.map((theme, idx) => (
          <div key={idx} className="glass-card">
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '1.5rem', paddingBottom: '1.5rem', borderBottom: '1px solid var(--border-glass)' }}>
              <div>
                <span className="badge" style={{ background: 'rgba(255,255,255,0.05)', marginBottom: '0.5rem' }}>Theme: {theme.category}</span>
                <h2 style={{ fontSize: '1.5rem', margin: '0 0 0.5rem 0', color: '#fff' }}>{theme.title}</h2>
                <p style={{ color: 'var(--text-secondary)', margin: 0 }}>{theme.summary}</p>
              </div>
              <div style={{ display: 'flex', gap: '0.5rem' }}>
                <span className={`badge badge-${theme.sentiment === 'positive' ? 'success' : theme.sentiment === 'negative' ? 'danger' : 'info'}`}>
                  {theme.sentiment}
                </span>
                <span className="badge badge-warning">{Math.round(theme.confidence * 100)}% Conf.</span>
              </div>
            </div>

            <div>
              <h4 style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', color: 'var(--accent-primary)', marginBottom: '1rem' }}>
                <Search size={16} /> Supporting Verbatim Evidence
              </h4>
              <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))', gap: '1rem' }}>
                {theme.supporting_quotes?.map((quote, qIdx) => (
                  <div key={qIdx} style={{ background: 'var(--bg-secondary)', padding: '1.25rem', borderRadius: '8px', borderLeft: '3px solid var(--accent-primary)' }}>
                    <p style={{ fontStyle: 'italic', fontSize: '0.95rem', color: 'var(--text-primary)', margin: '0 0 1rem 0' }}>"{quote}"</p>
                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', fontSize: '0.75rem', color: 'var(--text-muted)' }}>
                      <span>Source: App/Play Store</span>
                      <Link size={12} />
                    </div>
                  </div>
                ))}
              </div>
            </div>
            
          </div>
        ))}
        {(!data?.themes || data.themes.length === 0) && (
          <div className="glass-card" style={{ textAlign: 'center', padding: '3rem' }}>
            <p style={{ color: 'var(--text-muted)' }}>No themes/evidence found. Run the pipeline first.</p>
          </div>
        )}
      </div>
    </div>
  );
};

export default EvidenceExplorer;
