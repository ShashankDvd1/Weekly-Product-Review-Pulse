import React, { useState, useEffect } from 'react';
import { Presentation, Download, ArrowLeft, ArrowRight, Play, CheckSquare, ListTodo, AlertTriangle, TrendingUp, Landmark } from 'lucide-react';
import { getBackendUrl } from '../config';
import pptxgen from 'pptxgenjs';

const ExecutiveDeck = () => {
  const [slides, setSlides] = useState([]);
  const [loading, setLoading] = useState(true);
  const [currentSlideIndex, setCurrentSlideIndex] = useState(0);

  useEffect(() => {
    const fetchDeckData = async () => {
      try {
        setLoading(true);
        const res = await fetch(`${getBackendUrl()}/api/v2/reports/executive-deck`);
        const data = await res.json();
        setSlides(data.slides || []);
      } catch (err) {
        console.error('Error fetching executive deck', err);
      } finally {
        setLoading(false);
      }
    };
    fetchDeckData();
  }, []);

  const handleNextSlide = () => {
    if (currentSlideIndex < slides.length - 1) {
      setCurrentSlideIndex(prev => prev + 1);
    }
  };

  const handlePrevSlide = () => {
    if (currentSlideIndex > 0) {
      setCurrentSlideIndex(prev => prev - 1);
    }
  };

  // PPTX Export using pptxgenjs
  const exportPPTX = () => {
    if (slides.length === 0) return;
    const pptx = new pptxgen();

    pptx.defineLayout({ name: 'custom', width: 13.33, height: 7.5 });
    pptx.layout = 'custom';

    slides.forEach((slide) => {
      let pptxSlide = pptx.addSlide();
      
      // Theme colors
      const PRIMARY_NAVY = '0B1E36';
      const SECONDARY_BLUE = '1E3A8A';
      const WHITE = 'FFFFFF';
      const GRAY_TEXT = '4B5563';
      const LIGHT_BG = 'F8FAFC';

      // Background color
      pptxSlide.background = { color: LIGHT_BG };

      // Header Banner
      pptxSlide.addShape(pptx.shapes.RECTANGLE, { x: 0, y: 0, w: 13.33, h: 1.0, fill: { color: PRIMARY_NAVY } });
      
      // Title
      pptxSlide.addText(slide.title.toUpperCase(), { 
        x: 0.5, y: 0.2, w: 12.33, h: 0.6, 
        fontSize: 22, bold: true, color: WHITE, valign: 'middle' 
      });

      // Subtitle / Headline
      pptxSlide.addText(slide.headline, { 
        x: 0.5, y: 1.2, w: 12.33, h: 0.5, 
        fontSize: 16, italic: true, color: SECONDARY_BLUE, bold: true 
      });

      // Key Metrics (as callout boxes on the left)
      if (slide.key_metrics && slide.key_metrics.length > 0) {
        slide.key_metrics.forEach((metric, index) => {
          const yPos = 1.9 + (index * 1.6);
          // Metric Box Background
          pptxSlide.addShape(pptx.shapes.RECTANGLE, { 
            x: 0.5, y: yPos, w: 3.2, h: 1.3, 
            fill: { color: 'E2E8F0' }, line: { color: 'CBD5E1', width: 1 } 
          });
          // Value
          pptxSlide.addText(String(metric.value), { 
            x: 0.6, y: yPos + 0.1, w: 3.0, h: 0.5, 
            fontSize: 28, bold: true, color: PRIMARY_NAVY, align: 'center' 
          });
          // Label
          pptxSlide.addText(metric.label, { 
            x: 0.6, y: yPos + 0.65, w: 3.0, h: 0.5, 
            fontSize: 11, color: GRAY_TEXT, align: 'center' 
          });
        });
      }

      // Slide content text / details
      let contentString = '';
      if (slide.slide_number === 3 && slide.mvp_details) {
        const details = slide.mvp_details;
        contentString = `• TARGET USERS: ${details.target_users}\n• PAIN POINTS: ${details.pain_points}\n• PROPOSED SOLUTION: ${details.proposed_solution}\n• CORE FEATURES: ${(details.core_features || []).join(', ')}\n• METRICS: ${(details.success_metrics || []).join(', ')}`;
      } else if (Array.isArray(slide.content)) {
        contentString = slide.content.map(p => `• ${p}`).join('\n\n');
      } else if (typeof slide.content === 'string') {
        contentString = slide.content;
      }

      pptxSlide.addText(contentString, { 
        x: 4.2, y: 1.9, w: 8.5, h: 4.8, 
        fontSize: 13, color: '1E293B', fontFace: 'Calibri', valign: 'top', lineSpacing: 22 
      });

      // Speaker Notes
      let speakerText = '';
      if (slide.speaker_notes) {
        speakerText = `TALK TRACK:\n${slide.speaker_notes.what_to_say || ''}\n\nSTRATEGIC CONTEXT:\n${slide.speaker_notes.why_it_matters || ''}\n\nEXPECTED QUESTIONS & ANSWERS:\nQ: ${slide.speaker_notes.audience_question || ''}\nA: ${slide.speaker_notes.suggested_answer || ''}`;
      }
      pptxSlide.notes = speakerText;
    });

    pptx.writeFile({ fileName: 'AI_Executive_Insight_Deck.pptx' });
  };

  // Marp Markdown Export
  const exportMarpMarkdown = () => {
    if (slides.length === 0) return;

    let md = `---
marp: true
theme: gaia
_class: lead
paginate: true
backgroundColor: #f8fafc
color: #1e293b
---

# AI Executive Insight Deck
## Category Discovery Analysis & MVP Recommendation
Generated for Product Stakeholders

---

`;

    slides.forEach((slide) => {
      let contentText = '';
      if (slide.slide_number === 3 && slide.mvp_details) {
        const details = slide.mvp_details;
        contentText = `**Target Users**: ${details.target_users}\n\n**Pain Points**: ${details.pain_points}\n\n**Proposed MVP**: ${details.proposed_solution}\n\n**Core Features**:\n${(details.core_features || []).map(f => `- ${f}`).join('\n')}\n\n**Metrics**: ${(details.success_metrics || []).join(', ')}`;
      } else if (Array.isArray(slide.content)) {
        contentText = slide.content.map(p => `- ${p}`).join('\n');
      } else if (typeof slide.content === 'string') {
        contentText = slide.content;
      }

      md += `<!-- _header: "${slide.title}" -->
<!-- _footer: "Pulse Intelligence — Confidential" -->

### **${slide.headline}**

${contentText}

---

`;
    });

    const blob = new Blob([md], { type: 'text/markdown;charset=utf-8;' });
    const link = document.createElement("a");
    link.href = URL.createObjectURL(blob);
    link.setAttribute("download", "AI_Executive_Insight_Deck.md");
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  if (loading) return (
    <div className="flex-center" style={{ height: '80vh', display: 'flex', justifyContent: 'center', alignItems: 'center', flexDirection: 'column', gap: '1rem' }}>
      <div className="loader" style={{ width: '40px', height: '40px', borderColor: 'rgba(99, 102, 241, 0.3)', borderTopColor: 'var(--accent-primary)' }}></div>
      <p style={{ color: 'var(--text-secondary)' }}>Compiling AI Presentation Slides...</p>
    </div>
  );

  if (slides.length === 0) return (
    <div className="glass-card" style={{ textAlign: 'center', padding: '3rem', margin: '2rem' }}>
      <AlertTriangle size={48} color="var(--warning)" style={{ marginBottom: '1rem' }} />
      <h3>No presentation deck compiled yet</h3>
      <p style={{ color: 'var(--text-muted)' }}>Run the full collection and analysis pipeline on the Overview tab first.</p>
    </div>
  );

  const activeSlide = slides[currentSlideIndex];

  return (
    <div>
      <div className="page-header" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: '1rem' }}>
        <div>
          <h1 className="page-title text-gradient">Executive Insight Deck</h1>
          <p className="page-subtitle">A concise 4-slide McKinsey-style consulting presentation of category discovery insights.</p>
        </div>
        <div style={{ display: 'flex', gap: '0.75rem' }}>
          <button className="btn-secondary" onClick={exportMarpMarkdown} style={{ gap: '0.5rem' }}>
            <Download size={16} /> Marp MD
          </button>
          <button className="btn-primary" onClick={exportPPTX} style={{ gap: '0.5rem' }}>
            <Presentation size={16} /> Export Editable PPTX
          </button>
        </div>
      </div>

      <div className="grid-2" style={{ gridTemplateColumns: '7fr 3fr', gap: '2rem' }}>
        {/* Slide Canvas Column */}
        <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
          {/* Slide Frame (16:9 Aspect Ratio) */}
          <div className="glass-panel" style={{ 
            aspectRatio: '16/9', 
            background: '#0d1624', 
            border: '2px solid #1f2f47', 
            borderRadius: '12px',
            padding: '2.5rem',
            display: 'flex',
            flexDirection: 'column',
            position: 'relative',
            boxShadow: '0 10px 30px rgba(0,0,0,0.5)',
            textAlign: 'left'
          }}>
            {/* Slide Header */}
            <div style={{ borderBottom: '1px solid #1f2f47', paddingBottom: '1rem', marginBottom: '1.25rem' }}>
              <span style={{ fontSize: '0.8rem', color: 'var(--accent-primary)', fontWeight: '600', textTransform: 'uppercase', tracking: '0.05em' }}>
                Slide {activeSlide.slide_number} of {slides.length}
              </span>
              <h2 style={{ fontSize: '1.75rem', color: '#fff', margin: '0.2rem 0' }}>{activeSlide.title}</h2>
              <p style={{ fontSize: '1.05rem', color: '#60a5fa', margin: '0.2rem 0', fontWeight: '500', fontStyle: 'italic' }}>
                {activeSlide.headline}
              </p>
            </div>

            {/* Slide Body Grid */}
            <div style={{ display: 'grid', gridTemplateColumns: '1.2fr 2fr', gap: '2rem', flex: 1 }}>
              {/* Slide Left Column (Metrics / Visuals Config) */}
              <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem', justifyContent: 'center' }}>
                {activeSlide.key_metrics?.map((m, i) => (
                  <div key={i} style={{ background: '#122035', padding: '1rem', borderRadius: '8px', borderLeft: '4px solid var(--accent-primary)' }}>
                    <div style={{ fontSize: '2rem', fontWeight: '800', color: '#fff' }}>{m.value}</div>
                    <div style={{ fontSize: '0.8rem', color: 'var(--text-secondary)', marginTop: '0.25rem' }}>{m.label}</div>
                  </div>
                ))}

                {/* Optional visual placeholder for charts */}
                {activeSlide.visualization?.type === 'distribution' && (
                  <div style={{ background: 'rgba(255,255,255,0.02)', padding: '1rem', borderRadius: '8px', border: '1px dashed #1f2f47', fontSize: '0.8rem', color: 'var(--text-muted)' }}>
                    <strong>Chart: Sources Distribution</strong>
                    <div style={{ display: 'flex', gap: '4px', marginTop: '0.5rem', height: '10px', borderRadius: '4px', overflow: 'hidden' }}>
                      <div style={{ flex: 3, background: 'var(--success)' }}></div>
                      <div style={{ flex: 1, background: 'var(--info)' }}></div>
                    </div>
                  </div>
                )}
              </div>

              {/* Slide Right Column (Key Points / MVP Details) */}
              <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem', justifyContent: 'center', overflowY: 'auto' }}>
                {activeSlide.slide_number === 3 && activeSlide.mvp_details ? (
                  <div style={{ display: 'flex', flexDirection: 'column', gap: '0.8rem', fontSize: '0.9rem' }}>
                    <div style={{ display: 'grid', gridTemplateColumns: '100px 1fr', borderBottom: '1px solid rgba(255,255,255,0.05)', paddingBottom: '0.4rem' }}>
                      <span style={{ color: 'var(--text-muted)', fontWeight: '600' }}>Target Users:</span>
                      <span style={{ color: '#fff' }}>{activeSlide.mvp_details.target_users}</span>
                    </div>
                    <div style={{ display: 'grid', gridTemplateColumns: '100px 1fr', borderBottom: '1px solid rgba(255,255,255,0.05)', paddingBottom: '0.4rem' }}>
                      <span style={{ color: 'var(--text-muted)', fontWeight: '600' }}>Pain Points:</span>
                      <span style={{ color: '#fff' }}>{activeSlide.mvp_details.pain_points}</span>
                    </div>
                    <div style={{ display: 'grid', gridTemplateColumns: '100px 1fr', borderBottom: '1px solid rgba(255,255,255,0.05)', paddingBottom: '0.4rem' }}>
                      <span style={{ color: 'var(--text-muted)', fontWeight: '600' }}>MVP:</span>
                      <span style={{ color: '#60a5fa', fontWeight: 'bold' }}>{activeSlide.mvp_details.proposed_solution}</span>
                    </div>
                    <div>
                      <span style={{ color: 'var(--text-muted)', fontWeight: '600', display: 'block', marginBottom: '0.2rem' }}>Core MVP Features:</span>
                      <div style={{ display: 'flex', flexWrap: 'wrap', gap: '4px' }}>
                        {(activeSlide.mvp_details.core_features || []).map(f => (
                          <span key={f} className="badge badge-info" style={{ fontSize: '0.8rem' }}>{f}</span>
                        ))}
                      </div>
                    </div>
                  </div>
                ) : Array.isArray(activeSlide.content) ? (
                  <ul style={{ paddingLeft: '1.2rem', margin: 0, display: 'flex', flexDirection: 'column', gap: '0.75rem', fontSize: '0.95rem', color: '#cbd5e1', lineHeight: '1.5' }}>
                    {activeSlide.content.map((point, index) => (
                      <li key={index} style={{ marginBottom: '0.25rem' }}>{point}</li>
                    ))}
                  </ul>
                ) : (
                  <p style={{ fontSize: '1rem', color: '#cbd5e1', margin: 0, lineHeight: '1.6' }}>{activeSlide.content}</p>
                )}
              </div>
            </div>

            {/* Slide Footer */}
            <div style={{ display: 'flex', justifyContent: 'space-between', borderTop: '1px solid #1f2f47', paddingTop: '0.75rem', marginTop: '1rem', fontSize: '0.8rem', color: 'var(--text-muted)' }}>
              <span>Pulse Intelligence — Category Discovery Project</span>
              <span>McKinsey Standard Layout</span>
            </div>
          </div>

          {/* Navigation Controls */}
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginTop: '0.5rem' }}>
            <button className="btn-secondary" onClick={handlePrevSlide} disabled={currentSlideIndex === 0}>
              <ArrowLeft size={16} /> Back
            </button>
            <span style={{ color: 'var(--text-secondary)', fontSize: '0.9rem' }}>
              Slide {currentSlideIndex + 1} / {slides.length}
            </span>
            <button className="btn-secondary" onClick={handleNextSlide} disabled={currentSlideIndex === slides.length - 1}>
              Next <ArrowRight size={16} />
            </button>
          </div>
        </div>

        {/* Presenter Speaker Notes Column */}
        <div className="glass-panel" style={{ background: '#090e18', border: '1px solid #1e293b', borderRadius: '12px', padding: '1.5rem', display: 'flex', flexDirection: 'column', gap: '1.25rem', height: 'fit-content', textAlign: 'left' }}>
          <h3 style={{ borderBottom: '1px solid #1e293b', paddingBottom: '0.5rem', color: '#fff', fontSize: '1.1rem', margin: 0 }}>
            🎙️ Presenter Speaker Notes
          </h3>

          <div style={{ display: 'flex', flexDirection: 'column', gap: '1.25rem', fontSize: '0.9rem', overflowY: 'auto', maxHeight: '420px' }}>
            {activeSlide.speaker_notes ? (
              <>
                <div>
                  <strong style={{ color: 'var(--accent-primary)', display: 'block', marginBottom: '0.25rem' }}>What to Say (Talk Track):</strong>
                  <p style={{ color: '#cbd5e1', margin: 0, lineHeight: '1.4', fontStyle: 'italic' }}>"{activeSlide.speaker_notes.what_to_say}"</p>
                </div>

                <div>
                  <strong style={{ color: 'var(--accent-secondary)', display: 'block', marginBottom: '0.25rem' }}>Why it Matters (Strategic Value):</strong>
                  <p style={{ color: 'var(--text-secondary)', margin: 0, lineHeight: '1.4' }}>{activeSlide.speaker_notes.why_it_matters}</p>
                </div>

                <div style={{ borderTop: '1px solid #1e293b', paddingTop: '0.75rem' }}>
                  <strong style={{ color: 'var(--warning)', display: 'block', marginBottom: '0.25rem' }}>Expected Audience Question:</strong>
                  <p style={{ color: 'var(--text-primary)', fontWeight: 'bold', margin: '0 0 0.5rem 0' }}>"{activeSlide.speaker_notes.audience_question}"</p>
                  <strong style={{ color: 'var(--success)', display: 'block', marginBottom: '0.25rem' }}>Suggested Answer:</strong>
                  <p style={{ color: 'var(--text-secondary)', margin: 0, lineHeight: '1.4' }}>{activeSlide.speaker_notes.suggested_answer}</p>
                </div>
              </>
            ) : (
              <p style={{ color: 'var(--text-muted)' }}>No presenter notes compiled for this slide.</p>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default ExecutiveDeck;
