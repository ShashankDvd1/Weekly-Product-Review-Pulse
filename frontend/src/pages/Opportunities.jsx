import { useState, useEffect } from 'react';
import { Lightbulb, TrendingUp, Zap, Beaker } from 'lucide-react';
import { getBackendUrl } from '../config';

const Opportunities = () => {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const response = await fetch(`${getBackendUrl()}/api/v2/analyze/opportunities`);
        const result = await response.json();
        setData(result);
      } finally {
        setLoading(false);
      }
    };
    fetchData();
  }, []);

  if (loading) return <div className="loader" style={{ margin: '2rem auto', display: 'block' }}></div>;

  const getImpactBadge = (impact) => {
    if (impact === 'high') return <span className="badge badge-success">High Impact</span>;
    if (impact === 'medium') return <span className="badge badge-warning">Medium Impact</span>;
    return <span className="badge badge-info">Low Impact</span>;
  };

  return (
    <div>
      <div className="page-header">
        <h1 className="page-title text-gradient">Growth Opportunities</h1>
        <p className="page-subtitle">Actionable product recommendations synthesized from user barriers and JTBD.</p>
      </div>

      <div className="grid-2">
        {data?.opportunities?.map((opp, idx) => (
          <div key={idx} className="glass-card" style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
            
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
              <div>
                <span style={{ fontSize: '0.75rem', textTransform: 'uppercase', color: 'var(--accent-primary)', fontWeight: '700', letterSpacing: '0.05em' }}>
                  {opp.category}
                </span>
                <h3 style={{ margin: '0.25rem 0 0.5rem 0', color: '#fff' }}>{opp.title}</h3>
              </div>
              <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'flex-end', gap: '0.5rem' }}>
                {getImpactBadge(opp.impact)}
                <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>Effort: {opp.effort}</span>
              </div>
            </div>

            <p style={{ color: 'var(--text-secondary)', fontSize: '0.95rem' }}>{opp.description}</p>

            <div style={{ marginTop: 'auto', display: 'flex', gap: '1rem' }}>
              <div style={{ flex: 1, background: 'rgba(16, 185, 129, 0.05)', padding: '1rem', borderRadius: '8px', border: '1px solid rgba(16, 185, 129, 0.1)' }}>
                <h4 style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', fontSize: '0.8rem', color: 'var(--success)', marginBottom: '0.5rem' }}>
                  <UsersIcon /> Target Persona
                </h4>
                <p style={{ fontSize: '0.85rem', color: 'var(--text-muted)' }}>{opp.target_persona || 'All Users'}</p>
              </div>
              
              <div style={{ flex: 1, background: 'rgba(245, 158, 11, 0.05)', padding: '1rem', borderRadius: '8px', border: '1px solid rgba(245, 158, 11, 0.1)' }}>
                <h4 style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', fontSize: '0.8rem', color: 'var(--warning)', marginBottom: '0.5rem' }}>
                  <Beaker size={14} /> Recommended Experiment
                </h4>
                <p style={{ fontSize: '0.85rem', color: 'var(--text-muted)' }}>{opp.recommended_experiment}</p>
              </div>
            </div>

          </div>
        ))}
      </div>
    </div>
  );
};

// Quick inline icon component to avoid extra imports
const UsersIcon = () => <svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M16 21v-2a4 4 0 0 0-4-4H6a4 4 0 0 0-4 4v2"></path><circle cx="9" cy="7" r="4"></circle><path d="M22 21v-2a4 4 0 0 0-3-3.87"></path><path d="M16 3.13a4 4 0 0 1 0 7.75"></path></svg>;

export default Opportunities;
