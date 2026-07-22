import { useState, useEffect } from 'react';
import { UserCircle, ShoppingBag, Zap, Target } from 'lucide-react';
import { getBackendUrl } from '../config';

const Personas = () => {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const response = await fetch(`${getBackendUrl()}/api/v2/analyze/personas`);
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
        <h1 className="page-title text-gradient">Behavioral Personas</h1>
        <p className="page-subtitle">AI-generated user archetypes based on real consumer signals.</p>
      </div>

      <div className="grid-2">
        {data?.personas?.map((persona, idx) => (
          <div key={idx} className="glass-card" style={{ position: 'relative', overflow: 'hidden' }}>
            {/* Background decorative blob */}
            <div style={{
              position: 'absolute', top: '-50px', right: '-50px', width: '150px', height: '150px',
              background: 'radial-gradient(circle, rgba(236,72,153,0.15) 0%, rgba(0,0,0,0) 70%)',
              borderRadius: '50%', pointerEvents: 'none'
            }}></div>

            <div style={{ display: 'flex', gap: '1rem', alignItems: 'center', marginBottom: '1.5rem' }}>
              <UserCircle size={48} color="var(--accent-tertiary)" strokeWidth={1.5} />
              <div>
                <h2 style={{ margin: 0, fontSize: '1.5rem', color: '#fff' }}>{persona.name}</h2>
                <span className="badge badge-info" style={{ marginTop: '0.25rem' }}>{persona.signal_count} matching signals</span>
              </div>
            </div>

            <p style={{ color: 'var(--text-secondary)', marginBottom: '1.5rem', fontSize: '0.95rem' }}>
              {persona.description}
            </p>

            <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
              <div>
                <h4 style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', color: 'var(--text-primary)', marginBottom: '0.5rem' }}>
                  <ShoppingBag size={16} color="var(--accent-primary)" /> Shopping Habits
                </h4>
                <p style={{ fontSize: '0.9rem', color: 'var(--text-muted)' }}>{persona.shopping_habits}</p>
              </div>

              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1rem' }}>
                <div>
                  <h4 style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', color: 'var(--success)', marginBottom: '0.5rem' }}>
                    <Zap size={16} /> Core Motivations
                  </h4>
                  <ul style={{ paddingLeft: '1.2rem', margin: 0, fontSize: '0.85rem', color: 'var(--text-muted)' }}>
                    {persona.motivations.map((m, i) => <li key={i}>{m}</li>)}
                  </ul>
                </div>
                <div>
                  <h4 style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', color: 'var(--warning)', marginBottom: '0.5rem' }}>
                    <Target size={16} /> Category Barriers
                  </h4>
                  <ul style={{ paddingLeft: '1.2rem', margin: 0, fontSize: '0.85rem', color: 'var(--text-muted)' }}>
                    {persona.barriers.map((b, i) => <li key={i}>{b}</li>)}
                  </ul>
                </div>
              </div>

              <div style={{ background: 'rgba(255,255,255,0.02)', padding: '1rem', borderRadius: '8px', borderTop: '1px solid var(--border-glass)' }}>
                <h4 style={{ fontSize: '0.75rem', textTransform: 'uppercase', color: 'var(--text-muted)', marginBottom: '0.5rem', letterSpacing: '0.05em' }}>
                  Representative Quote
                </h4>
                <p style={{ fontStyle: 'italic', fontSize: '0.9rem', color: 'var(--text-secondary)' }}>
                  "{persona.representative_quotes?.[0] || 'No quote available.'}"
                </p>
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

export default Personas;
