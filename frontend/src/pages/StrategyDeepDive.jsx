import React, { useState, useEffect } from 'react';
import { Brain, ChevronDown, ChevronRight, Loader2, AlertTriangle, Target, Users, Lightbulb, Presentation, CheckCircle2 } from 'lucide-react';
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
  const [loading, setLoading] = useState(false);
  const [openSteps, setOpenSteps] = useState({});
  const [triggered, setTriggered] = useState(false);

  const handleRun = async () => {
    setLoading(true);
    setTriggered(true);
    try {
      const res = await fetch(`${getBackendUrl()}/api/v2/reports/strategy-deep-dive`);
      const result = await res.json();
      setData(result);
    } catch (err) {
      console.error('Strategy deep dive failed:', err);
    } finally {
      setLoading(false);
    }
  };

  const toggleStep = (stepId) => {
    setOpenSteps(prev => ({ ...prev, [stepId]: !prev[stepId] }));
  };

  const completedCount = data?.steps ? Object.values(data.steps).filter(s => s.status === 'complete').length : 0;
  const totalCount = data?.total_steps || 16;
  const progress = totalCount > 0 ? (completedCount / totalCount) * 100 : 0;

  return (
    <div>
      <div className="page-header" style={{ textAlign: 'left' }}>
        <h1 className="page-title text-gradient" style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
          <Brain size={32} /> Strategy Deep Dive
        </h1>
        <p className="page-subtitle">
          A 16-step Principal PM / Strategy Consultant analysis framework applying first-principles thinking, behavioral science, and competitive strategy.
        </p>
      </div>

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

      {loading && (
        <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', padding: '4rem', gap: '1.5rem' }}>
          <Loader2 size={48} color="var(--accent-primary)" style={{ animation: 'spin 1s linear infinite' }} />
          <p style={{ color: 'var(--text-secondary)', fontSize: '1rem' }}>Running 16-step deep analysis... This will take several minutes.</p>
          <p style={{ color: 'var(--text-muted)', fontSize: '0.85rem' }}>Each step queries the AI with your real signal data. Please be patient.</p>
          <style>{`@keyframes spin { from { transform: rotate(0deg); } to { transform: rotate(360deg); } }`}</style>
        </div>
      )}

      {data && data.steps && !loading && (
        <>
          {/* Progress Bar */}
          <div style={{ marginBottom: '2rem', padding: '0 0.5rem' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '0.5rem' }}>
              <span style={{ color: 'var(--text-secondary)', fontSize: '0.85rem' }}>Analysis Progress</span>
              <span style={{ color: 'var(--accent-primary)', fontWeight: 'bold', fontSize: '0.85rem' }}>
                {completedCount}/{totalCount} steps complete
              </span>
            </div>
            <div style={{ height: '6px', background: 'var(--bg-secondary)', borderRadius: '3px', overflow: 'hidden' }}>
              <div style={{ height: '100%', width: `${progress}%`, background: 'linear-gradient(90deg, var(--accent-primary), var(--accent-secondary))', borderRadius: '3px', transition: 'width 0.5s ease' }} />
            </div>
          </div>

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
      )}
    </div>
  );
};

export default StrategyDeepDive;
