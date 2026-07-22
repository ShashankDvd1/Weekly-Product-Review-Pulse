import { useState, useEffect } from 'react';
import { Presentation, Download, ArrowLeft, ArrowRight, Play, CheckSquare, ListTodo, AlertTriangle, TrendingUp, Landmark, Loader2 } from 'lucide-react';
import { getBackendUrl } from '../config';

const ExecutiveDeck = () => {
  const [slides, setSlides] = useState([]);
  const [loading, setLoading] = useState(true);
  const [currentSlideIndex, setCurrentSlideIndex] = useState(0);

  const [exportSlidesLoading, setExportSlidesLoading] = useState(false);
  const [exportSlidesUrl, setExportSlidesUrl] = useState(null);

  // Fetch overview to detect brand
  const [brand, setBrand] = useState('default');

  useEffect(() => {
    const fetchDeckData = async () => {
      try {
        setLoading(true);
        const [deckRes, overviewRes] = await Promise.all([
          fetch(`${getBackendUrl()}/api/v2/reports/executive-deck`),
          fetch(`${getBackendUrl()}/api/v2/dashboard/overview`)
        ]);
        
        const deckData = await deckRes.json();
        setSlides(deckData.slides || []);
        
        const overviewData = await overviewRes.json();
        if (overviewData.app_name) {
          setBrand(overviewData.app_name.toLowerCase());
        }
      } catch (err) {
        console.error('Error fetching deck or overview data', err);
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

  const getBrandColors = (brandName) => {
    const b = brandName.toLowerCase();
    if (b.includes('blinkit')) {
      return {
        primary: '#FAD02C', // Yellow
        accent: '#10b981', // Emerald
        bg: 'linear-gradient(135deg, #0e1208, #18220f)',
        cardBg: 'rgba(250, 208, 44, 0.04)',
        border: 'rgba(250, 208, 44, 0.15)',
        text: '#ffffff',
        brandLabel: 'Blinkit Yellow-Green Theme'
      };
    }
    if (b.includes('zepto')) {
      return {
        primary: '#8A3FFC', // Purple
        accent: '#ff7eb6', // Pink
        bg: 'linear-gradient(135deg, #100b1e, #1c1236)',
        cardBg: 'rgba(138, 63, 252, 0.04)',
        border: 'rgba(138, 63, 252, 0.15)',
        text: '#ffffff',
        brandLabel: 'Zepto Purple-Pink Theme'
      };
    }
    if (b.includes('swiggy') || b.includes('instamart')) {
      return {
        primary: '#FC8019', // Orange
        accent: '#06b6d4', // Cyan
        bg: 'linear-gradient(135deg, #1b0e06, #2d180b)',
        cardBg: 'rgba(252, 128, 25, 0.04)',
        border: 'rgba(252, 128, 25, 0.15)',
        text: '#ffffff',
        brandLabel: 'Swiggy Orange Theme'
      };
    }
    return {
      primary: '#3b82f6', // McKinsey Corporate Blue
      accent: '#60a5fa',
      bg: 'linear-gradient(135deg, #0b1329, #14213d)',
      cardBg: 'rgba(59, 130, 246, 0.04)',
      border: 'rgba(59, 130, 246, 0.15)',
      text: '#ffffff',
      brandLabel: 'Pulse Corporate Theme'
    };
  };

  // Google Slides Export
  const handleExportSlides = async () => {
    try {
      setExportSlidesLoading(true);
      const res = await fetch(`${getBackendUrl()}/api/v2/reports/executive-deck/export-slides`, {
        method: 'POST'
      });
      const resData = await res.json();
      if (resData.presentation_url) {
        setExportSlidesUrl(resData.presentation_url);
      } else {
        alert(resData.detail || "Could not export presentation.");
      }
    } catch (err) {
      alert("Error exporting presentation: " + err.message);
    } finally {
      setExportSlidesLoading(false);
    }
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
  const theme = getBrandColors(brand);

  const renderSlideContent = () => {
    // Slide 1: Opportunity/Title
    if (activeSlide.slide_number === 1) {
      return (
        <div style={{ display: 'grid', gridTemplateColumns: '1.2fr 1fr', gap: '1.5rem', height: '100%' }}>
          <div style={{ display: 'flex', flexDirection: 'column', justifyContent: 'center', gap: '1rem' }}>
            <span style={{ fontSize: '0.85rem', color: theme.primary, textTransform: 'uppercase', letterSpacing: '2px', fontWeight: 'bold' }}>
              Strategic Opportunity Identification
            </span>
            <h1 style={{ fontSize: '2rem', color: '#fff', margin: 0, lineHeight: '1.2', fontWeight: '800' }}>
              {activeSlide.title}
            </h1>
            <p style={{ fontSize: '1rem', color: '#94a3b8', margin: 0, lineHeight: '1.6' }}>
              {activeSlide.headline}
            </p>
          </div>
          <div style={{ display: 'flex', flexDirection: 'column', justifyContent: 'center', gap: '0.75rem' }}>
            {activeSlide.key_metrics?.map((m, i) => (
              <div key={i} style={{ 
                background: theme.cardBg, 
                padding: '1.25rem', 
                borderRadius: '12px', 
                border: `1px solid ${theme.border}`,
                borderLeft: `5px solid ${theme.primary}`
              }}>
                <div style={{ fontSize: '2.25rem', fontWeight: '800', color: theme.primary }}>{m.value}</div>
                <div style={{ fontSize: '0.8rem', color: '#94a3b8', marginTop: '0.25rem', fontWeight: '600' }}>{m.label}</div>
              </div>
            ))}
          </div>
        </div>
      );
    }

    // Slide 2: Evidence & Insights
    if (activeSlide.slide_number === 2) {
      const quotes = Array.isArray(activeSlide.content) ? activeSlide.content : [];
      return (
        <div style={{ display: 'grid', gridTemplateColumns: '1fr', gap: '1rem', height: '100%', overflowY: 'auto' }}>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
            <span style={{ fontSize: '0.8rem', color: theme.primary, textTransform: 'uppercase', letterSpacing: '2px', fontWeight: 'bold' }}>
              Voice of the Customer (VoC) Evidence
            </span>
            <p style={{ fontSize: '1.05rem', color: '#94a3b8', fontStyle: 'italic', margin: '0 0 0.5rem 0' }}>
              "{activeSlide.headline}"
            </p>
          </div>
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1rem' }}>
            {quotes.slice(0, 4).map((q, i) => (
              <div key={i} style={{ 
                background: theme.cardBg, 
                padding: '1rem', 
                borderRadius: '10px', 
                border: `1px solid ${theme.border}`,
                fontSize: '0.85rem',
                color: '#cbd5e1',
                lineHeight: '1.4',
                position: 'relative'
              }}>
                <span style={{ position: 'absolute', top: '8px', right: '12px', fontSize: '1.5rem', color: theme.primary, opacity: 0.3, fontFamily: 'serif' }}>”</span>
                {q}
              </div>
            ))}
          </div>
        </div>
      );
    }

    // Slide 3: MVP Solution
    if (activeSlide.slide_number === 3 && activeSlide.mvp_details) {
      const details = activeSlide.mvp_details;
      return (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem', height: '100%' }}>
          <span style={{ fontSize: '0.8rem', color: theme.primary, textTransform: 'uppercase', letterSpacing: '2px', fontWeight: 'bold' }}>
            Proposed MVP Strategy
          </span>
          <h3 style={{ fontSize: '1.25rem', color: '#fff', margin: 0 }}>
            {activeSlide.headline}
          </h3>
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1rem', flex: 1 }}>
            <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
              <div style={{ background: theme.cardBg, padding: '0.75rem 1rem', borderRadius: '8px', border: `1px solid ${theme.border}` }}>
                <strong style={{ color: theme.primary, fontSize: '0.75rem', textTransform: 'uppercase', display: 'block', marginBottom: '0.2rem' }}>Target User Segment</strong>
                <span style={{ fontSize: '0.85rem', color: '#cbd5e1' }}>{details.target_users}</span>
              </div>
              <div style={{ background: theme.cardBg, padding: '0.75rem 1rem', borderRadius: '8px', border: `1px solid ${theme.border}` }}>
                <strong style={{ color: theme.primary, fontSize: '0.75rem', textTransform: 'uppercase', display: 'block', marginBottom: '0.2rem' }}>Core Pain Points Solved</strong>
                <span style={{ fontSize: '0.85rem', color: '#cbd5e1' }}>{details.pain_points}</span>
              </div>
            </div>
            <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
              <div style={{ background: 'rgba(255,255,255,0.03)', padding: '0.75rem 1rem', borderRadius: '8px', border: `1px solid ${theme.border}`, borderLeft: `4px solid ${theme.accent}` }}>
                <strong style={{ color: theme.accent, fontSize: '0.75rem', textTransform: 'uppercase', display: 'block', marginBottom: '0.2rem' }}>Proposed MVP</strong>
                <span style={{ fontSize: '0.9rem', color: '#fff', fontWeight: 'bold' }}>{details.proposed_solution}</span>
              </div>
              <div>
                <strong style={{ color: '#94a3b8', fontSize: '0.75rem', textTransform: 'uppercase', display: 'block', marginBottom: '0.4rem' }}>Key Features</strong>
                <div style={{ display: 'flex', flexWrap: 'wrap', gap: '6px' }}>
                  {(details.core_features || []).map(f => (
                    <span key={f} style={{ 
                      background: theme.primary, 
                      color: '#000', 
                      fontWeight: 'bold', 
                      fontSize: '0.75rem', 
                      padding: '0.25rem 0.6rem', 
                      borderRadius: '4px' 
                    }}>
                      {f}
                    </span>
                  ))}
                </div>
              </div>
            </div>
          </div>
        </div>
      );
    }

    // Slide 4: KPIs & Launch Metrics
    if (activeSlide.slide_number === 4) {
      const points = Array.isArray(activeSlide.content) ? activeSlide.content : [];
      return (
        <div style={{ display: 'grid', gridTemplateColumns: '1.2fr 1fr', gap: '1.5rem', height: '100%' }}>
          <div style={{ display: 'flex', flexDirection: 'column', justifyContent: 'center', gap: '0.75rem' }}>
            <span style={{ fontSize: '0.8rem', color: theme.primary, textTransform: 'uppercase', letterSpacing: '2px', fontWeight: 'bold' }}>
              Success Metrics & Growth Loops
            </span>
            <h3 style={{ fontSize: '1.35rem', color: '#fff', margin: 0, fontWeight: '700' }}>
              {activeSlide.headline}
            </h3>
            <ul style={{ paddingLeft: '1.1rem', margin: 0, display: 'flex', flexDirection: 'column', gap: '0.4rem', fontSize: '0.85rem', color: '#94a3b8' }}>
              {points.map((pt, i) => (
                <li key={i}>{pt}</li>
              ))}
            </ul>
          </div>
          <div style={{ display: 'flex', flexDirection: 'column', justifyContent: 'center', gap: '0.75rem' }}>
            {activeSlide.key_metrics?.map((m, i) => (
              <div key={i} style={{ 
                background: theme.cardBg, 
                padding: '1rem 1.25rem', 
                borderRadius: '10px', 
                border: `1px solid ${theme.border}`,
                display: 'flex',
                justifyContent: 'space-between',
                alignItems: 'center'
              }}>
                <span style={{ fontSize: '0.8rem', color: '#cbd5e1', fontWeight: '500' }}>{m.label}</span>
                <span style={{ fontSize: '1.5rem', fontWeight: '800', color: theme.accent }}>{m.value}</span>
              </div>
            ))}
          </div>
        </div>
      );
    }

    // Fallback slide renderer
    return <p style={{ color: '#cbd5e1' }}>{activeSlide.content}</p>;
  };

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
          <button 
            className="btn-primary" 
            onClick={handleExportSlides} 
            disabled={exportSlidesLoading}
            style={{ gap: '0.5rem', background: 'linear-gradient(135deg, #f59e0b, #d97706)' }}
          >
            {exportSlidesLoading ? <Loader2 size={16} style={{ animation: 'spin 1s linear infinite' }} /> : <Presentation size={16} />}
            {exportSlidesLoading ? 'Generating Slides...' : 'Export to Google Slides'}
          </button>
        </div>
      </div>

      {exportSlidesUrl && (
        <div className="glass-panel" style={{ marginBottom: '1.5rem', padding: '1.25rem', background: 'rgba(16, 185, 129, 0.1)', border: '1px solid rgba(16, 185, 129, 0.3)', textAlign: 'left', borderRadius: '8px' }}>
          <h4 style={{ color: 'var(--success)', margin: '0 0 0.4rem 0', display: 'flex', alignItems: 'center', gap: '6px' }}>
            ✅ Google Slides Exported Successfully!
          </h4>
          <p style={{ margin: 0, color: 'var(--text-secondary)', fontSize: '0.9rem' }}>
            Live Presentation: <a href={exportSlidesUrl} target="_blank" rel="noopener noreferrer" style={{ color: 'var(--accent-primary)', fontWeight: 'bold' }}>{exportSlidesUrl}</a>
          </p>
        </div>
      )}

      <div className="grid-2" style={{ gridTemplateColumns: '7fr 3fr', gap: '2rem' }}>
        {/* Slide Canvas Column */}
        <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
          {/* Slide Frame (16:9 Aspect Ratio) */}
          <div className="glass-panel" style={{ 
            aspectRatio: '16/9', 
            background: theme.bg, 
            border: `2px solid ${theme.border}`, 
            borderRadius: '16px',
            padding: '2.5rem',
            display: 'flex',
            flexDirection: 'column',
            position: 'relative',
            boxShadow: '0 15px 35px rgba(0,0,0,0.6)',
            textAlign: 'left',
            overflow: 'hidden'
          }}>
            {/* Top brand indicator */}
            <div style={{ position: 'absolute', top: '12px', right: '20px', display: 'flex', alignItems: 'center', gap: '6px' }}>
              <span style={{ width: '8px', height: '8px', borderRadius: '50%', background: theme.primary }}></span>
              <span style={{ fontSize: '0.7rem', color: '#94a3b8', textTransform: 'uppercase', letterSpacing: '1px', fontWeight: 'bold' }}>
                {brand !== 'default' ? `${brand.toUpperCase()} ANALYSIS` : 'PULSE INTELLIGENCE'}
              </span>
            </div>

            {/* Slide Body */}
            <div style={{ flex: 1, display: 'flex', flexDirection: 'column', justifyContent: 'center' }}>
              {renderSlideContent()}
            </div>

            {/* Slide Footer */}
            <div style={{ display: 'flex', justifyContent: 'space-between', borderTop: `1px solid ${theme.border}`, paddingTop: '0.75rem', marginTop: '1rem', fontSize: '0.75rem', color: '#64748b' }}>
              <span>Pulse Intelligence — Category Discovery Project</span>
              <span>{theme.brandLabel}</span>
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
