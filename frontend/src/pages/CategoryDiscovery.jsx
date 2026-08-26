import { useState, useEffect } from 'react';
import { Target, AlertCircle, TrendingDown, EyeOff, ShieldAlert, Clock, IndianRupee, MapPin, Zap, HelpCircle, Bookmark, Scissors, Layers, Truck } from 'lucide-react';
import { getBackendUrl } from '../config';

const barrierIcons = {
  awareness: <EyeOff size={24} />,
  trust: <ShieldAlert size={24} />,
  habit: <Clock size={24} />,
  price_perception: <IndianRupee size={24} />,
  quality_concern: <AlertCircle size={24} />,
  selection: <Target size={24} />,
  convenience: <TrendingDown size={24} />,
  discovery: <MapPin size={24} />,
  ux_friction: <Zap size={24} />,
  decision_paralysis: <HelpCircle size={24} />,
  intent_decay: <Bookmark size={24} />,
  fit_and_sizing: <Scissors size={24} />,
  usability: <Layers size={24} />,
  logistics: <Truck size={24} />
};

const CategoryDiscovery = () => {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const response = await fetch(`${getBackendUrl()}/api/v2/analyze/barriers`);
        if (!response.ok) throw new Error('Failed to fetch barriers');
        const result = await response.json();
        setData(result);
      } catch (err) {
        setError(err.message);
      } finally {
        setLoading(false);
      }
    };
    fetchData();
  }, []);

  if (loading) return <div className="loader" style={{ margin: '2rem auto', display: 'block' }}></div>;
  if (error) return <div className="glass-card" style={{ borderColor: 'var(--danger)' }}>{error}</div>;

  return (
    <div>
      <div className="page-header">
        <h1 className="page-title text-gradient">Category Discovery Barriers</h1>
        <p className="page-subtitle">Why users aren't exploring new categories in quick commerce.</p>
      </div>

      <div className="grid-2">
        {data?.barriers?.map((barrier, idx) => (
          <div key={idx} className="glass-card" style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
              <div style={{ display: 'flex', gap: '1rem', alignItems: 'center' }}>
                <div style={{ 
                  background: 'rgba(99, 102, 241, 0.1)', 
                  padding: '1rem', 
                  borderRadius: '12px',
                  color: 'var(--accent-primary)'
                }}>
                  {barrierIcons[barrier.barrier_type] || <AlertCircle size={24} />}
                </div>
                <div>
                  <h3 style={{ textTransform: 'capitalize' }}>{barrier.category}</h3>
                  <span className="badge badge-warning">{barrier.barrier_type.replace('_', ' ')}</span>
                </div>
              </div>
              <div style={{ textAlign: 'right' }}>
                <div style={{ fontSize: '1.25rem', fontWeight: 'bold', color: 'var(--success)' }}>
                  {Math.round(barrier.confidence * 100)}%
                </div>
                <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>Confidence</div>
              </div>
            </div>
            
            <p style={{ color: 'var(--text-secondary)', margin: '0.5rem 0' }}>{barrier.description}</p>
            
            <div style={{ background: 'rgba(0,0,0,0.2)', padding: '1rem', borderRadius: '8px', borderLeft: '3px solid var(--accent-secondary)' }}>
              <h4 style={{ fontSize: '0.85rem', color: 'var(--text-muted)', marginBottom: '0.5rem', textTransform: 'uppercase' }}>User Evidence</h4>
              <p style={{ fontStyle: 'italic', fontSize: '0.9rem' }}>"{barrier.supporting_evidence?.[0]?.text || 'No verbatim quote available.'}"</p>
            </div>
            
            <div style={{ marginTop: 'auto', paddingTop: '1rem', borderTop: '1px solid var(--border-glass)' }}>
              <h4 style={{ fontSize: '0.85rem', color: 'var(--accent-tertiary)', marginBottom: '0.25rem' }}>Recommended Intervention</h4>
              <p style={{ fontSize: '0.9rem' }}>{barrier.recommended_intervention}</p>
            </div>
          </div>
        ))}
        {(!data?.barriers || data.barriers.length === 0) && (
          <div className="glass-card" style={{ gridColumn: '1 / -1', textAlign: 'center', padding: '3rem' }}>
            <p style={{ color: 'var(--text-muted)' }}>No category barriers found. Have you run the pipeline yet?</p>
          </div>
        )}
      </div>
    </div>
  );
};

export default CategoryDiscovery;
