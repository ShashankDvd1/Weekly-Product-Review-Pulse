import { useState, useEffect } from 'react';
import { Play, Send, CheckCircle, Award, Compass, AlertCircle, RefreshCw, Star, BarChart3, HelpCircle } from 'lucide-react';
import { getBackendUrl } from '../config';

const VivaDefense = () => {
  const [active, setActive] = useState(false);
  const [length, setLength] = useState(10);
  const [currentQuestion, setCurrentQuestion] = useState(null);
  const [currentIndex, setCurrentIndex] = useState(0);
  const [totalQuestions, setTotalQuestions] = useState(0);
  const [userAnswer, setUserAnswer] = useState('');
  const [loading, setLoading] = useState(false);
  const [feedbacks, setFeedbacks] = useState([]);
  const [completed, setCompleted] = useState(false);
  const [vivaSummary, setVivaSummary] = useState(null);

  const startDefense = async (selectedLength) => {
    try {
      setLoading(true);
      const res = await fetch(`${getBackendUrl()}/api/v2/review-board/viva/start`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ length: selectedLength })
      });
      const data = await res.json();
      setCurrentQuestion(data.question);
      setCurrentIndex(data.current_index);
      setTotalQuestions(data.total_questions);
      setActive(true);
      setCompleted(false);
      setFeedbacks([]);
      setUserAnswer('');
    } catch (err) {
      console.error('Error starting viva session', err);
    } finally {
      setLoading(false);
    }
  };

  const submitAnswer = async () => {
    if (!userAnswer.trim()) return;

    try {
      setLoading(true);
      const res = await fetch(`${getBackendUrl()}/api/v2/review-board/viva/answer`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ answer: userAnswer })
      });
      const data = await res.json();

      const newFeedback = {
        question: currentQuestion.question,
        answer: userAnswer,
        evaluation: data.evaluation
      };
      setFeedbacks(prev => [...prev, newFeedback]);

      if (data.completed) {
        setCompleted(true);
        setActive(false);
        setVivaSummary(data.evaluation.viva_summary);
      } else {
        setCurrentQuestion(data.next_question);
        setCurrentIndex(data.current_index);
        setUserAnswer('');
      }
    } catch (err) {
      console.error('Error submitting answer', err);
    } finally {
      setLoading(false);
    }
  };

  const getDifficultyColor = (diff) => {
    if (diff === 'easy') return 'var(--success)';
    if (diff === 'medium') return 'var(--info)';
    return 'var(--danger)';
  };

  if (loading && feedbacks.length === 0) return (
    <div className="flex-center" style={{ height: '80vh', display: 'flex', justifyContent: 'center', alignItems: 'center', flexDirection: 'column', gap: '1rem' }}>
      <div className="loader" style={{ width: '40px', height: '40px', borderColor: 'rgba(99, 102, 241, 0.3)', borderTopColor: 'var(--accent-primary)' }}></div>
      <p style={{ color: 'var(--text-secondary)' }}>Configuring Viva Defense Panel...</p>
    </div>
  );

  return (
    <div>
      <div className="page-header" style={{ textAlign: 'left' }}>
        <h1 className="page-title text-gradient">🎤 Product Viva & Defense</h1>
        <p className="page-subtitle">Defend your product opportunity analysis under critical mock interview grilling.</p>
      </div>

      {/* START SCREEN */}
      {!active && !completed && (
        <div className="glass-card" style={{ maxWidth: '600px', margin: '2rem auto', textAlign: 'center', padding: '3rem' }}>
          <Compass size={48} color="var(--accent-primary)" style={{ marginBottom: '1.5rem' }} />
          <h2 style={{ color: '#fff', marginBottom: '1rem' }}>Board Interview Mode</h2>
          <p style={{ color: 'var(--text-secondary)', fontSize: '0.95rem', lineHeight: '1.6', marginBottom: '2rem' }}>
            Choose your session length. The committee will evaluate your reasoning, business logic, data interpretation, and communication, escalating difficulty as the defense progresses.
          </p>

          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr 1fr', gap: '1rem', marginBottom: '2.5rem' }}>
            {[
              { label: 'Short (5 q)', val: 5, desc: 'Quick check' },
              { label: 'Standard (10 q)', val: 10, desc: 'Recommended' },
              { label: 'Full Board (15 q)', val: 15, desc: 'Extreme grill' },
            ].map(item => (
              <button
                key={item.val}
                onClick={() => setLength(item.val)}
                style={{
                  background: length === item.val ? 'rgba(99, 102, 241, 0.15)' : 'var(--bg-secondary)',
                  border: length === item.val ? '2px solid var(--accent-primary)' : '1px solid var(--border-glass)',
                  borderRadius: '8px',
                  padding: '1rem 0.5rem',
                  color: '#fff',
                  cursor: 'pointer',
                  transition: 'all 0.2s'
                }}
              >
                <div style={{ fontWeight: 'bold', fontSize: '1rem', marginBottom: '0.2rem' }}>{item.label}</div>
                <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>{item.desc}</div>
              </button>
            ))}
          </div>

          <button className="btn-primary" onClick={() => startDefense(length)} style={{ width: '100%', padding: '0.8rem', gap: '0.5rem' }}>
            <Play size={18} /> Start Defense
          </button>
        </div>
      )}

      {/* ACTIVE INTERVIEW SCREEN */}
      {active && currentQuestion && (
        <div className="grid-2" style={{ gridTemplateColumns: '5fr 3fr', gap: '2rem', textAlign: 'left' }}>
          {/* Chat Messenger log */}
          <div className="glass-panel" style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem', height: '650px', background: '#090e18' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', borderBottom: '1px solid var(--border-glass)', paddingBottom: '0.75rem', fontSize: '0.9rem', color: 'var(--text-secondary)' }}>
              <span>Committee Question {currentIndex + 1} of {totalQuestions}</span>
              <span className="badge" style={{ background: 'rgba(255,255,255,0.05)', color: getDifficultyColor(currentQuestion.difficulty) }}>
                {currentQuestion.difficulty.toUpperCase()}
              </span>
            </div>

            {/* Message log body */}
            <div style={{ flex: 1, overflowY: 'auto', display: 'flex', flexDirection: 'column', gap: '1.5rem', paddingRight: '0.5rem' }}>
              {/* If no chats yet */}
              {feedbacks.length === 0 && (
                <div style={{ textAlign: 'center', padding: '3rem', color: 'var(--text-muted)' }}>
                  Submit your first response to trigger reviewer feedback.
                </div>
              )}

              {feedbacks.map((f, i) => (
                <div key={i} style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
                  {/* AI Question */}
                  <div style={{ background: 'rgba(99, 102, 241, 0.05)', borderLeft: '3px solid var(--accent-primary)', padding: '1rem', borderRadius: '0 8px 8px 0' }}>
                    <span style={{ fontSize: '0.75rem', color: 'var(--accent-primary)', fontWeight: 'bold', display: 'block', marginBottom: '0.25rem' }}>BOARD REVIEWER</span>
                    <p style={{ margin: 0, color: '#fff', fontSize: '0.9rem' }}>{f.question}</p>
                  </div>

                  {/* Candidate Answer */}
                  <div style={{ background: 'rgba(255, 255, 255, 0.02)', borderRight: '3px solid var(--text-muted)', padding: '1rem', borderRadius: '8px 0 0 8px', alignSelf: 'flex-end', maxWidth: '90%' }}>
                    <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)', fontWeight: 'bold', display: 'block', marginBottom: '0.25rem', textAlign: 'right' }}>YOU</span>
                    <p style={{ margin: 0, color: '#cbd5e1', fontSize: '0.9rem', textAlign: 'right' }}>{f.answer}</p>
                  </div>

                  {/* AI Inline Feedback */}
                  <div className="glass-card" style={{ background: 'rgba(16, 185, 129, 0.02)', border: '1px solid rgba(16, 185, 129, 0.1)', padding: '1.25rem' }}>
                    <div style={{ display: 'flex', justifyContent: 'space-between', borderBottom: '1px solid rgba(255,255,255,0.05)', paddingBottom: '0.5rem', marginBottom: '0.75rem' }}>
                      <span style={{ fontSize: '0.8rem', color: 'var(--success)', fontWeight: 'bold' }}>Reviewer Evaluation Score</span>
                      <span style={{ fontSize: '1rem', color: '#fff', fontWeight: 'bold' }}>{f.evaluation.score} / 10</span>
                    </div>

                    <p style={{ margin: '0 0 1rem 0', fontSize: '0.85rem', color: 'var(--text-secondary)', lineHeight: '1.4' }}>
                      {f.evaluation.clarity}
                    </p>

                    <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '0.5rem', fontSize: '0.8rem', color: 'var(--text-muted)', marginBottom: '1rem' }}>
                      <div>Communication: <span style={{ color: '#fff' }}>{f.evaluation.communication_score}</span></div>
                      <div>Product Logic: <span style={{ color: '#fff' }}>{f.evaluation.logic_score}</span></div>
                      <div>Product Thinking: <span style={{ color: '#fff' }}>{f.evaluation.product_thinking_score}</span></div>
                      <div>Business Thinking: <span style={{ color: '#fff' }}>{f.evaluation.business_thinking_score}</span></div>
                    </div>

                    {f.evaluation.suggestions?.length > 0 && (
                      <div>
                        <span style={{ fontSize: '0.75rem', color: 'var(--accent-primary)', fontWeight: 'bold', display: 'block', marginBottom: '0.25rem' }}>Recommendations for Improvement</span>
                        <ul style={{ paddingLeft: '1.2rem', margin: 0, fontSize: '0.75rem', color: 'var(--text-muted)' }}>
                          {f.evaluation.suggestions.map((s, idx) => <li key={idx}>{s}</li>)}
                        </ul>
                      </div>
                    )}
                  </div>
                </div>
              ))}
            </div>

            {/* Answer Input Frame */}
            <div style={{ borderTop: '1px solid var(--border-glass)', paddingTop: '1rem' }}>
              <div style={{ display: 'flex', gap: '0.75rem' }}>
                <textarea
                  value={userAnswer}
                  onChange={(e) => setUserAnswer(e.target.value)}
                  placeholder="Type your defense answer here..."
                  disabled={loading}
                  style={{
                    flex: 1,
                    height: '60px',
                    background: 'var(--bg-secondary)',
                    border: '1px solid var(--border-glass)',
                    borderRadius: '6px',
                    color: '#fff',
                    padding: '0.75rem',
                    outline: 'none',
                    resize: 'none',
                    fontSize: '0.9rem'
                  }}
                />
                <button
                  className="btn-primary"
                  onClick={submitAnswer}
                  disabled={loading || !userAnswer.trim()}
                  style={{ width: '60px', padding: 0, display: 'flex', alignItems: 'center', justifyContent: 'center' }}
                >
                  <Send size={18} />
                </button>
              </div>
            </div>
          </div>

          {/* Current Question Focus Sidebar */}
          <div style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
            <div className="glass-panel" style={{ borderLeft: `4px solid ${getDifficultyColor(currentQuestion.difficulty)}` }}>
              <span className="badge" style={{ background: 'rgba(255,255,255,0.05)', color: getDifficultyColor(currentQuestion.difficulty), marginBottom: '0.5rem', display: 'inline-block' }}>
                Active Question
              </span>
              <h3 style={{ margin: '0 0 1rem 0', color: '#fff', fontSize: '1.2rem', lineHeight: '1.4' }}>{currentQuestion.question}</h3>

              <div style={{ background: 'var(--bg-secondary)', padding: '1rem', borderRadius: '8px', marginBottom: '1rem', fontSize: '0.85rem' }}>
                <strong style={{ color: 'var(--accent-primary)', display: 'block', marginBottom: '0.25rem' }}>Why are we asking this?</strong>
                <p style={{ color: 'var(--text-secondary)', margin: 0 }}>{currentQuestion.purpose}</p>
              </div>

              <div style={{ background: 'var(--bg-secondary)', padding: '1rem', borderRadius: '8px', fontSize: '0.85rem' }}>
                <strong style={{ color: 'var(--success)', display: 'block', marginBottom: '0.25rem' }}>Expected response criteria:</strong>
                <p style={{ color: 'var(--text-secondary)', margin: 0 }}>{currentQuestion.expected_direction}</p>
              </div>
            </div>

            <button 
              className="btn-secondary" 
              onClick={() => { setActive(false); setCompleted(false); }}
              style={{ gap: '0.5rem', color: 'var(--danger)' }}
            >
              <AlertCircle size={16} /> Exit Viva Session
            </button>
          </div>
        </div>
      )}

      {/* FINAL SCORECARD / COMPLETE SCREEN */}
      {completed && vivaSummary && (
        <div style={{ maxWidth: '800px', margin: '2rem auto', textAlign: 'left' }}>
          <div className="glass-panel" style={{ textAlign: 'center', padding: '3rem', borderLeft: '4px solid var(--accent-primary)' }}>
            <Award size={48} color="var(--accent-primary)" style={{ margin: '0 auto 1rem auto', display: 'block' }} />
            <h2 style={{ color: '#fff', margin: '0 0 0.5rem 0' }}>Viva Defense Completed!</h2>
            <p style={{ color: 'var(--text-secondary)', margin: '0 0 2rem 0' }}>The review board has compiled your final candidate score.</p>

            <div style={{ display: 'flex', gap: '3rem', justifyContent: 'center', alignItems: 'center', marginBottom: '2rem' }}>
              <div>
                <span style={{ fontSize: '3rem', fontWeight: '800', color: '#fff' }}>
                  {vivaSummary.average_score.toFixed(1)} / 10
                </span>
                <span style={{ display: 'block', fontSize: '0.75rem', color: 'var(--text-muted)', marginTop: '0.25rem' }}>AVERAGE DEFENSE SCORE</span>
              </div>

              <div style={{ borderLeft: '1px solid var(--border-glass)', height: '60px' }}></div>

              <div>
                <span className="badge badge-success" style={{ padding: '0.5rem 1rem', fontSize: '1rem' }}>
                  {vivaSummary.average_score >= 8.0 ? 'PORTFOLIO READY' : 'REFINEMENT RECOMMENDED'}
                </span>
                <span style={{ display: 'block', fontSize: '0.75rem', color: 'var(--text-muted)', marginTop: '0.5rem' }}>COMMITTEE STATUS</span>
              </div>
            </div>

            <button className="btn-primary" onClick={() => { setCompleted(false); setActive(false); }} style={{ margin: '0 auto', gap: '0.5rem' }}>
              <RefreshCw size={16} /> Restart New Defense
            </button>
          </div>

          <h3 style={{ marginTop: '2rem', color: '#fff', borderBottom: '1px solid var(--border-glass)', paddingBottom: '0.5rem' }}>
            Answer Summary & Criticisms
          </h3>

          <div style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem', marginTop: '1.5rem' }}>
            {feedbacks.map((f, i) => (
              <div key={i} className="glass-card" style={{ borderLeft: '4px solid var(--accent-secondary)' }}>
                <h4 style={{ margin: '0 0 0.5rem 0', color: '#fff' }}>Question {i + 1}: {f.question}</h4>
                <p style={{ fontSize: '0.85rem', color: 'var(--text-muted)', margin: '0 0 1rem 0' }}>
                  <strong>Your response: </strong>"{f.answer}"
                </p>

                <div style={{ background: 'var(--bg-secondary)', padding: '1rem', borderRadius: '8px', fontSize: '0.85rem' }}>
                  <strong style={{ color: 'var(--accent-primary)', display: 'block', marginBottom: '0.25rem' }}>Reviewer Critique:</strong>
                  <p style={{ color: 'var(--text-secondary)', margin: '0 0 0.5rem 0' }}>{f.evaluation.clarity}</p>
                  <strong style={{ color: 'var(--warning)', display: 'block', marginBottom: '0.25rem' }}>Improvement Suggestions:</strong>
                  <ul style={{ paddingLeft: '1.2rem', margin: 0, color: 'var(--text-muted)' }}>
                    {f.evaluation.suggestions.map((s, idx) => <li key={idx}>{s}</li>)}
                  </ul>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};

export default VivaDefense;
