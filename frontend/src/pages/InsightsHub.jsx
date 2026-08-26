import { useState, useEffect } from 'react';
import { 
  Target, 
  AlertCircle, 
  TrendingDown, 
  EyeOff, 
  ShieldAlert, 
  Clock, 
  IndianRupee, 
  MapPin,
  UserCircle, 
  ShoppingBag, 
  Zap,
  Lightbulb, 
  Beaker,
  Users,
  HelpCircle,
  Scissors,
  Layers,
  Truck,
  Bookmark
} from 'lucide-react';
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

const InsightsHub = () => {
  const [activeTab, setActiveTab] = useState('barriers'); // 'barriers', 'personas', 'opportunities'
  
  // Barriers data
  const [barriersData, setBarriersData] = useState(null);
  const [barriersLoading, setBarriersLoading] = useState(true);
  const [barriersError, setBarriersError] = useState(null);

  // Personas data
  const [personasData, setPersonasData] = useState(null);
  const [personasLoading, setPersonasLoading] = useState(true);

  // Opportunities data
  const [oppsData, setOppsData] = useState(null);
  const [oppsLoading, setOppsLoading] = useState(true);

  // Fetch Category Barriers
  useEffect(() => {
    if (activeTab === 'barriers' && !barriersData) {
      const fetchData = async () => {
        try {
          setBarriersLoading(true);
          const response = await fetch(`${getBackendUrl()}/api/v2/analyze/barriers`);
          if (!response.ok) throw new Error('Failed to fetch barriers');
          const result = await response.json();
          setBarriersData(result);
        } catch (err) {
          setBarriersError(err.message);
        } finally {
          setBarriersLoading(false);
        }
      };
      fetchData();
    }
  }, [activeTab, barriersData]);

  // Fetch Personas
  useEffect(() => {
    if (activeTab === 'personas' && !personasData) {
      const fetchData = async () => {
        try {
          setPersonasLoading(true);
          const response = await fetch(`${getBackendUrl()}/api/v2/analyze/personas`);
          const result = await response.json();
          setPersonasData(result);
        } catch (err) {
          console.error(err);
        } finally {
          setPersonasLoading(false);
        }
      };
      fetchData();
    }
  }, [activeTab, personasData]);

  // Fetch Opportunities
  useEffect(() => {
    if (activeTab === 'opportunities' && !oppsData) {
      const fetchData = async () => {
        try {
          setOppsLoading(true);
          const response = await fetch(`${getBackendUrl()}/api/v2/analyze/opportunities`);
          const result = await response.json();
          setOppsData(result);
        } catch (err) {
          console.error(err);
        } finally {
          setOppsLoading(false);
        }
      };
      fetchData();
    }
  }, [activeTab, oppsData]);

  const getImpactBadge = (impact) => {
    if (impact === 'high') return <span className="badge badge-success">High Impact</span>;
    if (impact === 'medium') return <span className="badge badge-warning">Medium Impact</span>;
    return <span className="badge badge-info">Low Impact</span>;
  };

  return (
    <div>
      <div className="page-header" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <div>
          <h1 className="page-title text-gradient">Consumer Insights</h1>
          <p className="page-subtitle">AI-synthesized behavioral barriers, user personas, and actionable opportunities.</p>
        </div>

        {/* Tab Selection Switcher */}
        <div className="glass-panel" style={{ display: 'flex', padding: '0.25rem', borderRadius: '8px', gap: '0.25rem' }}>
          <button 
            onClick={() => setActiveTab('barriers')}
            style={{
              padding: '0.5rem 1rem', borderRadius: '6px', border: 'none',
              background: activeTab === 'barriers' ? 'var(--accent-primary)' : 'transparent',
              color: activeTab === 'barriers' ? '#fff' : 'var(--text-secondary)',
              cursor: 'pointer', fontWeight: '600', transition: 'all 0.2s ease'
            }}
          >
            Category Barriers
          </button>
          <button 
            onClick={() => setActiveTab('personas')}
            style={{
              padding: '0.5rem 1rem', borderRadius: '6px', border: 'none',
              background: activeTab === 'personas' ? 'var(--accent-primary)' : 'transparent',
              color: activeTab === 'personas' ? '#fff' : 'var(--text-secondary)',
              cursor: 'pointer', fontWeight: '600', transition: 'all 0.2s ease'
            }}
          >
            User Personas
          </button>
          <button 
            onClick={() => setActiveTab('opportunities')}
            style={{
              padding: '0.5rem 1rem', borderRadius: '6px', border: 'none',
              background: activeTab === 'opportunities' ? 'var(--accent-primary)' : 'transparent',
              color: activeTab === 'opportunities' ? '#fff' : 'var(--text-secondary)',
              cursor: 'pointer', fontWeight: '600', transition: 'all 0.2s ease'
            }}
          >
            Growth Opportunities
          </button>
        </div>
      </div>

      {/* RENDER BARRIERS TAB */}
      {activeTab === 'barriers' && (
        <div>
          {barriersLoading ? (
            <div className="loader" style={{ margin: '4rem auto', display: 'block' }}></div>
          ) : barriersError ? (
            <div className="glass-card" style={{ borderColor: 'var(--danger)', color: 'var(--danger)' }}>
              <h3 style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '0.5rem' }}>
                <AlertCircle /> Error
              </h3>
              <p>{barriersError}</p>
            </div>
          ) : (
            <div className="grid-2">
              {barriersData?.barriers?.map((barrier, idx) => (
                <div key={idx} className="glass-card" style={{ display: 'flex', flexDirection: 'column', gap: '1rem', textAlign: 'left' }}>
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
                        <h3 style={{ margin: 0, color: '#fff', fontSize: '1.25rem' }}>{barrier.name}</h3>
                        <span className="badge badge-info" style={{ marginTop: '0.25rem' }}>
                          Type: {barrier.barrier_type.replace('_', ' ').toUpperCase()}
                        </span>
                      </div>
                    </div>
                    <span className="badge badge-warning" style={{ fontWeight: 'bold' }}>
                      {Math.round(barrier.confidence * 100)}% Confidence
                    </span>
                  </div>

                  <p style={{ color: 'var(--text-secondary)', fontSize: '0.95rem', lineHeight: '1.5', margin: 0 }}>
                    {barrier.description}
                  </p>

                  <div style={{ borderTop: '1px solid var(--border-glass)', paddingTop: '1rem', marginTop: '0.5rem' }}>
                    <h4 style={{ color: '#fff', fontSize: '0.9rem', marginBottom: '0.5rem', display: 'flex', alignItems: 'center', gap: '4px' }}>
                      💡 Recommended Mitigation Product Requirement
                    </h4>
                    <p style={{ color: 'var(--text-muted)', fontSize: '0.85rem', lineHeight: '1.4', margin: 0 }}>
                      {barrier.mitigation_strategy}
                    </p>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      )}

      {/* RENDER PERSONAS TAB */}
      {activeTab === 'personas' && (
        <div>
          {personasLoading ? (
            <div className="loader" style={{ margin: '4rem auto', display: 'block' }}></div>
          ) : (
            <div className="grid-2">
              {personasData?.personas?.map((persona, idx) => (
                <div key={idx} className="glass-card" style={{ position: 'relative', overflow: 'hidden', textAlign: 'left' }}>
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

                    <div>
                      <h4 style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', color: 'var(--text-primary)', marginBottom: '0.5rem' }}>
                        <Zap size={16} color="var(--warning)" /> Core Friction & Pain Point
                      </h4>
                      <p style={{ fontSize: '0.9rem', color: 'var(--text-muted)' }}>{persona.core_friction}</p>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      )}

      {/* RENDER OPPORTUNITIES TAB */}
      {activeTab === 'opportunities' && (
        <div>
          {oppsLoading ? (
            <div className="loader" style={{ margin: '4rem auto', display: 'block' }}></div>
          ) : (
            <div className="grid-2">
              {oppsData?.opportunities?.map((opp, idx) => (
                <div key={idx} className="glass-card" style={{ display: 'flex', flexDirection: 'column', gap: '1rem', textAlign: 'left' }}>
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
                        <Users size={14} /> Target Persona
                      </h4>
                      <p style={{ fontSize: '0.85rem', color: 'var(--text-primary)', margin: 0 }}>{opp.target_persona}</p>
                    </div>
                    
                    <div style={{ flex: 1, background: 'rgba(99, 102, 241, 0.05)', padding: '1rem', borderRadius: '8px', border: '1px solid rgba(99, 102, 241, 0.1)' }}>
                      <h4 style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', fontSize: '0.8rem', color: 'var(--accent-primary)', marginBottom: '0.5rem' }}>
                        <Beaker size={14} /> Core Value Proposition
                      </h4>
                      <p style={{ fontSize: '0.85rem', color: 'var(--text-primary)', margin: 0 }}>{opp.core_value_prop}</p>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      )}
    </div>
  );
};

export default InsightsHub;
