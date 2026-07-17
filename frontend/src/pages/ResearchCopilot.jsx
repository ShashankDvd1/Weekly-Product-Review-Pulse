import React, { useState, useEffect } from 'react';
import { Microscope, HelpCircle, CheckCircle, FileText, Play } from 'lucide-react';
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

    md += `\n## Part 2: "Mom Test" Interview Guide\nThe following open-ended questions are designed to gather objective facts about past user behavior without leading the subject:\n\n`;

    questions.questions.forEach((q, idx) => {
      md += `${idx + 1}. **${q.question}**\n   - *Question Type*: ${q.question_type}\n   - *Target Persona*: ${q.target_persona || 'All Users'}\n   - *Research Purpose*: ${q.purpose}\n\n`;
    });

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

    const formQuestions = questions.questions.map(q => `  // ${q.question_type} Question\n  var item = form.addParagraphTextItem();\n  item.setTitle(${JSON.stringify(q.question)});\n  item.setHelpText(${JSON.stringify(`Purpose: ${q.purpose}`)});\n  item.setRequired(true);`).join('\n\n');

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

  return (
    <div>
      <div className="page-header">
        <h1 className="page-title text-gradient">Research Copilot</h1>
        <p className="page-subtitle">Testable hypotheses and "Mom Test" interview questions generated from behavioral data.</p>
      </div>

      {/* Export Panel */}
      <div className="glass-card" style={{ marginBottom: '2rem', display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: '1rem', borderLeft: '4px solid var(--accent-primary)', textAlign: 'left' }}>
        <div>
          <h3 style={{ margin: 0, color: '#fff', fontSize: '1.15rem' }}>Research Export & Google Forms Integrator</h3>
          <p style={{ margin: '0.25rem 0 0 0', fontSize: '0.85rem', color: 'var(--text-secondary)' }}>
            Export hypotheses and user interview questions, or generate a Google Form via Apps Script.
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
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '0.5rem' }}>
                <h3 style={{ fontSize: '1.1rem', color: '#fff', margin: 0 }}>Hypothesis {idx + 1}</h3>
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
        <div style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem', textAlign: 'left' }}>
          <h2 style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '0.5rem', color: '#fff' }}>
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
