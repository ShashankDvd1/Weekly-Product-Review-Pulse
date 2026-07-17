import React, { useState, useEffect } from 'react';
import { Award, CheckCircle, TrendingUp, HelpCircle, Shield, ListTodo, FileText, ArrowRight } from 'lucide-react';
import { getBackendUrl } from '../config';

const MvpCaseStudy = () => {
  const [caseStudy, setCaseStudy] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchCaseStudy = async () => {
      try {
        setLoading(true);
        const res = await fetch(`${getBackendUrl()}/api/v2/reports/mvp-case`);
        const data = await res.json();
        setCaseStudy(data);
      } catch (err) {
        console.error('Error fetching MVP case study', err);
      } finally {
        setLoading(false);
      }
    };
    fetchCaseStudy();
  }, []);

  if (loading) return (
    <div className="flex-center" style={{ height: '80vh', display: 'flex', justifyContent: 'center', alignItems: 'center', flexDirection: 'column', gap: '1rem' }}>
      <div className="loader" style={{ width: '40px', height: '40px', borderColor: 'rgba(99, 102, 241, 0.3)', borderTopColor: 'var(--accent-primary)' }}></div>
      <p style={{ color: 'var(--text-secondary)' }}>Compiling MVP Business Case Study...</p>
    </div>
  );

  if (!caseStudy || caseStudy.error) return (
    <div className="glass-card" style={{ textAlign: 'center', padding: '3rem', margin: '2rem' }}>
      <Shield size={48} color="var(--warning)" style={{ marginBottom: '1rem' }} />
      <h3>Business Case Study not ready</h3>
      <p style={{ color: 'var(--text-muted)', marginBottom: '1.5rem' }}>
        Please run the full intelligence pipeline on the Overview tab first to populate MVP metrics.
      </p>
    </div>
  );

  return (
    <div>
      <div className="page-header" style={{ textAlign: 'left' }}>
        <h1 className="page-title text-gradient">MVP Case Study</h1>
        <p className="page-subtitle">A comprehensive PM business case detailing the selected MVP, data-backed rationale, prioritizations, and KPIs.</p>
      </div>

      <div className="grid-2" style={{ gridTemplateColumns: '7fr 5fr', gap: '2rem', textAlign: 'left' }}>
        <div style={{ display: 'flex', flexDirection: 'column', gap: '2rem' }}>
          {/* MVP Selection Banner */}
          <div className="glass-panel" style={{ borderLeft: '4px solid var(--accent-primary)', padding: '2rem' }}>
            <span style={{ fontSize: '0.8rem', color: 'var(--accent-primary)', fontWeight: 'bold', textTransform: 'uppercase' }}>
              Selected Product MVP
            </span>
            <h2 style={{ fontSize: '1.85rem', color: '#fff', margin: '0.25rem 0 0.75rem 0' }}>{caseStudy.mvp_title}</h2>
            <p style={{ fontSize: '1.1rem', color: 'var(--text-primary)', margin: 0, fontStyle: 'italic' }}>
              "{caseStudy.core_value_prop}"
            </p>
            <div style={{ marginTop: '1rem', display: 'flex', gap: '0.5rem', alignItems: 'center' }}>
              <span className="badge badge-info">Target Profile: {caseStudy.target_persona}</span>
            </div>
          </div>

          {/* Rationale & Evidence */}
          <div className="glass-card" style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
            <h3 style={{ margin: 0, color: '#fff', display: 'flex', alignItems: 'center', gap: '8px' }}>
              <FileText size={20} color="var(--accent-secondary)" /> Problem Context & Evidence
            </h3>
            <p style={{ fontSize: '0.9rem', color: 'var(--text-secondary)', lineHeight: '1.5', margin: 0 }}>
              {caseStudy.problem_context}
            </p>

            <h3 style={{ margin: '1rem 0 0 0', color: '#fff', display: 'flex', alignItems: 'center', gap: '8px' }}>
              <Award size={20} color="var(--accent-tertiary)" /> Why This MVP? (PM Justification)
            </h3>
            <p style={{ fontSize: '0.9rem', color: 'var(--text-secondary)', lineHeight: '1.5', margin: 0 }}>
              {caseStudy.why_chosen_rationale}
            </p>
          </div>

          {/* RICE Matrix Table */}
          <div className="glass-card" style={{ padding: 0, overflowX: 'auto' }}>
            <div style={{ padding: '1.25rem 1.5rem', borderBottom: '1px solid var(--border-glass)' }}>
              <h3 style={{ margin: 0, color: '#fff' }}>RICE Prioritization Matrix</h3>
            </div>
            <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: '0.9rem' }}>
              <thead>
                <tr style={{ background: 'rgba(255,255,255,0.02)', borderBottom: '1px solid var(--border-glass)' }}>
                  <th style={{ padding: '0.75rem 1rem', textAlign: 'left', color: 'var(--text-secondary)' }}>Opportunity Solution</th>
                  <th style={{ padding: '0.75rem 1rem', textAlign: 'center', color: 'var(--text-secondary)' }}>Reach (R)</th>
                  <th style={{ padding: '0.75rem 1rem', textAlign: 'center', color: 'var(--text-secondary)' }}>Impact (I)</th>
                  <th style={{ padding: '0.75rem 1rem', textAlign: 'center', color: 'var(--text-secondary)' }}>Confidence (C)</th>
                  <th style={{ padding: '0.75rem 1rem', textAlign: 'center', color: 'var(--text-secondary)' }}>Effort (E)</th>
                  <th style={{ padding: '0.75rem 1rem', textAlign: 'center', color: 'var(--text-secondary)' }}>RICE Score</th>
                </tr>
              </thead>
              <tbody>
                {(caseStudy.rice_matrix || []).map((row, idx) => (
                  <tr key={idx} style={{ borderBottom: '1px solid rgba(255,255,255,0.02)' }}>
                    <td style={{ padding: '1rem', color: '#fff', fontWeight: '500' }}>{row.title}</td>
                    <td style={{ padding: '1rem', textAlign: 'center', color: 'var(--text-secondary)' }}>{row.reach}</td>
                    <td style={{ padding: '1rem', textAlign: 'center', color: 'var(--text-secondary)' }}>{row.impact}</td>
                    <td style={{ padding: '1rem', textAlign: 'center', color: 'var(--text-secondary)' }}>{Math.round(row.confidence * 100)}%</td>
                    <td style={{ padding: '1rem', textAlign: 'center', color: 'var(--text-secondary)' }}>{row.effort}</td>
                    <td style={{ padding: '1rem', textAlign: 'center', color: 'var(--accent-primary)', fontWeight: 'bold' }}>{row.score}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>

        {/* METRICS DASHBOARD & EXPERIMENT DESIGN */}
        <div style={{ display: 'flex', flexDirection: 'column', gap: '2rem' }}>
          {/* KPI Dashboard */}
          <div className="glass-panel" style={{ display: 'flex', flexDirection: 'column', gap: '1.25rem' }}>
            <h3 style={{ margin: 0, color: '#fff', borderBottom: '1px solid var(--border-glass)', paddingBottom: '0.5rem', display: 'flex', alignItems: 'center', gap: '8px' }}>
              <TrendingUp size={20} color="var(--success)" /> Metric Target Dashboard
            </h3>

            {(caseStudy.kpi_metrics || []).map((kpi, idx) => (
              <div key={idx} style={{ background: 'var(--bg-secondary)', padding: '1rem', borderRadius: '8px', borderLeft: '3px solid var(--success)' }}>
                <span className="badge badge-success" style={{ fontSize: '0.75rem', marginBottom: '0.25rem', display: 'inline-block' }}>
                  {kpi.type}
                </span>
                <h4 style={{ margin: '0 0 0.25rem 0', color: '#fff', fontSize: '0.95rem' }}>{kpi.kpi_name}</h4>
                <div style={{ color: 'var(--success)', fontWeight: 'bold', fontSize: '1rem', marginBottom: '0.5rem' }}>
                  Target: {kpi.target_improvement}
                </div>
                <p style={{ margin: 0, fontSize: '0.75rem', color: 'var(--text-muted)' }}>
                  <strong>Measurement:</strong> {kpi.measurement_method}
                </p>
              </div>
            ))}
          </div>

          {/* Experimentation Plan */}
          <div className="glass-card" style={{ display: 'flex', flexDirection: 'column', gap: '1.25rem' }}>
            <h3 style={{ margin: 0, color: '#fff', borderBottom: '1px solid var(--border-glass)', paddingBottom: '0.5rem', display: 'flex', alignItems: 'center', gap: '8px' }}>
              <ListTodo size={20} color="var(--accent-primary)" /> Experiment & Validation Plan
            </h3>

            {/* Phases */}
            <div>
              <span style={{ fontSize: '0.8rem', color: 'var(--accent-primary)', fontWeight: 'bold', display: 'block', marginBottom: '0.5rem' }}>
                Execution Phases
              </span>
              <div style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
                {(caseStudy.experiment_design?.phases || []).map((phase, idx) => (
                  <div key={idx} style={{ display: 'flex', gap: '0.5rem', fontSize: '0.85rem', color: 'var(--text-secondary)' }}>
                    <ArrowRight size={14} style={{ flexShrink: 0, marginTop: '2px' }} />
                    <span>{phase}</span>
                  </div>
                ))}
              </div>
            </div>

            {/* Success Criteria */}
            <div style={{ borderTop: '1px solid rgba(255,255,255,0.03)', paddingTop: '1rem' }}>
              <span style={{ fontSize: '0.8rem', color: 'var(--success)', fontWeight: 'bold', display: 'block', marginBottom: '0.5rem' }}>
                Decision Gate Criteria
              </span>
              <div style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
                {(caseStudy.experiment_design?.success_criteria || []).map((crit, idx) => (
                  <div key={idx} style={{ display: 'flex', gap: '0.5rem', fontSize: '0.85rem', color: 'var(--text-secondary)' }}>
                    <CheckCircle size={14} color="var(--success)" style={{ flexShrink: 0, marginTop: '2px' }} />
                    <span>{crit}</span>
                  </div>
                ))}
              </div>
            </div>

            {/* Risk Mitigation */}
            <div style={{ borderTop: '1px solid rgba(255,255,255,0.03)', paddingTop: '1rem' }}>
              <span style={{ fontSize: '0.8rem', color: 'var(--warning)', fontWeight: 'bold', display: 'block', marginBottom: '0.5rem' }}>
                Critical Risks & Mitigations
              </span>
              <div style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
                {(caseStudy.experiment_design?.risk_mitigation || []).map((risk, idx) => (
                  <p key={idx} style={{ margin: 0, fontSize: '0.85rem', color: 'var(--text-muted)', fontStyle: 'italic' }}>
                    {risk}
                  </p>
                ))}
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default MvpCaseStudy;
