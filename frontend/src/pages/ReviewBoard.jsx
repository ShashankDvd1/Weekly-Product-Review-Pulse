import React, { useState, useEffect } from 'react';
import { Award, ShieldAlert, Sparkles, HelpCircle, Wrench, RefreshCw, FileText, CheckCircle, TrendingUp, Sliders } from 'lucide-react';
import { getBackendUrl } from '../config';

const ReviewBoard = () => {
  const [evaluation, setEvaluation] = useState(null);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState('overview'); // 'overview', 'academic', 'pm', 'investor', 'improvements', 'visuals'

  // Weight Sliders
  const [profWeight, setProfWeight] = useState(35);
  const [pmWeight, setPmWeight] = useState(40);
  const [founderWeight, setFounderWeight] = useState(25);

  useEffect(() => {
    const fetchEvaluation = async () => {
      try {
        setLoading(true);
        const res = await fetch(`${getBackendUrl()}/api/v2/review-board/evaluation`);
        const data = await res.json();
        setEvaluation(data);
      } catch (err) {
        console.error('Error fetching review board evaluation', err);
      } finally {
        setLoading(false);
      }
    };
    fetchEvaluation();
  }, []);

  // Dynamically compile Mermaid charts
  useEffect(() => {
    if (activeTab === 'visuals') {
      const renderMermaid = () => {
        if (window.mermaid) {
          try {
            window.mermaid.initialize({ startOnLoad: false, theme: 'dark', securityLevel: 'loose' });
            window.mermaid.run();
          } catch (e) {
            console.error('Mermaid render error', e);
          }
        } else {
          const script = document.createElement('script');
          script.src = 'https://cdn.jsdelivr.net/npm/mermaid/dist/mermaid.min.js';
          script.async = true;
          script.onload = () => {
            window.mermaid.initialize({ startOnLoad: false, theme: 'dark', securityLevel: 'loose' });
            window.mermaid.run();
          };
          document.body.appendChild(script);
        }
      };
      // Give a tiny timeout for DOM to mount
      const timer = setTimeout(renderMermaid, 200);
      return () => clearTimeout(timer);
    }
  }, [activeTab, evaluation]);

  if (loading) return (
    <div className="flex-center" style={{ height: '80vh', display: 'flex', justifyContent: 'center', alignItems: 'center', flexDirection: 'column', gap: '1rem' }}>
      <div className="loader" style={{ width: '40px', height: '40px', borderColor: 'rgba(99, 102, 241, 0.3)', borderTopColor: 'var(--accent-primary)' }}></div>
      <p style={{ color: 'var(--text-secondary)' }}>Convening Academic & Product Review Board...</p>
    </div>
  );

  if (!evaluation || evaluation.error) return (
    <div className="glass-card" style={{ textAlign: 'center', padding: '3rem', margin: '2rem' }}>
      <ShieldAlert size={48} color="var(--warning)" style={{ marginBottom: '1rem' }} />
      <h3>Review Board is not ready</h3>
      <p style={{ color: 'var(--text-muted)', marginBottom: '1.5rem' }}>
        Please run the full intelligence pipeline on the Overview tab first to populate review board data.
      </p>
    </div>
  );

  // Compute sub-averages
  const getSubAverage = (scorecard) => {
    if (!scorecard || !scorecard.scores || scorecard.scores.length === 0) return 0;
    const total = scorecard.scores.reduce((acc, curr) => acc + curr.score, 0);
    return total / scorecard.scores.length;
  };

  const profAvg = getSubAverage(evaluation.professor_scorecard);
  const pmAvg = getSubAverage(evaluation.pm_scorecard);
  const founderAvg = getSubAverage(evaluation.founder_scorecard);

  // Weight Slider normalization handler
  const handleSliderChange = (type, val) => {
    const value = parseInt(val, 10);
    if (type === 'prof') {
      setProfWeight(value);
      const remaining = 100 - value;
      const sumOthers = pmWeight + founderWeight;
      if (sumOthers > 0) {
        setPmWeight(Math.round((pmWeight / sumOthers) * remaining));
        setFounderWeight(100 - value - Math.round((pmWeight / sumOthers) * remaining));
      } else {
        setPmWeight(Math.round(remaining / 2));
        setFounderWeight(remaining - Math.round(remaining / 2));
      }
    } else if (type === 'pm') {
      setPmWeight(value);
      const remaining = 100 - value;
      const sumOthers = profWeight + founderWeight;
      if (sumOthers > 0) {
        setProfWeight(Math.round((profWeight / sumOthers) * remaining));
        setFounderWeight(100 - value - Math.round((profWeight / sumOthers) * remaining));
      } else {
        setProfWeight(Math.round(remaining / 2));
        setFounderWeight(remaining - Math.round(remaining / 2));
      }
    } else if (type === 'founder') {
      setFounderWeight(value);
      const remaining = 100 - value;
      const sumOthers = profWeight + pmWeight;
      if (sumOthers > 0) {
        setProfWeight(Math.round((profWeight / sumOthers) * remaining));
        setPmWeight(100 - value - Math.round((profWeight / sumOthers) * remaining));
      } else {
        setProfWeight(Math.round(remaining / 2));
        setPmWeight(remaining - Math.round(remaining / 2));
      }
    }
  };

  // Calculate Weighted Score
  const weightedScore = parseFloat(
    ((profAvg * profWeight + pmAvg * pmWeight + founderAvg * founderWeight) / 100).toFixed(2)
  );

  // Score to Letter Grade
  const getLetterGrade = (score) => {
    if (score >= 9.0) return { grade: 'A+', color: 'var(--success)' };
    if (score >= 8.0) return { grade: 'A', color: 'rgba(16, 185, 129, 0.85)' };
    if (score >= 7.0) return { grade: 'B+', color: 'var(--info)' };
    if (score >= 6.0) return { grade: 'B', color: '#fbbf24' };
    if (score >= 5.0) return { grade: 'C', color: '#f97316' };
    return { grade: 'FAIL', color: 'var(--danger)' };
  };

  const letterGrade = getLetterGrade(weightedScore);
  const decisionGo = weightedScore >= 7.5;

  return (
    <div>
      <div className="page-header" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <div>
          <h1 className="page-title text-gradient">AI Product Review Board</h1>
          <p className="page-subtitle">Critique and grade reports from three expert virtual reviewers with dynamic metrics weighting.</p>
        </div>
      </div>

      {/* Tabs */}
      <div style={{ display: 'flex', borderBottom: '1px solid var(--border-glass)', marginBottom: '2rem', overflowX: 'auto', gap: '0.5rem' }}>
        {[
          { id: 'overview', label: 'Overall Decision' },
          { id: 'academic', label: 'Academic (Prof)' },
          { id: 'pm', label: 'Product (PM)' },
          { id: 'investor', label: 'Startup (Founder)' },
          { id: 'visuals', label: 'Visual Assets' },
          { id: 'improvements', label: 'Improvements' },
        ].map(tab => (
          <button
            key={tab.id}
            onClick={() => setActiveTab(tab.id)}
            style={{
              padding: '0.75rem 1.25rem',
              background: activeTab === tab.id ? 'rgba(99, 102, 241, 0.15)' : 'transparent',
              border: 'none',
              borderBottom: activeTab === tab.id ? '2px solid var(--accent-primary)' : '2px solid transparent',
              color: activeTab === tab.id ? '#fff' : 'var(--text-secondary)',
              cursor: 'pointer',
              fontWeight: activeTab === tab.id ? '600' : '400',
              whiteSpace: 'nowrap',
              transition: 'all 0.2s'
            }}
          >
            {tab.label}
          </button>
        ))}
      </div>

      {/* OVERVIEW TAB */}
      {activeTab === 'overview' && (
        <div className="grid-2" style={{ gridTemplateColumns: '3fr 2fr', gap: '2rem', textAlign: 'left' }}>
          {/* Main Grade Banner */}
          <div style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
            <div className="glass-panel" style={{ display: 'flex', gap: '2rem', alignItems: 'center', padding: '2rem', borderRadius: '12px' }}>
              <div style={{ 
                width: '120px', height: '120px', borderRadius: '50%', 
                border: `8px solid ${letterGrade.color}`, display: 'flex', 
                alignItems: 'center', justifyContent: 'center', flexDirection: 'column',
                boxShadow: `0 0 20px ${letterGrade.color}33`
              }}>
                <span style={{ fontSize: '3rem', fontWeight: '800', color: '#fff', lineHeight: '1' }}>{letterGrade.grade}</span>
                <span style={{ fontSize: '0.75rem', color: 'var(--text-secondary)', fontWeight: 'bold' }}>GRADE</span>
              </div>

              <div>
                <h3 style={{ margin: '0 0 0.5rem 0', color: '#fff', fontSize: '1.5rem' }}>
                  Weighted Committee Score: <span style={{ color: letterGrade.color }}>{weightedScore} / 10</span>
                </h3>
                <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '0.5rem' }}>
                  <span className="badge" style={{ background: decisionGo ? 'rgba(16, 185, 129, 0.15)' : 'rgba(239, 68, 68, 0.15)', color: decisionGo ? 'var(--success)' : 'var(--danger)', fontSize: '0.9rem', padding: '0.4rem 0.8rem' }}>
                    {decisionGo ? '🟢 GO (Approved for Build)' : '🔴 NO-GO (Needs Refinement)'}
                  </span>
                </div>
                <p style={{ color: 'var(--text-secondary)', fontSize: '0.85rem', margin: 0 }}>
                  Calculated dynamically from the weighted scores of your Academic, Product Management, and Startup Investor reviews.
                </p>
              </div>
            </div>

            {/* Individual Reviewer Overview Cards */}
            <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
              {[
                { name: 'Dr. Sarah Sterling', title: 'Academic Reviewer', avg: profAvg, feedback: evaluation.professor_scorecard.overall_reviewer_feedback, color: 'var(--accent-primary)' },
                { name: 'Alex Chen', title: 'Product Reviewer', avg: pmAvg, feedback: evaluation.pm_scorecard.overall_reviewer_feedback, color: 'var(--accent-secondary)' },
                { name: 'Marcus Vance', title: 'Investor Reviewer', avg: founderAvg, feedback: evaluation.founder_scorecard.overall_reviewer_feedback, color: 'var(--accent-tertiary)' },
              ].map((rev, idx) => (
                <div key={idx} className="glass-card" style={{ display: 'grid', gridTemplateColumns: '1fr 5fr', gap: '1.5rem', borderLeft: `4px solid ${rev.color}` }}>
                  <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', background: 'rgba(255,255,255,0.02)', borderRadius: '6px', padding: '0.5rem' }}>
                    <span style={{ fontSize: '1.75rem', fontWeight: '800', color: '#fff' }}>{rev.avg.toFixed(1)}</span>
                    <span style={{ fontSize: '0.7rem', color: 'var(--text-muted)' }}>SCORE</span>
                  </div>
                  <div>
                    <h4 style={{ margin: '0 0 0.25rem 0', color: '#fff' }}>{rev.name} <span style={{ fontSize: '0.8rem', color: 'var(--text-secondary)', fontWeight: 'normal' }}>({rev.title})</span></h4>
                    <p style={{ margin: 0, fontSize: '0.85rem', color: 'var(--text-secondary)', fontStyle: 'italic' }}>
                      "{rev.feedback}"
                    </p>
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Side Weights Slider controls */}
          <div className="glass-panel" style={{ height: 'fit-content', padding: '1.5rem', borderRadius: '12px' }}>
            <h3 style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', borderBottom: '1px solid var(--border-glass)', paddingBottom: '0.5rem', margin: '0 0 1.5rem 0', color: '#fff' }}>
              <Sliders size={20} color="var(--accent-primary)" /> Dynamic Weight Panel
            </h3>

            <div style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
              <div>
                <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '0.5rem', fontSize: '0.9rem' }}>
                  <span style={{ color: 'var(--text-primary)', fontWeight: '600' }}>Academic Board (Prof)</span>
                  <span style={{ color: 'var(--accent-primary)', fontWeight: 'bold' }}>{profWeight}%</span>
                </div>
                <input 
                  type="range" min="0" max="100" value={profWeight} 
                  onChange={(e) => handleSliderChange('prof', e.target.value)}
                  style={{ width: '100%', cursor: 'pointer' }}
                />
              </div>

              <div>
                <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '0.5rem', fontSize: '0.9rem' }}>
                  <span style={{ color: 'var(--text-primary)', fontWeight: '600' }}>Product Board (PM)</span>
                  <span style={{ color: 'var(--accent-secondary)', fontWeight: 'bold' }}>{pmWeight}%</span>
                </div>
                <input 
                  type="range" min="0" max="100" value={pmWeight} 
                  onChange={(e) => handleSliderChange('pm', e.target.value)}
                  style={{ width: '100%', cursor: 'pointer' }}
                />
              </div>

              <div>
                <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '0.5rem', fontSize: '0.9rem' }}>
                  <span style={{ color: 'var(--text-primary)', fontWeight: '600' }}>Investor Board (Founder)</span>
                  <span style={{ color: 'var(--accent-tertiary)', fontWeight: 'bold' }}>{founderWeight}%</span>
                </div>
                <input 
                  type="range" min="0" max="100" value={founderWeight} 
                  onChange={(e) => handleSliderChange('founder', e.target.value)}
                  style={{ width: '100%', cursor: 'pointer' }}
                />
              </div>

              <div style={{ borderTop: '1px solid var(--border-glass)', paddingTop: '1rem', marginTop: '0.5rem', textAlign: 'center', fontSize: '0.8rem', color: 'var(--text-muted)' }}>
                Sum of weights: {profWeight + pmWeight + founderWeight}% (Auto-Normalized)
              </div>
            </div>
          </div>
        </div>
      )}

      {/* CORE EVALUATION SCORECARD VIEWS */}
      {(activeTab === 'academic' || activeTab === 'pm' || activeTab === 'investor') && (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem', textAlign: 'left' }}>
          {/* Board Header details */}
          <div className="glass-panel" style={{ borderLeft: '4px solid var(--accent-primary)' }}>
            <h3 style={{ margin: 0, color: '#fff' }}>
              {activeTab === 'academic' && evaluation.professor_scorecard.reviewer_name}
              {activeTab === 'pm' && evaluation.pm_scorecard.reviewer_name}
              {activeTab === 'investor' && evaluation.founder_scorecard.reviewer_name}
            </h3>
            <p style={{ margin: '0.25rem 0 0 0', fontSize: '0.85rem', color: 'var(--text-secondary)' }}>
              <strong>Focus Area: </strong>
              {activeTab === 'academic' && evaluation.professor_scorecard.focus}
              {activeTab === 'pm' && evaluation.pm_scorecard.focus}
              {activeTab === 'investor' && evaluation.founder_scorecard.focus}
            </p>
          </div>

          {/* List of subscores */}
          <div style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
            {(activeTab === 'academic' ? evaluation.professor_scorecard.scores :
              activeTab === 'pm' ? evaluation.pm_scorecard.scores :
              evaluation.founder_scorecard.scores).map((scoreItem, idx) => (
                <div key={idx} className="glass-card" style={{ display: 'grid', gridTemplateColumns: '7fr 3fr', gap: '2rem' }}>
                  <div>
                    <h4 style={{ margin: '0 0 0.5rem 0', fontSize: '1.15rem', color: '#fff' }}>{scoreItem.category}</h4>
                    <p style={{ fontSize: '0.9rem', color: 'var(--text-secondary)', lineHeight: '1.4', marginBottom: '1rem' }}>
                      {scoreItem.reason}
                    </p>

                    <div className="grid-2" style={{ gap: '1rem', marginTop: '0.5rem' }}>
                      {scoreItem.strengths?.length > 0 && (
                        <div style={{ background: 'rgba(16, 185, 129, 0.03)', padding: '0.75rem', borderRadius: '6px', border: '1px solid rgba(16, 185, 129, 0.1)' }}>
                          <span style={{ fontSize: '0.8rem', color: 'var(--success)', fontWeight: 'bold', display: 'block', marginBottom: '0.25rem' }}>Strengths</span>
                          <ul style={{ paddingLeft: '1rem', margin: 0, fontSize: '0.8rem', color: 'var(--text-secondary)' }}>
                            {scoreItem.strengths.map((s, i) => <li key={i}>{s}</li>)}
                          </ul>
                        </div>
                      )}
                      {scoreItem.weaknesses?.length > 0 && (
                        <div style={{ background: 'rgba(239, 68, 68, 0.03)', padding: '0.75rem', borderRadius: '6px', border: '1px solid rgba(239, 68, 68, 0.1)' }}>
                          <span style={{ fontSize: '0.8rem', color: 'var(--danger)', fontWeight: 'bold', display: 'block', marginBottom: '0.25rem' }}>Weaknesses</span>
                          <ul style={{ paddingLeft: '1rem', margin: 0, fontSize: '0.8rem', color: 'var(--text-secondary)' }}>
                            {scoreItem.weaknesses.map((w, i) => <li key={i}>{w}</li>)}
                          </ul>
                        </div>
                      )}
                    </div>
                  </div>

                  <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', background: 'rgba(255,255,255,0.01)', borderLeft: '1px solid var(--border-glass)', paddingLeft: '1rem' }}>
                    <div style={{ fontSize: '3rem', fontWeight: '800', color: scoreItem.score >= 8 ? 'var(--success)' : scoreItem.score >= 6 ? '#fbbf24' : 'var(--danger)' }}>
                      {scoreItem.score.toFixed(1)}
                    </div>
                    <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>SCORE / 10</span>

                    {scoreItem.suggestions?.length > 0 && (
                      <div style={{ marginTop: '1rem', width: '100%' }}>
                        <span style={{ fontSize: '0.75rem', color: 'var(--accent-primary)', fontWeight: 'bold', display: 'block', marginBottom: '0.25rem', textAlign: 'center' }}>Board Suggestion</span>
                        <p style={{ fontSize: '0.75rem', color: 'var(--text-muted)', margin: 0, textAlign: 'center', fontStyle: 'italic' }}>
                          "{scoreItem.suggestions[0]}"
                        </p>
                      </div>
                    )}
                  </div>
                </div>
              ))}
          </div>
        </div>
      )}

      {/* VISUAL ASSETS TAB */}
      {activeTab === 'visuals' && (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '2rem', textAlign: 'left' }}>
          <div className="glass-panel" style={{ borderLeft: '4px solid var(--accent-secondary)' }}>
            <h3 style={{ margin: 0, color: '#fff' }}>Board Visualizations & User Flows</h3>
            <p style={{ margin: '0.25rem 0 0 0', fontSize: '0.85rem', color: 'var(--text-secondary)' }}>
              Automatically compiled architecture diagrams, user journey maps, wireframes, and roadmap visualizations.
            </p>
          </div>

          <div className="grid-2" style={{ gap: '2rem' }}>
            {[
              { title: 'User Conversion Decision Tree', code: evaluation.visual_assets?.decision_tree, key: 'dt' },
              { title: 'MVP Category Discovery Wireframe Schema', code: evaluation.visual_assets?.wireframe, key: 'wf' },
              { title: 'Customer Experience Journey Map', code: evaluation.visual_assets?.journey_map, key: 'jm' },
              { title: 'GTM & Feature Milestones Roadmap', code: evaluation.visual_assets?.roadmap, key: 'rm' },
            ].map((chart, i) => (
              <div key={chart.key} className="glass-card" style={{ display: 'flex', flexDirection: 'column', gap: '1rem', minHeight: '350px' }}>
                <h4 style={{ margin: 0, borderBottom: '1px solid var(--border-glass)', paddingBottom: '0.5rem', color: '#fff' }}>
                  {chart.title}
                </h4>
                <div 
                  className="mermaid" 
                  style={{ 
                    flex: 1, 
                    display: 'flex', 
                    alignItems: 'center', 
                    justifyContent: 'center', 
                    background: 'rgba(0,0,0,0.2)', 
                    borderRadius: '8px', 
                    padding: '1rem',
                    overflowX: 'auto'
                  }}
                >
                  {chart.code || 'graph TD\n    A[No Diagram Data]'}
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* IMPROVEMENTS TAB */}
      {activeTab === 'improvements' && (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem', textAlign: 'left' }}>
          <div className="glass-panel" style={{ borderLeft: '4px solid var(--accent-tertiary)' }}>
            <h3 style={{ margin: 0, color: '#fff' }}>Automatic Improvement Report</h3>
            <p style={{ margin: '0.25rem 0 0 0', fontSize: '0.85rem', color: 'var(--text-secondary)' }}>
              Highly critical, prioritized checklist generated by the board to prepare your product solution for accelerator pitch or portfolio review.
            </p>
          </div>

          <div className="glass-card" style={{ padding: '0' }}>
            <div style={{ padding: '1.5rem', borderBottom: '1px solid var(--border-glass)' }}>
              <h4 style={{ margin: 0, color: '#fff' }}>Top 10 Board Recommendations</h4>
            </div>

            <div style={{ padding: '1.5rem', display: 'flex', flexDirection: 'column', gap: '1.25rem' }}>
              {(evaluation.improvement_report || []).map((imp, idx) => (
                <div key={idx} style={{ display: 'flex', gap: '1rem', alignItems: 'flex-start' }}>
                  <div style={{ 
                    width: '28px', height: '28px', borderRadius: '50%', 
                    background: 'rgba(99, 102, 241, 0.15)', display: 'flex', alignItems: 'center', justifyContent: 'center',
                    fontWeight: 'bold', color: 'var(--accent-primary)', flexShrink: 0, fontSize: '0.85rem'
                  }}>
                    {idx + 1}
                  </div>
                  <div style={{ paddingTop: '2px' }}>
                    <p style={{ fontSize: '0.95rem', color: '#fff', margin: 0, lineHeight: '1.4' }}>{imp}</p>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default ReviewBoard;
