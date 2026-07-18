import React, { useState, useEffect } from 'react';
import { Microscope, HelpCircle, CheckCircle, FileText, Play, Clock, Sparkles, AlertTriangle, Trash2 } from 'lucide-react';
import { getBackendUrl } from '../config';

const ResearchCopilot = () => {
  const [hypotheses, setHypotheses] = useState(null);
  const [questions, setQuestions] = useState(null);
  const [loading, setLoading] = useState(true);
  const [scriptCopied, setScriptCopied] = useState(false);
  const [generatedScript, setGeneratedScript] = useState('');

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

  const handleDownloadMarkdown = () => {
    if (!questions || !hypotheses) return;

    let md = `# Pulse Intelligence - User Research Guide\nGenerated on ${new Date().toLocaleDateString()}\n\n## Part 1: Product Hypotheses\nThese testable hypotheses are derived from app reviews and Reddit consumer signals:\n\n`;

    hypotheses.hypotheses.forEach((h, idx) => {
      md += `### Hypothesis ${idx + 1}: ${h.statement}\n- **Rationale**: ${h.rationale}\n- **Confidence**: ${Math.round(h.confidence * 100)}%\n- **Validation Method**: ${h.validation_method}\n\n`;
    });

    md += `\n## Part 2: "Mom Test" Interview Guide\nThe following optimized questions are designed to gather objective facts about past user behavior without leading the subject:\n\n`;
    md += `**Quality Score**: ${questions.quality_score}/100\n`;
    md += `**Estimated Duration**: ${questions.estimated_duration}\n\n`;

    if (questions.optimized_script && questions.optimized_script.length > 0) {
      questions.optimized_script.forEach((q, idx) => {
        md += `${idx + 1}. **${q.optimized_question}**\n`;
        md += `   - *Original draft*: ${q.original_question}\n`;
        md += `   - *Issues identified*: ${q.issues.join(', ') || 'None'}\n`;
        md += `   - *Validates Hypothesis*: ${q.validated_hypothesis}\n`;
        md += `   - *Supports Decision*: ${q.decision_supported}\n\n`;
      });
    }

    if (questions.removed_questions && questions.removed_questions.length > 0) {
      md += `\n## Part 3: Removed Draft Questions (Mom Test Violations)\n`;
      questions.removed_questions.forEach((q, idx) => {
        md += `- **Draft**: ${q.question}\n  - *Reason for removal*: ${q.reason}\n`;
      });
    }

    if (questions.recommendations && questions.recommendations.length > 0) {
      md += `\n## Part 4: Recommendations for the Interviewer\n`;
      questions.recommendations.forEach((r) => {
        md += `- ${r}\n`;
      });
    }

    const blob = new Blob([md], { type: 'text/markdown;charset=utf-8;' });
    const link = document.createElement("a");
    link.href = URL.createObjectURL(blob);
    link.setAttribute("download", "User_Research_Mom_Test_Guide.md");
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  const handleCopyAppsScript = () => {
    if (!questions) return;

    const optimizedScript = questions.optimized_script || [];

    const formQuestions = optimizedScript.map(q => {
      return `  // Validates Hypothesis: ${q.validated_hypothesis}\n  // Supports Decision: ${q.decision_supported}\n  var item = form.addParagraphTextItem();\n  item.setTitle(${JSON.stringify(q.optimized_question)});\n  item.setHelpText(${JSON.stringify(`Purpose: To validate hypothesis: ${q.validated_hypothesis}`)});\n  item.setRequired(true);`;
    }).join('\n\n');

    const script = `function createGoogleForm() {
  var form = FormApp.create('Pulse Intel - Mom Test User Interview Form');
  form.setDescription('Mom Test User Interview Questionnaire generated automatically by Pulse Intelligence from consumer signals.\\n\\nAnswer honestly about your past experiences.');
  
  form.setCollectEmail(false);
  form.setAllowResponseEdits(false);
  form.setLimitOneResponsePerUser(false);

  // Add Target Persona info field
  var personaItem = form.addMultipleChoiceItem();
  personaItem.setTitle('Which user profile fits you best?');
  personaItem.setChoices([
    personaItem.createChoice('I buy only regular groceries and avoid beauty/electronics'),
    personaItem.createChoice('I regularly explore and buy beauty/electronics on 10-min apps'),
    personaItem.createChoice('I do not use quick commerce apps'),
    personaItem.createChoice('Other')
  ]);
  personaItem.setRequired(true);

${formQuestions}

  Logger.log('Published Form URL: ' + form.getPublishedUrl());
  Logger.log('Editor URL: ' + form.getEditUrl());
}`;

    setGeneratedScript(script);
    navigator.clipboard.writeText(script);
    setScriptCopied(true);
  };

  if (loading) return <div className="loader" style={{ margin: '2rem auto', display: 'block' }}></div>;

  const optimizedQuestions = questions?.optimized_script || [];
  const removedQuestions = questions?.removed_questions || [];
  const recommendations = questions?.recommendations || [];
  const qualityScore = questions?.quality_score || 0;
  const estimatedDuration = questions?.estimated_duration || "15-20 minutes";

  return (
    <div>
      <div className="page-header">
        <h1 className="page-title text-gradient">Research Copilot</h1>
        <p className="page-subtitle">Testable hypotheses and optimized "Mom Test" interview scripts generated from behavioral data.</p>
      </div>

      {/* Export Panel */}
      <div className="glass-card" style={{ marginBottom: '2rem', display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: '1rem', borderLeft: '4px solid var(--accent-primary)', textAlign: 'left' }}>
        <div>
          <h3 style={{ margin: 0, color: '#fff', fontSize: '1.15rem' }}>Research Export & Google Forms Integrator</h3>
          <p style={{ margin: '0.25rem 0 0 0', fontSize: '0.85rem', color: 'var(--text-secondary)' }}>
            Export hypotheses and optimized user interview guides, or build a Google Form via Apps Script.
          </p>
        </div>
        <div style={{ display: 'flex', gap: '0.75rem' }}>
          <button className="btn-secondary" onClick={handleDownloadMarkdown} disabled={!questions || !hypotheses} style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
            <FileText size={16} /> Export Markdown Guide
          </button>
          <button className="btn-primary" onClick={handleCopyAppsScript} disabled={!questions} style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
            <Play size={16} /> Copy Google Forms Script
          </button>
        </div>
      </div>

      {/* Copy Instructions Dialog */}
      {scriptCopied && (
        <div className="glass-panel" style={{ 
          marginBottom: '2rem', 
          background: 'rgba(16, 185, 129, 0.1)', 
          border: '1px solid rgba(16, 185, 129, 0.3)', 
          borderRadius: '8px', 
          padding: '1.25rem',
          textAlign: 'left',
          animation: 'fadeIn 0.3s ease-out'
        }}>
          <h4 style={{ color: 'var(--success)', margin: '0 0 0.5rem 0', display: 'flex', alignItems: 'center', gap: '8px' }}>
            ✅ Google Forms Apps Script Copied to Clipboard!
          </h4>
          <p style={{ color: 'var(--text-secondary)', fontSize: '0.85rem', margin: 0 }}>
            <strong>How to create your Google Form:</strong>
            <ol style={{ margin: '0.5rem 0 0.5rem 0', paddingLeft: '1.2rem', display: 'flex', flexDirection: 'column', gap: '4px' }}>
              <li>Go to <a href="https://script.google.com" target="_blank" rel="noopener noreferrer" style={{ color: 'var(--accent-primary)', textDecoration: 'underline' }}>script.google.com</a> and sign in.</li>
              <li>Click <strong>New Project</strong>.</li>
              <li>Select all default code in the editor, delete it, and paste (Ctrl+V) the copied script.</li>
              <li>Click the 💾 (Save) icon, then click the ▶️ <strong>Run</strong> button at the top.</li>
              <li>Authorize permissions when prompted. The form will be created in your Google Drive!</li>
            </ol>
          </p>

          <div style={{ marginTop: '1.25rem' }}>
            <strong style={{ color: '#fff', display: 'block', marginBottom: '0.5rem', fontSize: '0.85rem' }}>Copied Google Apps Script:</strong>
            <pre style={{ 
              background: '#070a13', 
              color: '#a5b4fc', 
              padding: '1rem', 
              borderRadius: '6px', 
              fontSize: '0.8rem', 
              overflowX: 'auto',
              maxHeight: '180px',
              border: '1px solid rgba(255,255,255,0.05)',
              fontFamily: 'Consolas, Monaco, Courier New, monospace'
            }}>
              {generatedScript}
            </pre>
          </div>

          <button className="btn-secondary" onClick={() => setScriptCopied(false)} style={{ marginTop: '1rem', padding: '0.3rem 0.8rem', fontSize: '0.8rem' }}>
            Close Instructions
          </button>
        </div>
      )}

      <div className="grid-2">
        {/* Hypotheses Column */}
        <div style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem', textAlign: 'left' }}>
          <h2 style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '0.5rem', color: '#fff' }}>
            <Microscope color="var(--accent-primary)" /> Product Hypotheses
          </h2>
          
          {hypotheses?.hypotheses?.map((hyp, idx) => (
            <div key={idx} className="glass-card" style={{ borderLeft: '4px solid var(--accent-secondary)' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '0.5rem' }}>
                <h3 style={{ fontSize: '1.1rem', color: '#fff', margin: 0 }}>Hypothesis {idx + 1}</h3>
                <span className="badge badge-success" style={{ marginLeft: 'auto' }}>{Math.round(hyp.confidence * 100)}% Conf.</span>
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
        <div style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem', textAlign: 'left' }}>
          <h2 style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '0.5rem', color: '#fff' }}>
            <HelpCircle color="var(--accent-tertiary)" /> Mom Test Interview Guide
          </h2>
          
          {/* Dashboard Summary Card */}
          <div className="glass-card" style={{ display: 'flex', gap: '1.5rem', padding: '1rem', flexWrap: 'wrap', background: 'linear-gradient(135deg, rgba(29, 78, 216, 0.1) 0%, rgba(124, 58, 237, 0.1) 100%)', border: '1px solid rgba(255,255,255,0.08)' }}>
            <div style={{ flex: '1 1 120px', display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', borderRight: '1px solid rgba(255,255,255,0.1)', paddingRight: '1rem' }}>
              <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '1px' }}>Quality Score</span>
              <span style={{ fontSize: '2rem', fontWeight: 'bold', color: 'var(--success)', display: 'flex', alignItems: 'center', gap: '4px' }}>
                <Sparkles size={20} color="var(--success)" /> {qualityScore}<span style={{ fontSize: '1rem', color: 'var(--text-muted)' }}>/100</span>
              </span>
            </div>
            
            <div style={{ flex: '1 1 120px', display: 'flex', flexDirection: 'column', justifyContent: 'center' }}>
              <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>Estimated Duration</span>
              <span style={{ fontSize: '1rem', fontWeight: '500', color: '#fff', display: 'flex', alignItems: 'center', gap: '6px', marginTop: '4px' }}>
                <Clock size={16} color="var(--accent-tertiary)" /> {estimatedDuration}
              </span>
            </div>

            <div style={{ flex: '1 1 120px', display: 'flex', flexDirection: 'column', justifyContent: 'center' }}>
              <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>Hypothesis Coverage</span>
              <span style={{ fontSize: '1rem', fontWeight: '500', color: '#fff', display: 'flex', alignItems: 'center', gap: '6px', marginTop: '4px' }}>
                <CheckCircle size={16} color="var(--accent-secondary)" /> {optimizedQuestions.length} Mapped Questions
              </span>
            </div>
          </div>
          
          {/* Questionnaire list */}
          <div className="glass-card" style={{ padding: '0' }}>
            <div style={{ padding: '1.5rem', borderBottom: '1px solid var(--border-glass)' }}>
              <h3 style={{ fontSize: '1.1rem', margin: 0, color: 'var(--text-primary)' }}>Optimized Interview Script</h3>
              <p style={{ fontSize: '0.85rem', color: 'var(--text-muted)', margin: '0.5rem 0 0 0' }}>
                Critically evaluated and rewritten to comply strictly with Mom Test rules (asking about past behavior, not opinions).
              </p>
            </div>
            
            <div style={{ padding: '1.5rem', display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
              {optimizedQuestions.map((q, idx) => (
                <div key={idx} className="glass-panel" style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem', padding: '1rem', background: 'rgba(255,255,255,0.02)', borderRadius: '8px' }}>
                  <div style={{ display: 'flex', gap: '1rem', alignItems: 'flex-start' }}>
                    <div style={{ 
                      width: '28px', height: '28px', borderRadius: '50%', 
                      background: 'var(--bg-secondary)', display: 'flex', alignItems: 'center', justifyContent: 'center',
                      fontWeight: 'bold', color: 'var(--accent-tertiary)', flexShrink: 0, fontSize: '0.85rem'
                    }}>
                      {idx + 1}
                    </div>
                    <div style={{ flex: 1 }}>
                      <p style={{ fontWeight: '600', color: '#fff', margin: '0 0 0.5rem 0', fontSize: '1rem' }}>
                        {q.optimized_question}
                      </p>
                      
                      {/* Hypothesis Tag */}
                      <div style={{ display: 'flex', flexWrap: 'wrap', gap: '0.5rem', marginBottom: '0.75rem' }}>
                        <span className="badge" style={{ background: 'rgba(59, 130, 246, 0.1)', color: '#60a5fa', border: '1px solid rgba(59, 130, 246, 0.2)' }}>
                          🎯 Tests: {q.validated_hypothesis}
                        </span>
                      </div>
                      
                      {/* Audit details */}
                      <div style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem', background: 'rgba(0,0,0,0.2)', padding: '0.75rem', borderRadius: '6px', fontSize: '0.85rem' }}>
                        <div>
                          <span style={{ color: 'var(--text-muted)', display: 'block', fontSize: '0.75rem', textTransform: 'uppercase', marginBottom: '2px' }}>Original Draft</span>
                          <span style={{ color: 'var(--text-secondary)', textDecoration: 'line-through', opacity: 0.6 }}>"{q.original_question}"</span>
                        </div>
                        {q.issues && q.issues.length > 0 && (
                          <div>
                            <span style={{ color: 'var(--text-muted)', display: 'block', fontSize: '0.75rem', textTransform: 'uppercase', marginBottom: '4px' }}>Mom Test Violations Flagged</span>
                            <div style={{ display: 'flex', flexWrap: 'wrap', gap: '0.35rem' }}>
                              {q.issues.map((issue, i) => (
                                <span key={i} className="badge" style={{ background: 'rgba(239, 68, 68, 0.1)', color: '#f87171', fontSize: '0.75rem', display: 'flex', alignItems: 'center', gap: '4px' }}>
                                  <AlertTriangle size={10} /> {issue}
                                </span>
                              ))}
                            </div>
                          </div>
                        )}
                        <div>
                          <span style={{ color: 'var(--text-muted)', display: 'block', fontSize: '0.75rem', textTransform: 'uppercase', marginBottom: '2px' }}>Decision Supported</span>
                          <span style={{ color: 'var(--accent-secondary)' }}>{q.decision_supported}</span>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Removed questions (audit log) */}
          {removedQuestions.length > 0 && (
            <div className="glass-card">
              <h3 style={{ display: 'flex', alignItems: 'center', gap: '8px', color: '#fff', fontSize: '1.1rem', margin: '0 0 1rem 0' }}>
                <Trash2 color="#ef4444" size={18} /> Removed Questions (Mom Test Violations)
              </h3>
              <p style={{ fontSize: '0.85rem', color: 'var(--text-muted)', marginBottom: '1.25rem' }}>
                The following draft questions were rejected by the AI Review Board for violating customer discovery principles.
              </p>
              
              <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
                {removedQuestions.map((q, idx) => (
                  <div key={idx} style={{ display: 'flex', gap: '0.75rem', background: 'rgba(239, 68, 68, 0.03)', border: '1px solid rgba(239, 68, 68, 0.1)', padding: '0.75rem', borderRadius: '6px', fontSize: '0.85rem' }}>
                    <div style={{ flex: 1 }}>
                      <span style={{ fontWeight: '500', color: 'var(--text-secondary)', display: 'block', textDecoration: 'line-through' }}>
                        "{q.question}"
                      </span>
                      <span style={{ color: '#f87171', display: 'block', marginTop: '0.25rem', fontSize: '0.8rem' }}>
                        <strong>Reason:</strong> {q.reason}
                      </span>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Recommendations Panel */}
          {recommendations.length > 0 && (
            <div className="glass-card" style={{ borderLeft: '4px solid var(--success)' }}>
              <h3 style={{ color: '#fff', fontSize: '1.1rem', margin: '0 0 1rem 0', display: 'flex', alignItems: 'center', gap: '6px' }}>
                💡 Interviewer Best Practices
              </h3>
              <ul style={{ margin: 0, paddingLeft: '1.2rem', color: 'var(--text-secondary)', fontSize: '0.9rem', display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
                {recommendations.map((r, idx) => (
                  <li key={idx}>{r}</li>
                ))}
              </ul>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default ResearchCopilot;
