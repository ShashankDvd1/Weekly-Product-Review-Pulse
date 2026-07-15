import React, { useState, useEffect } from 'react';
import { Microscope, HelpCircle, CheckCircle, FileText } from 'lucide-react';
import { getBackendUrl } from '../config';

const ResearchCopilot = () => {
  const [hypotheses, setHypotheses] = useState(null);
  const [questions, setQuestions] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const [hypRes, qRes] = await Promise.all([
          fetch(`${getBackendUrl()}/api/v2/research/hypotheses`),
          fetch(`${getBackendUrl()}/api/v2/research/questions`)
        ]);
        
        const hypData = await hypRes.json();
        const qData = await qRes.json();
        
        setHypotheses(hypData);
        setQuestions(qData);
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
        <h1 className="page-title text-gradient">Research Copilot</h1>
        <p className="page-subtitle">Testable hypotheses and "Mom Test" interview questions generated from behavioral data.</p>
      </div>

      <div className="grid-2">
        {/* Hypotheses Column */}
        <div style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
          <h2 style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '0.5rem' }}>
            <Microscope color="var(--accent-primary)" /> Product Hypotheses
          </h2>
          
          {hypotheses?.hypotheses?.map((hyp, idx) => (
            <div key={idx} className="glass-card" style={{ borderLeft: '4px solid var(--accent-secondary)' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '0.5rem' }}>
                <h3 style={{ fontSize: '1.1rem', color: '#fff' }}>Hypothesis {idx + 1}</h3>
                <span className="badge badge-success">{Math.round(hyp.confidence * 100)}% Conf.</span>
              </div>
              
              <p style={{ fontWeight: '500', color: 'var(--text-primary)', marginBottom: '1rem', fontStyle: 'italic' }}>
                {hyp.statement}
              </p>
              
              <div style={{ background: 'var(--bg-secondary)', padding: '1rem', borderRadius: '8px', fontSize: '0.9rem', color: 'var(--text-secondary)', marginBottom: '1rem' }}>
                <strong>Rationale:</strong> {hyp.rationale}
              </div>
              
              <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', fontSize: '0.85rem', color: 'var(--info)' }}>
                <CheckCircle size={16} /> Validation Method: {hyp.validation_method}
              </div>
            </div>
          ))}
        </div>

        {/* Interview Questions Column */}
        <div style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
          <h2 style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '0.5rem' }}>
            <HelpCircle color="var(--accent-tertiary)" /> Interview Guide
          </h2>
          
          <div className="glass-card" style={{ padding: '0' }}>
            <div style={{ padding: '1.5rem', borderBottom: '1px solid var(--border-glass)' }}>
              <h3 style={{ fontSize: '1.1rem', margin: 0, color: 'var(--text-primary)' }}>"Mom Test" Questionnaire</h3>
              <p style={{ fontSize: '0.85rem', color: 'var(--text-muted)', margin: '0.5rem 0 0 0' }}>
                Behavioral questions focused on past actions, designed to validate the hypotheses.
              </p>
            </div>
            
            <div style={{ padding: '1.5rem', display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
              {questions?.questions?.map((q, idx) => (
                <div key={idx} style={{ display: 'flex', gap: '1rem' }}>
                  <div style={{ 
                    width: '30px', height: '30px', borderRadius: '50%', 
                    background: 'var(--bg-secondary)', display: 'flex', alignItems: 'center', justifyContent: 'center',
                    fontWeight: 'bold', color: 'var(--accent-tertiary)', flexShrink: 0
                  }}>
                    {idx + 1}
                  </div>
                  <div>
                    <p style={{ fontWeight: '500', color: '#fff', margin: '0 0 0.25rem 0' }}>{q.question}</p>
                    <p style={{ fontSize: '0.85rem', color: 'var(--text-muted)', margin: '0 0 0.5rem 0' }}>{q.purpose}</p>
                    <div style={{ display: 'flex', gap: '0.5rem' }}>
                      <span className="badge" style={{ background: 'rgba(255,255,255,0.05)', color: 'var(--text-secondary)' }}>{q.question_type}</span>
                      {q.target_persona && <span className="badge" style={{ background: 'rgba(255,255,255,0.05)', color: 'var(--text-secondary)' }}>{q.target_persona}</span>}
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ResearchCopilot;
