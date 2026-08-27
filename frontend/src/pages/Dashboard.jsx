import { useState, useEffect } from 'react';
import { 
  Activity, 
  MessageSquare, 
  AlertTriangle, 
  TrendingUp, 
  RefreshCw, 
  Users, 
  Terminal, 
  Send, 
  Play, 
  CheckCircle2, 
  Calendar, 
  Search, 
  Layers,
  Brain, 
  ChevronDown, 
  ChevronRight, 
  Loader2, 
  Target, 
  Lightbulb, 
  Presentation, 
  FileText, 
  ArrowLeft, 
  ArrowRight, 
  Award, 
  Upload, 
  Download,
  Database,
  Shield
} from 'lucide-react';
import { PieChart, Pie, Cell, ResponsiveContainer, Tooltip } from 'recharts';
import { getBackendUrl } from '../config';

const PHASE_META = {
  1: { label: 'Planning & Processing', icon: <Target size={18} />, color: '#f97316', steps: ['step_1', 'step_2'] },
  2: { label: 'Behavioral Discovery', icon: <Users size={18} />, color: '#8b5cf6', steps: ['step_4', 'step_8'] },
  3: { label: 'Evidence Traceability', icon: <Lightbulb size={18} />, color: '#06b6d4', steps: ['step_13'] },
  4: { label: 'Solution Generation', icon: <Presentation size={18} />, color: '#10b981', steps: ['step_14'] },
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

const renderActiveSlideContent = (activeSlide, brandColor) => {
  const type = activeSlide.type;
  switch (type) {
    case 'market_gap':
      return (
        <div style={{ display: 'grid', gridTemplateColumns: '1.1fr 0.9fr', gap: '1.5rem', height: '100%' }}>
          <div style={{ display: 'flex', flexDirection: 'column', justifyContent: 'center', gap: '0.75rem', textAlign: 'left' }}>
            <span style={{ fontSize: '0.8rem', color: brandColor, textTransform: 'uppercase', letterSpacing: '2px', fontWeight: 'bold' }}>
              Slide {activeSlide.slide_number}: Market Gap & Problem
            </span>
            <h2 style={{ fontSize: '1.5rem', color: '#fff', margin: 0, fontWeight: '800', lineHeight: '1.3' }}>
              {activeSlide.headline}
            </h2>
            <div style={{ display: 'flex', flexDirection: 'column', gap: '0.4rem', marginTop: '0.5rem' }}>
              {activeSlide.bullets?.map((b, i) => (
                <p key={i} style={{ color: 'var(--text-secondary)', fontSize: '0.8rem', margin: 0, lineHeight: '1.4' }}>• {b}</p>
              ))}
            </div>
            {/* Stat Cards */}
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: '0.5rem', marginTop: '0.5rem' }}>
              {activeSlide.stats?.map((st, i) => (
                <div key={i} style={{ background: 'rgba(255,255,255,0.02)', padding: '0.5rem', borderRadius: '6px', border: '1px solid rgba(255,255,255,0.05)', textAlign: 'center' }}>
                  <div style={{ fontSize: '1.1rem', fontWeight: 'bold', color: brandColor }}>{st.value}</div>
                  <div style={{ fontSize: '0.65rem', color: 'var(--text-muted)' }}>{st.label}</div>
                </div>
              ))}
            </div>
          </div>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem', overflowY: 'auto', textAlign: 'left', paddingRight: '0.25rem' }}>
            {/* Market Gap Table */}
            <div style={{ background: 'rgba(255,255,255,0.02)', border: '1px solid rgba(255,255,255,0.05)', borderRadius: '8px', overflow: 'hidden' }}>
              <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: '0.75rem' }}>
                <thead>
                  <tr style={{ background: 'rgba(255,255,255,0.03)', borderBottom: '1px solid rgba(255,255,255,0.06)' }}>
                    <th style={{ padding: '0.4rem', textAlign: 'left' }}>Platform</th>
                    <th style={{ padding: '0.4rem', textAlign: 'left' }}>What they offer</th>
                    <th style={{ padding: '0.4rem', textAlign: 'left' }}>What's missing</th>
                  </tr>
                </thead>
                <tbody>
                  {activeSlide.market_gap_table?.map((row, i) => (
                    <tr key={i} style={{ borderBottom: '1px solid rgba(255,255,255,0.04)' }}>
                      <td style={{ padding: '0.4rem', fontWeight: 'bold', color: brandColor }}>{row.platform}</td>
                      <td style={{ padding: '0.4rem', color: 'var(--text-secondary)' }}>{row.offer}</td>
                      <td style={{ padding: '0.4rem', color: '#f87171' }}>{row.missing}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
            {/* Why Solve First */}
            <div style={{ background: 'rgba(255,255,255,0.02)', padding: '0.6rem', borderRadius: '8px', border: '1px solid rgba(255,255,255,0.05)' }}>
              <strong style={{ display: 'block', fontSize: '0.7rem', color: brandColor, textTransform: 'uppercase', marginBottom: '0.25rem' }}>Why Solve This First</strong>
              <div style={{ display: 'flex', flexDirection: 'column', gap: '0.25rem' }}>
                {activeSlide.why_solve_first?.map((pt, i) => (
                  <div key={i} style={{ fontSize: '0.75rem', color: 'var(--text-secondary)' }}>✓ {pt}</div>
                ))}
              </div>
            </div>
          </div>
        </div>
      );
    case 'user_research':
      return (
        <div style={{ display: 'grid', gridTemplateColumns: '1.1fr 0.9fr', gap: '1.5rem', height: '100%' }}>
          <div style={{ display: 'flex', flexDirection: 'column', justifyContent: 'center', gap: '0.75rem', textAlign: 'left' }}>
            <span style={{ fontSize: '0.8rem', color: brandColor, textTransform: 'uppercase', letterSpacing: '2px', fontWeight: 'bold' }}>
              Slide {activeSlide.slide_number}: User Research & Sentiment
            </span>
            <h2 style={{ fontSize: '1.5rem', color: '#fff', margin: 0, fontWeight: '800', lineHeight: '1.3' }}>
              {activeSlide.headline}
            </h2>
            {/* Findings Card */}
            <div style={{ background: 'rgba(255,255,255,0.02)', padding: '0.75rem', borderRadius: '8px', border: '1px solid rgba(255,255,255,0.05)', display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '0.5rem' }}>
              <div>
                <div style={{ fontSize: '0.7rem', color: 'var(--text-muted)' }}>Analyzed / Labeled</div>
                <div style={{ fontSize: '1.1rem', fontWeight: 'bold', color: '#fff' }}>{activeSlide.findings?.total_analyzed} / {activeSlide.findings?.llm_labeled}</div>
              </div>
              <div>
                <div style={{ fontSize: '0.7rem', color: 'var(--text-muted)' }}>Discovery Pain Rate</div>
                <div style={{ fontSize: '1.1rem', fontWeight: 'bold', color: 'var(--error)' }}>{activeSlide.findings?.discovery_pain_pct}%</div>
              </div>
            </div>
            {/* Demands */}
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: '0.35rem' }}>
              {[
                { label: 'Variety', pct: activeSlide.findings?.wants_variety_pct },
                { label: 'Less Repetition', pct: activeSlide.findings?.less_repetition_pct },
                { label: 'Real navigation', pct: activeSlide.findings?.real_shuffle_pct },
                { label: 'Better suggestions', pct: activeSlide.findings?.better_music_pct }
              ].map((d, i) => (
                <div key={i} style={{ background: 'rgba(255,255,255,0.01)', padding: '0.35rem', borderRadius: '4px', textAlign: 'center', fontSize: '0.65rem', border: '1px solid rgba(255,255,255,0.03)' }}>
                  <div style={{ fontWeight: 'bold', color: brandColor }}>{d.pct}%</div>
                  <div style={{ color: 'var(--text-muted)', overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>{d.label}</div>
                </div>
              ))}
            </div>
          </div>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem', overflowY: 'auto', textAlign: 'left', paddingRight: '0.25rem' }}>
            {/* Sentiment Cards */}
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: '0.4rem' }}>
              <div style={{ background: 'rgba(239,68,68,0.1)', border: '1px solid rgba(239,68,68,0.2)', padding: '0.5rem', borderRadius: '6px', textAlign: 'center' }}>
                <div style={{ fontSize: '1rem', fontWeight: 'bold', color: 'var(--error)' }}>{activeSlide.sentiment?.negative}</div>
                <div style={{ fontSize: '0.65rem', color: 'var(--text-muted)' }}>Negative</div>
              </div>
              <div style={{ background: 'rgba(245,158,11,0.1)', border: '1px solid rgba(245,158,11,0.2)', padding: '0.5rem', borderRadius: '6px', textAlign: 'center' }}>
                <div style={{ fontSize: '1rem', fontWeight: 'bold', color: 'var(--warning)' }}>{activeSlide.sentiment?.neutral}</div>
                <div style={{ fontSize: '0.65rem', color: 'var(--text-muted)' }}>Neutral</div>
              </div>
              <div style={{ background: 'rgba(16,185,129,0.1)', border: '1px solid rgba(16,185,129,0.2)', padding: '0.5rem', borderRadius: '6px', textAlign: 'center' }}>
                <div style={{ fontSize: '1rem', fontWeight: 'bold', color: 'var(--success)' }}>{activeSlide.sentiment?.positive}</div>
                <div style={{ fontSize: '0.65rem', color: 'var(--text-muted)' }}>Positive</div>
              </div>
            </div>
            {/* Cited Quotes */}
            <div style={{ display: 'flex', flexDirection: 'column', gap: '0.4rem' }}>
              <strong style={{ fontSize: '0.7rem', color: 'var(--text-muted)', textTransform: 'uppercase' }}>Cited User Verbatims</strong>
              {activeSlide.cited_quotes?.map((q, i) => (
                <div key={i} style={{ background: 'rgba(255,255,255,0.01)', padding: '0.5rem', borderRadius: '6px', border: '1px solid rgba(255,255,255,0.03)', fontSize: '0.75rem', borderLeft: `3px solid ${brandColor}` }}>
                  <p style={{ margin: '0 0 0.25rem 0', color: '#e2e8f0', fontStyle: 'italic' }}>"{q.quote}"</p>
                  <span style={{ fontSize: '0.65rem', color: 'var(--text-muted)' }}>{q.source}</span>
                </div>
              ))}
            </div>
          </div>
        </div>
      );
    case 'personas_journey':
      return (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem', height: '100%', overflowY: 'auto', textAlign: 'left' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <div>
              <span style={{ fontSize: '0.8rem', color: brandColor, textTransform: 'uppercase', letterSpacing: '2px', fontWeight: 'bold' }}>
                Slide {activeSlide.slide_number}: Segment Personas & User Journey
              </span>
              <h2 style={{ fontSize: '1.35rem', color: '#fff', margin: 0, fontWeight: '800' }}>
                {activeSlide.headline}
              </h2>
            </div>
          </div>
          {/* Personas Side-by-side */}
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '0.75rem' }}>
            {activeSlide.personas?.map((p, i) => (
              <div key={i} style={{ background: 'rgba(255,255,255,0.02)', padding: '0.6rem 0.8rem', borderRadius: '8px', border: '1px solid rgba(255,255,255,0.05)', fontSize: '0.75rem', borderLeft: `3px solid ${i === 0 ? 'var(--accent-primary)' : 'var(--accent-secondary)'}` }}>
                <strong style={{ fontSize: '0.85rem', color: '#fff', display: 'block' }}>{p.name}</strong>
                <span style={{ fontSize: '0.7rem', color: brandColor, fontStyle: 'italic', display: 'block', marginBottom: '0.35rem' }}>"{p.title}" — {p.meta}</span>
                <div style={{ display: 'flex', flexDirection: 'column', gap: '0.2rem', color: 'var(--text-secondary)' }}>
                  <div><strong>Trust pattern:</strong> {p.trust_pattern}</div>
                  <div><strong>Unmet need:</strong> {p.unmet_need}</div>
                  <div><strong>Behavioral trap:</strong> {p.behavioral_trap}</div>
                </div>
                <p style={{ margin: '0.4rem 0 0 0', color: 'var(--text-muted)', fontStyle: 'italic' }}>"{p.quote}"</p>
              </div>
            ))}
          </div>
          {/* User Journey horizontal flow */}
          <div style={{ marginTop: '0.25rem' }}>
            <strong style={{ fontSize: '0.7rem', color: 'var(--text-muted)', textTransform: 'uppercase', display: 'block', marginBottom: '0.35rem' }}>User Journey Habit Loop</strong>
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(5, 1fr)', gap: '0.4rem' }}>
              {activeSlide.user_journey?.map((st, i) => (
                <div key={i} style={{ background: 'rgba(255,255,255,0.01)', padding: '0.5rem', borderRadius: '6px', border: '1px solid rgba(255,255,255,0.03)', fontSize: '0.7rem', position: 'relative' }}>
                  <div style={{ fontWeight: 'bold', color: brandColor, borderBottom: '1px solid rgba(255,255,255,0.05)', paddingBottom: '0.2rem', marginBottom: '0.25rem' }}>{st.stage}</div>
                  <div style={{ color: '#fff', fontWeight: '500', marginBottom: '0.2rem' }}>{st.behavior}</div>
                  <div style={{ color: '#f87171', fontSize: '0.65rem' }}><strong>Friction:</strong> {st.friction}</div>
                  {i < 4 && (
                    <div style={{ position: 'absolute', top: '50%', right: '-8px', transform: 'translateY(-50%)', zIndex: 10, color: 'rgba(255,255,255,0.2)' }}>→</div>
                  )}
                </div>
              ))}
            </div>
          </div>
        </div>
      );
    case 'problem_framing':
      return (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem', height: '100%', overflowY: 'auto', textAlign: 'left' }}>
          <div>
            <span style={{ fontSize: '0.8rem', color: brandColor, textTransform: 'uppercase', letterSpacing: '2px', fontWeight: 'bold' }}>
              Slide {activeSlide.slide_number}: Problem Framing Canvas
            </span>
            <h2 style={{ fontSize: '1.35rem', color: '#fff', margin: 0, fontWeight: '800' }}>
              {activeSlide.headline}
            </h2>
          </div>
          {/* 4-Panel Canvas Grid */}
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '0.75rem' }}>
            <div style={{ background: 'rgba(239,68,68,0.03)', border: '1px solid rgba(239,68,68,0.1)', padding: '0.75rem', borderRadius: '8px', fontSize: '0.75rem' }}>
              <strong style={{ color: 'var(--error)', textTransform: 'uppercase', fontSize: '0.7rem', display: 'block', marginBottom: '0.25rem' }}>1. What is the True Problem?</strong>
              <p style={{ margin: 0, color: 'var(--text-secondary)', lineHeight: '1.4' }}>{activeSlide.true_problem}</p>
            </div>
            <div style={{ background: 'rgba(139,92,246,0.03)', border: '1px solid rgba(139,92,246,0.1)', padding: '0.75rem', borderRadius: '8px', fontSize: '0.75rem' }}>
              <strong style={{ color: '#8b5cf6', textTransform: 'uppercase', fontSize: '0.7rem', display: 'block', marginBottom: '0.25rem' }}>2. Who faces this problem?</strong>
              <p style={{ margin: 0, color: 'var(--text-secondary)', lineHeight: '1.4' }}>{activeSlide.target_cohort}</p>
            </div>
            <div style={{ background: 'rgba(6,182,212,0.03)', border: '1px solid rgba(6,182,212,0.1)', padding: '0.75rem', borderRadius: '8px', fontSize: '0.75rem' }}>
              <strong style={{ color: '#06b6d4', textTransform: 'uppercase', fontSize: '0.7rem', display: 'block', marginBottom: '0.25rem' }}>3. How do we know it's a problem?</strong>
              <div style={{ display: 'flex', flexDirection: 'column', gap: '0.2rem', color: 'var(--text-secondary)' }}>
                {activeSlide.evidences?.map((ev, idx) => (
                  <div key={idx}>• {ev}</div>
                ))}
              </div>
            </div>
            <div style={{ background: 'rgba(16,185,129,0.03)', border: '1px solid rgba(16,185,129,0.1)', padding: '0.75rem', borderRadius: '8px', fontSize: '0.75rem' }}>
              <strong style={{ color: 'var(--success)', textTransform: 'uppercase', fontSize: '0.7rem', display: 'block', marginBottom: '0.25rem' }}>4. Value Generated by Solving This</strong>
              <div style={{ color: 'var(--text-secondary)', lineHeight: '1.4' }}>
                <div><strong>For Users:</strong> {activeSlide.value_generated?.for_user}</div>
                <div style={{ marginTop: '0.25rem' }}><strong>For Platform:</strong> {activeSlide.value_generated?.for_platform}</div>
              </div>
            </div>
          </div>
          {/* Why solve now */}
          <div style={{ background: 'rgba(245,158,11,0.03)', border: '1px solid rgba(245,158,11,0.1)', padding: '0.6rem', borderRadius: '8px', fontSize: '0.75rem' }}>
            <strong style={{ color: 'var(--warning)', textTransform: 'uppercase', fontSize: '0.7rem', display: 'block', marginBottom: '0.25rem' }}>5. Why Should We Solve This Now?</strong>
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: '0.5rem' }}>
              <div><strong>Saturation:</strong> <span style={{ color: 'var(--text-secondary)' }}>{activeSlide.why_now?.saturation}</span></div>
              <div><strong>AI Unlock:</strong> <span style={{ color: 'var(--text-secondary)' }}>{activeSlide.why_now?.ai_unlock}</span></div>
              <div><strong>First-mover window:</strong> <span style={{ color: 'var(--text-secondary)' }}>{activeSlide.why_now?.first_mover}</span></div>
            </div>
          </div>
        </div>
      );
    case 'hypotheses_rice':
      return (
        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1.5rem', height: '100%', overflowY: 'auto', textAlign: 'left' }}>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '0.6rem', justifyContent: 'center' }}>
            <span style={{ fontSize: '0.8rem', color: brandColor, textTransform: 'uppercase', letterSpacing: '2px', fontWeight: 'bold' }}>
              Slide {activeSlide.slide_number}: Hypotheses & RICE Framework
            </span>
            <h2 style={{ fontSize: '1.4rem', color: '#fff', margin: 0, fontWeight: '800', lineHeight: '1.3' }}>
              {activeSlide.headline}
            </h2>
            {/* Hypotheses List */}
            <div style={{ display: 'flex', flexDirection: 'column', gap: '0.4rem' }}>
              {activeSlide.hypotheses?.map((h, i) => (
                <div key={i} style={{ background: 'rgba(255,255,255,0.01)', padding: '0.5rem', borderRadius: '6px', border: '1px solid rgba(255,255,255,0.03)', fontSize: '0.75rem', borderLeft: `3px solid ${h.id === 'H1' ? 'var(--success)' : 'rgba(255,255,255,0.2)'}` }}>
                  <strong style={{ color: '#fff' }}>{h.id}: {h.name}</strong>
                  {h.id === 'H1' && <span style={{ marginLeft: '0.5rem', background: 'var(--success)30', color: 'var(--success)', padding: '1px 4px', borderRadius: '4px', fontSize: '0.6rem', fontWeight: 'bold' }}>CHOSEN</span>}
                  <p style={{ margin: '0.2rem 0 0 0', color: 'var(--text-secondary)' }}>{h.statement}</p>
                </div>
              ))}
            </div>
          </div>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '0.6rem', overflowY: 'auto', paddingRight: '0.25rem' }}>
            {/* RICE Comparison Table */}
            <div style={{ background: 'rgba(255,255,255,0.02)', border: '1px solid rgba(255,255,255,0.05)', borderRadius: '8px', overflow: 'hidden' }}>
              <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: '0.72rem' }}>
                <thead>
                  <tr style={{ background: 'rgba(255,255,255,0.03)', borderBottom: '1px solid rgba(255,255,255,0.06)' }}>
                    <th style={{ padding: '0.4rem', textAlign: 'left' }}>ID</th>
                    <th style={{ padding: '0.4rem', textAlign: 'center' }}>Reach</th>
                    <th style={{ padding: '0.4rem', textAlign: 'center' }}>Impact</th>
                    <th style={{ padding: '0.4rem', textAlign: 'center' }}>Conf</th>
                    <th style={{ padding: '0.4rem', textAlign: 'center' }}>Effort</th>
                    <th style={{ padding: '0.4rem', textAlign: 'center', fontWeight: 'bold', color: brandColor }}>Score</th>
                  </tr>
                </thead>
                <tbody>
                  {activeSlide.rice_scores?.map((r, i) => (
                    <tr key={i} style={{ borderBottom: '1px solid rgba(255,255,255,0.04)', background: r.hypothesis_id === 'H1' ? 'rgba(16,185,129,0.04)' : 'transparent' }}>
                      <td style={{ padding: '0.4rem', fontWeight: 'bold', color: r.hypothesis_id === 'H1' ? 'var(--success)' : '#fff' }}>{r.hypothesis_id}</td>
                      <td style={{ padding: '0.4rem', textAlign: 'center', color: 'var(--text-secondary)' }}>{r.reach}/10</td>
                      <td style={{ padding: '0.4rem', textAlign: 'center', color: 'var(--text-secondary)' }}>{r.impact}/10</td>
                      <td style={{ padding: '0.4rem', textAlign: 'center', color: 'var(--text-secondary)' }}>{r.confidence * 10 || r.confidence}/10</td>
                      <td style={{ padding: '0.4rem', textAlign: 'center', color: 'var(--text-secondary)' }}>{r.effort}/10</td>
                      <td style={{ padding: '0.4rem', textAlign: 'center', fontWeight: 'bold', color: r.hypothesis_id === 'H1' ? 'var(--success)' : brandColor }}>{r.score}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
            {/* Winning Rationale */}
            <div style={{ background: 'rgba(16,185,129,0.03)', padding: '0.6rem', borderRadius: '8px', border: '1px solid rgba(16,185,129,0.1)', fontSize: '0.72rem', textAlign: 'left' }}>
              <strong style={{ color: 'var(--success)', textTransform: 'uppercase', display: 'block', marginBottom: '0.2rem' }}>Winning Rationale</strong>
              <p style={{ margin: 0, color: 'var(--text-secondary)', lineHeight: '1.4' }}>{activeSlide.winning_rationale}</p>
            </div>
          </div>
        </div>
      );
    case 'solution_comparison':
      return (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem', height: '100%', overflowY: 'auto', textAlign: 'left' }}>
          <div>
            <span style={{ fontSize: '0.8rem', color: brandColor, textTransform: 'uppercase', letterSpacing: '2px', fontWeight: 'bold' }}>
              Slide {activeSlide.slide_number}: Solution Comparison
            </span>
            <h2 style={{ fontSize: '1.35rem', color: '#fff', margin: 0, fontWeight: '800' }}>
              {activeSlide.headline}
            </h2>
          </div>
          {/* Solutions list S1-S4 */}
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: '0.5rem' }}>
            {activeSlide.solutions?.map((sol, i) => (
              <div key={i} style={{ background: 'rgba(255,255,255,0.02)', padding: '0.5rem', borderRadius: '6px', border: '1px solid rgba(255,255,255,0.05)', fontSize: '0.7rem', display: 'flex', flexDirection: 'column', gap: '0.25rem', borderTop: `4px solid ${sol.status === 'CHOSEN' ? 'var(--success)' : 'var(--error)'}` }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                  <strong style={{ color: '#fff' }}>{sol.id}: {sol.name}</strong>
                </div>
                <span style={{ fontSize: '0.6rem', padding: '1px 4px', borderRadius: '3px', fontWeight: 'bold', alignSelf: 'flex-start', background: sol.status === 'CHOSEN' ? 'var(--success)20' : 'var(--error)20', color: sol.status === 'CHOSEN' ? 'var(--success)' : 'var(--error)' }}>
                  {sol.status}
                </span>
                <p style={{ margin: 0, color: 'var(--text-secondary)', fontSize: '0.65rem', lineHeight: '1.3' }}>{sol.description}</p>
                <p style={{ margin: 0, color: 'var(--text-muted)', fontSize: '0.62rem', fontStyle: 'italic' }}>"{sol.feedback}"</p>
              </div>
            ))}
          </div>
          {/* Solution vs comparison chosen justification */}
          <div style={{ background: 'rgba(255,255,255,0.01)', padding: '0.6rem', borderRadius: '8px', border: '1px solid rgba(255,255,255,0.04)', fontSize: '0.72rem' }}>
            <strong style={{ color: brandColor, textTransform: 'uppercase', display: 'block', marginBottom: '0.25rem' }}>Why the Selected Solution Wins Against Each Alternative</strong>
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: '0.5rem' }}>
              {activeSlide.vs_comparison?.map((comp, idx) => (
                <div key={idx}>
                  <strong style={{ color: 'var(--error)' }}>vs {comp.against}:</strong>{' '}
                  <span style={{ color: 'var(--text-secondary)' }}>{comp.justification}</span>
                </div>
              ))}
            </div>
          </div>
        </div>
      );
    case 'mvp_spec':
      return (
        <div style={{ display: 'grid', gridTemplateColumns: '1.1fr 0.9fr', gap: '1.5rem', height: '100%', overflowY: 'auto', textAlign: 'left' }}>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '0.6rem', justifyContent: 'center' }}>
            <span style={{ fontSize: '0.8rem', color: brandColor, textTransform: 'uppercase', letterSpacing: '2px', fontWeight: 'bold' }}>
              Slide {activeSlide.slide_number}: MVP Prototype Specifications
            </span>
            <h2 style={{ fontSize: '1.4rem', color: '#fff', margin: 0, fontWeight: '800', lineHeight: '1.3' }}>
              {activeSlide.headline}
            </h2>
            <div style={{ display: 'flex', flexDirection: 'column', gap: '0.35rem', marginTop: '0.25rem' }}>
              {activeSlide.bullets?.map((b, i) => (
                <p key={i} style={{ color: 'var(--text-secondary)', fontSize: '0.75rem', margin: 0, lineHeight: '1.4' }}>• {b}</p>
              ))}
            </div>
            <div style={{ background: 'rgba(59,130,246,0.05)', border: '1px solid rgba(59,130,246,0.1)', padding: '0.5rem 0.75rem', borderRadius: '8px', fontSize: '0.72rem', marginTop: '0.25rem' }}>
              <strong style={{ color: '#60a5fa', display: 'block', marginBottom: '0.2rem' }}>Dynamic Trust Cues Configured</strong>
              <div style={{ display: 'flex', gap: '0.5rem' }}>
                {activeSlide.trust_cues?.map((tc, idx) => (
                  <span key={idx} style={{ background: 'rgba(255,255,255,0.03)', padding: '2px 6px', borderRadius: '4px', color: 'var(--text-secondary)' }}>{tc}</span>
                ))}
              </div>
            </div>
          </div>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '0.6rem', overflowY: 'auto', paddingRight: '0.25rem' }}>
            <strong style={{ fontSize: '0.7rem', color: 'var(--text-muted)', textTransform: 'uppercase' }}>MVP Screen Mapping Spec</strong>
            {activeSlide.screens?.map((scr, idx) => (
              <div key={idx} style={{ background: 'rgba(255,255,255,0.01)', padding: '0.5rem', borderRadius: '6px', border: '1px solid rgba(255,255,255,0.03)', fontSize: '0.72rem', borderLeft: `3px solid ${brandColor}` }}>
                <strong style={{ color: '#fff', display: 'block', marginBottom: '0.15rem' }}>{idx + 1}. {scr.name}</strong>
                <span style={{ color: 'var(--text-secondary)' }}>{scr.spec}</span>
              </div>
            ))}
            <button 
              className="btn-primary" 
              onClick={() => {
                fetch(`${getBackendUrl()}/api/v2/reports/mvp-workspace`)
                  .then(res => res.json())
                  .then(data => {
                    if (data.markdown) {
                      const blob = new Blob([data.markdown], { type: 'text/markdown;charset=utf-8;' });
                      const url = URL.createObjectURL(blob);
                      const link = document.createElement('a');
                      link.href = url;
                      link.setAttribute('download', 'mvp_prototype_spec.md');
                      document.body.appendChild(link);
                      link.click();
                      document.body.removeChild(link);
                    } else {
                      alert("Prototype markdown not available yet.");
                    }
                  })
                  .catch(err => alert("Error downloading prototype markdown: " + err.message));
              }}
              style={{ 
                marginTop: '0.5rem', padding: '0.4rem 0.75rem', fontSize: '0.72rem', 
                background: brandColor, color: '#000', border: 'none', borderRadius: '6px', 
                fontWeight: 'bold', cursor: 'pointer', display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '0.4rem'
              }}
            >
              📥 Download Complete Prototype Markdown (.MD)
            </button>
          </div>
        </div>
      );
    case 'data_flow_edges':
      return (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '0.6rem', height: '100%', overflowY: 'auto', textAlign: 'left' }}>
          <div>
            <span style={{ fontSize: '0.8rem', color: brandColor, textTransform: 'uppercase', letterSpacing: '2px', fontWeight: 'bold' }}>
              Slide {activeSlide.slide_number}: System Data Flow & Edge Cases
            </span>
            <h2 style={{ fontSize: '1.35rem', color: '#fff', margin: 0, fontWeight: '800' }}>
              {activeSlide.headline}
            </h2>
          </div>
          {/* Data Flow pipelines */}
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '0.75rem' }}>
            <div style={{ background: 'rgba(6,182,212,0.02)', border: '1px solid rgba(6,182,212,0.08)', padding: '0.6rem', borderRadius: '8px', fontSize: '0.72rem' }}>
              <strong style={{ color: '#06b6d4', display: 'block', marginBottom: '0.2rem', textTransform: 'uppercase', fontSize: '0.65rem' }}>① Review Insights Pipeline</strong>
              <p style={{ margin: 0, color: 'var(--text-secondary)' }}>{activeSlide.data_flow?.review_engine}</p>
            </div>
            <div style={{ background: 'rgba(16,185,129,0.02)', border: '1px solid rgba(16,185,129,0.08)', padding: '0.6rem', borderRadius: '8px', fontSize: '0.72rem' }}>
              <strong style={{ color: 'var(--success)', display: 'block', marginBottom: '0.2px', textTransform: 'uppercase', fontSize: '0.65rem' }}>② Contextual Cross-Sell Engine</strong>
              <p style={{ margin: 0, color: 'var(--text-secondary)' }}>{activeSlide.data_flow?.product_engine}</p>
            </div>
          </div>
          {/* Grounding & Edge Cases */}
          <div style={{ display: 'grid', gridTemplateColumns: '0.9fr 1.1fr', gap: '0.75rem' }}>
            <div style={{ background: 'rgba(255,255,255,0.01)', padding: '0.5rem', borderRadius: '8px', border: '1px solid rgba(255,255,255,0.04)', fontSize: '0.7rem' }}>
              <strong style={{ color: brandColor, display: 'block', marginBottom: '0.2rem', textTransform: 'uppercase', fontSize: '0.65rem' }}>Behavioral Nudges Built In</strong>
              {activeSlide.nudges?.map((n, i) => (
                <div key={i} style={{ color: 'var(--text-secondary)', marginBottom: '0.2rem' }}>• {n}</div>
              ))}
            </div>
            <div style={{ display: 'flex', flexDirection: 'column', gap: '0.35rem' }}>
              <strong style={{ fontSize: '0.65rem', color: 'var(--text-muted)', textTransform: 'uppercase' }}>Edge Cases & Mitigations Handled</strong>
              {activeSlide.edge_cases?.map((ec, idx) => (
                <div key={idx} style={{ background: 'rgba(255,255,255,0.01)', padding: '0.4rem', borderRadius: '6px', border: '1px solid rgba(255,255,255,0.03)', fontSize: '0.68rem' }}>
                  <strong style={{ color: '#fff' }}>{ec.id}: {ec.title}</strong>{' '}
                  <span style={{ color: 'var(--text-muted)' }}>→ {ec.mitigation}</span>
                </div>
              ))}
            </div>
          </div>
        </div>
      );
    case 'metrics_indicators':
      return (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem', height: '100%', overflowY: 'auto', textAlign: 'left' }}>
          <div>
            <span style={{ fontSize: '0.8rem', color: brandColor, textTransform: 'uppercase', letterSpacing: '2px', fontWeight: 'bold' }}>
              Slide {activeSlide.slide_number}: success metrics & leading indicators
            </span>
            <h2 style={{ fontSize: '1.35rem', color: '#fff', margin: 0, fontWeight: '800' }}>
              {activeSlide.headline}
            </h2>
          </div>
          {/* North Star banner */}
          <div style={{ background: 'linear-gradient(90deg, rgba(16,185,129,0.08), rgba(6,182,212,0.08))', border: '1px solid rgba(16,185,129,0.2)', padding: '0.6rem 1rem', borderRadius: '8px', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <div style={{ textAlign: 'left' }}>
              <strong style={{ color: 'var(--success)', fontSize: '0.7rem', textTransform: 'uppercase', display: 'block', letterSpacing: '0.5px' }}>★ NORTH STAR METRIC</strong>
              <span style={{ fontSize: '1rem', fontWeight: 'bold', color: '#fff' }}>{activeSlide.north_star?.name}</span>
              <p style={{ margin: '0.15rem 0 0 0', color: 'var(--text-secondary)', fontSize: '0.7rem', lineHeight: '1.3' }}>{activeSlide.north_star?.definition}</p>
            </div>
            <div style={{ textAlign: 'right', minWidth: '120px' }}>
              <div style={{ fontSize: '1.1rem', fontWeight: 'bold', color: 'var(--success)' }}>{activeSlide.north_star?.target}</div>
              <div style={{ fontSize: '0.6rem', color: 'var(--text-muted)' }}>Target Shift</div>
            </div>
          </div>
          {/* Leading Indicators */}
          <div>
            <strong style={{ fontSize: '0.7rem', color: 'var(--text-muted)', textTransform: 'uppercase', display: 'block', marginBottom: '0.35rem' }}>Leading Indicators & Action Plans</strong>
            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '0.5rem' }}>
              {activeSlide.leading_indicators?.map((li, idx) => (
                <div key={idx} style={{ background: 'rgba(255,255,255,0.02)', padding: '0.5rem', borderRadius: '6px', border: '1px solid rgba(255,255,255,0.05)', fontSize: '0.7rem' }}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '0.15rem' }}>
                    <strong style={{ color: '#fff' }}>{li.name}</strong>
                    <strong style={{ color: brandColor }}>{li.target}</strong>
                  </div>
                  <div style={{ color: 'var(--text-secondary)', fontSize: '0.65rem' }}>{li.proves}</div>
                  <div style={{ color: '#f87171', fontSize: '0.62rem', marginTop: '0.2rem', borderTop: '1px solid rgba(255,255,255,0.04)', paddingTop: '0.2rem' }}>
                    <strong>Below Target:</strong> {li.below_target_action}
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      );
    case 'failure_mitigations':
      return (
        <div style={{ display: 'grid', gridTemplateColumns: '1.1fr 0.9fr', gap: '1.5rem', height: '100%', overflowY: 'auto', textAlign: 'left' }}>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '0.6rem', justifyContent: 'center' }}>
            <span style={{ fontSize: '0.8rem', color: brandColor, textTransform: 'uppercase', letterSpacing: '2px', fontWeight: 'bold' }}>
              Slide {activeSlide.slide_number}: Failure Modes & Mitigations
            </span>
            <h2 style={{ fontSize: '1.4rem', color: '#fff', margin: 0, fontWeight: '800', lineHeight: '1.3' }}>
              {activeSlide.headline}
            </h2>
            <div style={{ display: 'flex', flexDirection: 'column', gap: '0.4rem', marginTop: '0.25rem' }}>
              {activeSlide.bullets?.map((b, i) => (
                <p key={i} style={{ color: 'var(--text-secondary)', fontSize: '0.75rem', margin: 0, lineHeight: '1.4' }}>• {b}</p>
              ))}
            </div>
            <p style={{ margin: '0.5rem 0 0 0', color: 'var(--text-muted)', fontSize: '0.75rem', fontStyle: 'italic', borderTop: '1px solid rgba(255,255,255,0.06)', paddingTop: '0.5rem' }}>
              "{activeSlide.closing_message}"
            </p>
          </div>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '0.6rem', overflowY: 'auto', paddingRight: '0.25rem' }}>
            {/* Failure table */}
            <div style={{ background: 'rgba(255,255,255,0.02)', border: '1px solid rgba(255,255,255,0.05)', borderRadius: '8px', overflow: 'hidden' }}>
              <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: '0.72rem' }}>
                <thead>
                  <tr style={{ background: 'rgba(255,255,255,0.03)', borderBottom: '1px solid rgba(255,255,255,0.06)' }}>
                    <th style={{ padding: '0.4rem', textAlign: 'left' }}>What could go wrong</th>
                    <th style={{ padding: '0.4rem', textAlign: 'left' }}>Mitigation</th>
                    <th style={{ padding: '0.4rem', textAlign: 'center' }}>Sev</th>
                  </tr>
                </thead>
                <tbody>
                  {activeSlide.failures?.map((f, i) => (
                    <tr key={i} style={{ borderBottom: '1px solid rgba(255,255,255,0.04)' }}>
                      <td style={{ padding: '0.4rem', color: 'var(--text-secondary)' }}>{f.risk}</td>
                      <td style={{ padding: '0.4rem', color: 'var(--text-secondary)' }}>{f.handling}</td>
                      <td style={{ padding: '0.4rem', textAlign: 'center' }}>
                        <span style={{ 
                          fontSize: '0.55rem', fontWeight: 'bold', padding: '1px 4px', borderRadius: '3px',
                          background: f.severity === 'CRIT' ? 'rgba(239,68,68,0.2)' : f.severity === 'HIGH' ? 'rgba(245,158,11,0.2)' : 'rgba(59,130,246,0.2)',
                          color: f.severity === 'CRIT' ? 'var(--error)' : f.severity === 'HIGH' ? 'var(--warning)' : 'var(--accent-secondary)'
                        }}>{f.severity}</span>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
            {/* Guardrails List */}
            <div style={{ display: 'flex', flexDirection: 'column', gap: '0.35rem' }}>
              <strong style={{ fontSize: '0.65rem', color: 'var(--text-muted)', textTransform: 'uppercase' }}>Guardrails to enforce</strong>
              {activeSlide.guardrails?.map((g, idx) => (
                <div key={idx} style={{ background: 'rgba(255,255,255,0.01)', padding: '0.4rem', borderRadius: '6px', border: '1px solid rgba(255,255,255,0.03)', fontSize: '0.68rem', display: 'flex', justifyContent: 'space-between' }}>
                  <span style={{ color: 'var(--text-secondary)' }}>{g.name}: <strong style={{ color: 'var(--error)' }}>{g.threshold}</strong></span>
                  <span style={{ color: 'var(--text-muted)', fontSize: '0.62rem' }}>{g.purpose}</span>
                </div>
              ))}
            </div>
          </div>
        </div>
      );
    default: {
      // Fallback to standard key-value rendering
      const skipKeys = ["title", "headline", "slide_number", "type", "speaker_notes"];
      const entries = Object.entries(activeSlide).filter(([k]) => !skipKeys.includes(k));
      return (
        <div style={{ display: 'grid', gridTemplateColumns: '1.1fr 0.9fr', gap: '1.5rem', height: '100%', overflowY: 'auto' }}>
          <div style={{ display: 'flex', flexDirection: 'column', justifyContent: 'center', gap: '1rem', textAlign: 'left' }}>
            <span style={{ fontSize: '0.8rem', color: brandColor, textTransform: 'uppercase', letterSpacing: '2px', fontWeight: 'bold' }}>
              Slide {activeSlide.slide_number}: {activeSlide.title}
            </span>
            <h2 style={{ fontSize: '1.65rem', color: '#fff', margin: 0, fontWeight: '800', lineHeight: '1.3' }}>
              {activeSlide.headline}
            </h2>
          </div>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '0.6rem', overflowY: 'auto', maxHeight: '310px', paddingRight: '0.5rem', textAlign: 'left' }}>
            {entries.slice(0, 4).map(([key, val]) => (
              <div key={key} style={{ 
                background: 'rgba(255,255,255,0.01)', padding: '0.6rem 0.8rem', borderRadius: '8px',
                border: '1px solid rgba(255,255,255,0.04)', borderLeft: `3px solid ${brandColor}`
              }}>
                <strong style={{ color: '#fff', fontSize: '0.7rem', textTransform: 'uppercase', display: 'block', marginBottom: '0.15rem' }}>{key.replace(/_/g, ' ')}</strong>
                {renderValue(val)}
              </div>
            ))}
          </div>
        </div>
      );
    }
  }
};

const Dashboard = () => {
  const [activeSection, setActiveSection] = useState('overview'); // 'overview', 'steps', 'slides', 'case_study'

  // Dashboard Overview Telemetry Data
  const [dashboardData, setDashboardData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  
  // Pipeline & Ingestion execution states
  const [pipelineRunning, setPipelineRunning] = useState(false);
  const [pipelineLogs, setPipelineLogs] = useState([]);
  const [pipelineStatus, setPipelineStatus] = useState(null);

  // Strategy Deep Dive states
  const [strategyData, setStrategyData] = useState(null);
  const [boardPresentation, setBoardPresentation] = useState(null);
  const [currentSlideIndex, setCurrentSlideIndex] = useState(0);
  const [strategyLogs, setStrategyLogs] = useState([]);
  const [completedSteps, setCompletedSteps] = useState(0);
  const [totalSteps, setTotalSteps] = useState(9);
  const [strategyStatus, setStrategyStatus] = useState('idle');

  // Prototype Markdown state
  const [prototypeMarkdown, setPrototypeMarkdown] = useState('');
  const [prototypeLoading, setPrototypeLoading] = useState(false);
  const [resynthesizing, setResynthesizing] = useState(false);

  // Survey & Case Study states
  const [generatingForm, setGeneratingForm] = useState(false);
  const [generatedFormUrl, setGeneratedFormUrl] = useState(null);
  const [uploading, setUploading] = useState(false);
  const [file, setFile] = useState(null);
  const [surveyResult, setSurveyResult] = useState(null);
  const [caseStudy, setCaseStudy] = useState(null);
  const [caseLoading, setCaseLoading] = useState(true);

  // Document exports states
  const [exportLoading, setExportLoading] = useState(false);
  const [exportDocUrl, setExportDocUrl] = useState(null);
  const [exportSlidesLoading, setExportSlidesLoading] = useState(false);
  const [exportSlidesUrl, setExportSlidesUrl] = useState(null);
  const [exportSourceLoading, setExportSourceLoading] = useState(false);

  // Collapsible step cards
  const [openSteps, setOpenSteps] = useState({});

  // Setup Date Range configurations
  const thirtyDaysAgo = new Date();
  thirtyDaysAgo.setDate(thirtyDaysAgo.getDate() - 30);
  const defaultFrom = thirtyDaysAgo.toISOString().split('T')[0];
  const defaultTo = new Date().toISOString().split('T')[0];

  const [dateRangeOption, setDateRangeOption] = useState('30days'); // '7days', '14days', '30days', 'custom'
  const [fromDate, setFromDate] = useState(defaultFrom);
  const [toDate, setToDate] = useState(defaultTo);

  const [selectedApps, setSelectedApps] = useState({
    zepto: true,
    blinkit: true,
    swiggy_instamart: true
  });

  const [appUrl, setAppUrl] = useState('');

  const [promptMode, setPromptMode] = useState('quick'); // 'quick' or 'ai_prompt'
  const [prompt, setPrompt] = useState('');
  const [parsing, setParsing] = useState(false);
  const [parsedConfig, setParsedConfig] = useState(null);

  const [problemStatement, setProblemStatement] = useState("");
  const [keywords, setKeywords] = useState("");

  const toggleStep = (stepId) => {
    setOpenSteps(prev => ({ ...prev, [stepId]: !prev[stepId] }));
  };

  const strategyProgress = Math.min(100, Math.round((completedSteps / totalSteps) * 100));

  // ── Long-running pipeline monitor (asynchronous polling) ──
  useEffect(() => {
    let intervalId;
    if (pipelineRunning) {
      intervalId = setInterval(async () => {
        try {
          // Poll main pipeline status
          const res = await fetch(`${getBackendUrl()}/api/v2/pipeline/status`);
          if (!res.ok) return;
          const statusData = await res.json();
          setPipelineStatus(statusData.status);
          setPipelineLogs(statusData.progress || []);
          
          // Poll strategy deep dive status concurrently
          const stratRes = await fetch(`${getBackendUrl()}/api/v2/reports/strategy-deep-dive`);
          if (stratRes.ok) {
            const stratData = await stratRes.json();
            setStrategyStatus(stratData.status);
            setStrategyLogs(stratData.logs || []);
            setCompletedSteps(stratData.completed_steps || 0);
            if (stratData.result) setStrategyData(stratData.result);
            if (stratData.board_presentation) setBoardPresentation(stratData.board_presentation);
          }

          if (statusData.status === 'complete' || statusData.status === 'error') {
            setPipelineRunning(false);
            clearInterval(intervalId);
            await fetchDashboardAndStrategy();
            if (statusData.status === 'error') {
              alert("Pipeline execution failed. Check backend logs.");
            } else if (statusData.status === 'complete') {
              alert("Intelligence Ingestion & Strategy Discovery (Phase 1) Complete!");
            }
          }
        } catch (err) {
          console.error("Error polling pipeline status:", err);
        }
      }, 2000);
    }
    return () => clearInterval(intervalId);
  }, [pipelineRunning]);

  // ── Phase 2 strategy deep dive monitor ──
  useEffect(() => {
    let intervalId;
    if (strategyStatus === 'running' && completedSteps >= 5) {
      intervalId = setInterval(async () => {
        try {
          const res = await fetch(`${getBackendUrl()}/api/v2/reports/strategy-deep-dive`);
          if (!res.ok) return;
          const result = await res.json();
          
          if (result.logs) setStrategyLogs(result.logs);
          if (result.completed_steps !== undefined) setCompletedSteps(result.completed_steps);
          
          if (result.status === 'completed') {
            setStrategyStatus('completed');
            clearInterval(intervalId);
            setStrategyData(result.result);
            if (result.board_presentation) setBoardPresentation(result.board_presentation);
            alert("Phase 2 & Executive Presentation completed successfully!");
            setActiveSection('slides'); // Auto-switch to board presentation tab
          } else if (result.status === 'failed') {
            setStrategyStatus('failed');
            clearInterval(intervalId);
            alert("Phase 2 compilation failed. Check console logs.");
          }
        } catch (err) {
          console.error("Error polling Phase 2 strategy:", err);
        }
      }, 2000);
    }
    return () => clearInterval(intervalId);
  }, [strategyStatus, completedSteps]);

  // ── Sync date range options ──
  useEffect(() => {
    if (dateRangeOption === 'custom') return;
    const today = new Date();
    const toStr = today.toISOString().split('T')[0];
    let days = 30;
    if (dateRangeOption === '7days') days = 7;
    else if (dateRangeOption === '14days') days = 14;
    else if (dateRangeOption === '30days') days = 30;
    
    const pastDate = new Date();
    pastDate.setDate(today.getDate() - days);
    const fromStr = pastDate.toISOString().split('T')[0];
    
    setFromDate(fromStr);
    setToDate(toStr);
  }, [dateRangeOption]);

  useEffect(() => {
    fetchDashboardAndStrategy();
    fetchCaseStudyData();
  }, []);

  async function fetchDashboardAndStrategy() {
    try {
      const statusRes = await fetch(`${getBackendUrl()}/api/v2/pipeline/status`);
      if (statusRes.ok) {
        const statusData = await statusRes.json();
        setPipelineStatus(statusData.status);
        setPipelineLogs(statusData.progress || []);
        if (statusData.status === 'collecting' || statusData.status === 'analyzing') {
          setPipelineRunning(true);
        } else {
          setPipelineRunning(false);
        }
      }

      // 2. Fetch strategy deep dive data
      const stratRes = await fetch(`${getBackendUrl()}/api/v2/reports/strategy-deep-dive`);
      let stratData = null;
      if (stratRes.ok) {
        stratData = await stratRes.json();
        setStrategyStatus(stratData.status);
        setStrategyLogs(stratData.logs || []);
        setCompletedSteps(stratData.completed_steps || 0);
        if (stratData.result) setStrategyData(stratData.result);
        if (stratData.board_presentation) setBoardPresentation(stratData.board_presentation);
      }

      // 3. Fetch dashboard telemetry
      const response = await fetch(`${getBackendUrl()}/api/v2/dashboard/overview`);
      if (response.ok) {
        const result = await response.json();
        // Sync personas and opportunities count from strategy deep dive if available
        if (stratData?.result?.segmentation?.user_segments?.length && (!result.personas_count || result.personas_count === 0)) {
          result.personas_count = stratData.result.segmentation.user_segments.length;
        }
        if (stratData?.result?.segmentation?.growth_opportunities?.length && (!result.opportunities_count || result.opportunities_count === 0)) {
          result.opportunities_count = stratData.result.segmentation.growth_opportunities.length;
        }

        // Auto-restore input parameters from last run session
        if (result.input_params) {
          if (result.input_params.problem_statement) setProblemStatement(result.input_params.problem_statement);
          if (result.input_params.keywords) setKeywords(result.input_params.keywords);
          if (result.input_params.app_name) setAppName(result.input_params.app_name);
          if (result.input_params.custom_package_name) setCustomPackageName(result.input_params.custom_package_name);
          if (result.input_params.custom_app_store_id) setCustomAppStoreId(result.input_params.custom_app_store_id);
          if (result.input_params.from_date) setFromDate(result.input_params.from_date);
          if (result.input_params.to_date) setToDate(result.input_params.to_date);
        }

        setDashboardData(result);
      }
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }

  const handleClearCache = async () => {
    if (!window.confirm("Are you sure you want to clear the previous session data and start completely fresh?")) return;
    try {
      await fetch(`${getBackendUrl()}/api/v2/cache/clear`, { method: 'POST' });
      setDashboardData(null);
      setStrategyData(null);
      setBoardPresentation(null);
      setPipelineLogs([]);
      setPipelineStatus('idle');
      setStrategyLogs([]);
      setStrategyStatus('idle');
      setCompletedSteps(0);
      alert("Session cache cleared! You can now start a brand new research session.");
    } catch (err) {
      console.error("Failed to clear cache:", err);
    }
  };

  async function fetchCaseStudyData() {
    try {
      const res = await fetch(`${getBackendUrl()}/api/v2/reports/mvp-case`);
      if (res.ok) {
        const result = await res.json();
        setCaseStudy(result);
      }
    } catch (err) {
      console.error("Failed to load case study:", err);
    } finally {
      setCaseLoading(false);
    }
  }

  const handleParsePrompt = async (e) => {
    e.preventDefault();
    if (!prompt.trim()) return;

    setParsing(true);
    setError(null);
    setParsedConfig(null);

    try {
      const res = await fetch(`${getBackendUrl()}/api/v2/pipeline/parse-prompt`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ prompt })
      });
      if (!res.ok) throw new Error("Failed to parse prompt command");
      const config = await res.json();
      setParsedConfig(config);
    } catch (err) {
      setError(err.message);
    } finally {
      setParsing(false);
    }
  };

  const handleLaunchAIPipeline = async () => {
    if (!parsedConfig) return;
    setPipelineRunning(true);
    setPipelineLogs(["[SYSTEM] Initiating AI custom intelligence run..."]);
    try {
      const res = await fetch(`${getBackendUrl()}/api/v2/pipeline/run`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          ...parsedConfig,
          problem_statement: problemStatement,
          keywords: keywords
        })
      });
      if (!res.ok) throw new Error("Pipeline run encountered a server error");
      const result = await res.json();
      setPipelineLogs(result.progress || []);
    } catch (err) {
      setError(err.message);
      setPipelineRunning(false);
    }
  };

  const getParsedUrlConfig = () => {
    if (!appUrl.trim()) return null;
    let playStorePackage = null;
    let appStoreId = null;
    let detectedApp = "custom";
    let detectedAppName = "Custom App";

    if (appUrl.includes('play.google.com') || appUrl.includes('details?id=')) {
      const match = appUrl.match(/(?:id=)([^&?#\s]+)/);
      if (match) playStorePackage = match[1];
    } else if (appUrl.includes('apps.apple.com') || appUrl.includes('/id')) {
      const match = appUrl.match(/\/id(\d+)/) || appUrl.match(/id[=]?(\d+)/);
      if (match) appStoreId = match[1];
    }

    if (!playStorePackage && !appStoreId) {
      playStorePackage = appUrl.trim();
      detectedAppName = appUrl.trim();
    }

    if (playStorePackage === 'com.zeptoconsumerapp' || appStoreId === '1575323645') {
      detectedApp = 'zepto';
      detectedAppName = 'Zepto';
    } else if (playStorePackage === 'com.grofers.customerapp' || appStoreId === '960335206') {
      detectedApp = 'blinkit';
      detectedAppName = 'Blinkit';
    } else if (playStorePackage === 'in.swiggy.android' || appStoreId === '989540920') {
      detectedApp = 'swiggy_instamart';
      detectedAppName = 'Swiggy Instamart';
    }

    return {
      apps: detectedApp !== 'custom' ? [detectedApp] : [],
      play_store_package: playStorePackage,
      app_store_id: appStoreId,
      appName: detectedAppName
    };
  };

  const handleRunPipeline = async () => {
    const parsed = getParsedUrlConfig();
    if (!parsed) {
      alert("Please enter a valid Google Play Store or Apple App Store URL (e.g. for Blinkit or Zepto).");
      return;
    }
    const confirm = window.confirm(`This will trigger collection & multi-agent strategy analysis for ${parsed.appName}. Continue?`);
    if (!confirm) return;
    
    try {
      setPipelineRunning(true);
      setPipelineLogs(["[SYSTEM] Initiating intelligence run with custom problem statement..."]);
      const response = await fetch(`${getBackendUrl()}/api/v2/pipeline/run`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          apps: parsed.apps,
          play_store_package: parsed.play_store_package,
          app_store_id: parsed.app_store_id,
          from_date: fromDate,
          to_date: toDate,
          include_reddit: true,
          include_youtube: true,
          problem_statement: problemStatement,
          keywords: keywords
        })
      });
      if (!response.ok) throw new Error('Pipeline failed to initiate');
    } catch (err) {
      alert("Error: " + err.message);
      setPipelineRunning(false);
    }
  };

  // ── Survey validation & exports ──
  const handleSurveyUpload = async () => {
    if (!file) return alert("Please select a Survey Responses CSV file first.");
    setUploading(true);
    const formData = new FormData();
    formData.append('file', file);
    try {
      const res = await fetch(`${getBackendUrl()}/api/v2/surveys/upload`, {
        method: 'POST',
        body: formData
      });
      const data = await res.json();
      if (res.ok) {
        setSurveyResult(data);
        setStrategyStatus('running');
        setCompletedSteps(5); // Transition back to running Phase 2
        alert("Survey uploaded successfully! Resuming Phase 2 Strategy Compilation.");
      } else {
        alert(data.detail || 'Failed to upload survey');
      }
    } catch (err) {
      alert('Error uploading survey file');
    } finally {
      setUploading(false);
    }
  };

  const handleGenerateForm = async () => {
    setGeneratingForm(true);
    try {
      const res = await fetch(`${getBackendUrl()}/api/v2/research/generate-form`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          product_name: "Quick Commerce Platform",
          problem_statement: problemStatement,
          product_description: "Consolidated multi-agent shopping behaviors analysis",
          target_segment: "All platform users",
          key_features: "Behavioral discovery feed",
          assumptions: "Users stick to habit loops and avoid discovery of non-grocery categories"
        })
      });
      const resData = await res.json();
      if (res.ok) {
        if (resData.form_url) setGeneratedFormUrl(resData.form_url);
        else alert("Survey generated successfully and saved.");
      } else {
        alert(resData.detail || "Failed to generate Google Form.");
      }
    } catch (err) {
      alert("Error generating form: " + err.message);
    } finally {
      setGeneratingForm(false);
    }
  };

  const handleExportDoc = async () => {
    try {
      setExportLoading(true);
      const res = await fetch(`${getBackendUrl()}/api/v2/reports/strategy-deep-dive/export-doc`, { method: 'POST' });
      const resData = await res.json();
      if (res.ok) setExportDocUrl(resData.doc_url);
      else alert(resData.detail || "Export to Google Doc failed.");
    } catch (err) {
      alert("Error: " + err.message);
    } finally {
      setExportLoading(false);
    }
  };

  const handleExportSlides = async () => {
    try {
      setExportSlidesLoading(true);
      const res = await fetch(`${getBackendUrl()}/api/v2/reports/strategy-deep-dive/export-slides`, { method: 'POST' });
      const resData = await res.json();
      if (res.ok) setExportSlidesUrl(resData.presentation_url);
      else alert(resData.detail || "Export to Google Slides failed.");
    } catch (err) {
      alert("Error: " + err.message);
    } finally {
      setExportSlidesLoading(false);
    }
  };

  const handleExportSource = async () => {
    try {
      setExportSourceLoading(true);
      const res = await fetch(`${getBackendUrl()}/api/v2/reports/strategy-deep-dive/export-markdown`);
      const resData = await res.json();
      if (res.ok) {
        const blob = new Blob([resData.markdown_content], { type: "text/markdown" });
        const href = URL.createObjectURL(blob);
        const link = document.createElement("a");
        link.href = href;
        link.download = "strategy_deep_dive_report.md";
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
        URL.revokeObjectURL(href);
      } else {
        alert(resData.detail || "Markdown export failed.");
      }
    } catch (err) {
      alert("Error: " + err.message);
    } finally {
      setExportSourceLoading(false);
    }
  };

  const fetchPrototypeMarkdown = async () => {
    if (prototypeMarkdown) return;
    setPrototypeLoading(true);
    try {
      const res = await fetch(`${getBackendUrl()}/api/v2/reports/mvp-workspace`);
      if (res.ok) {
        const data = await res.json();
        setPrototypeMarkdown(data.markdown || "# Prototype PRD\n\nNo prototype data generated.");
      }
    } catch (err) {
      console.error("Failed to fetch prototype markdown:", err);
    } finally {
      setPrototypeLoading(false);
    }
  };

  const handleDownloadPrototypeMarkdown = () => {
    if (!prototypeMarkdown) return;
    const blob = new Blob([prototypeMarkdown], { type: 'text/markdown;charset=utf-8;' });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.setAttribute('download', 'mvp_prototype_spec.md');
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  const handleResynthesizeCache = async () => {
    try {
      setResynthesizing(true);
      const res = await fetch(`${getBackendUrl()}/api/v2/reports/resynthesize-cache`, { method: 'POST' });
      const data = await res.json();
      if (res.ok) {
        if (data.board_presentation) setBoardPresentation(data.board_presentation);
        if (data.mvp_workspace_prd) setPrototypeMarkdown(data.mvp_workspace_prd);
        alert("✅ Presentation slides and prototype markdown successfully re-synthesized from cache!");
      } else {
        alert(data.detail || "Re-synthesis failed.");
      }
    } catch (err) {
      alert("Error re-synthesizing cache: " + err.message);
    } finally {
      setResynthesizing(false);
    }
  };

  const handleNextSlide = () => {
    if (boardPresentation && currentSlideIndex < boardPresentation.slides.length - 1) {
      setCurrentSlideIndex(prev => prev + 1);
    }
  };

  const handlePrevSlide = () => {
    if (currentSlideIndex > 0) {
      setCurrentSlideIndex(prev => prev - 1);
    }
  };

  const COLORS = ['#8b5cf6', '#3b82f6', '#f59e0b', '#ef4444', '#10b981'];

  // Calculate sentiment data for Recharts Pie
  const sentimentChartData = dashboardData?.sentiment_summary ? [
    { name: 'Positive', value: Math.round(dashboardData.sentiment_summary.positive * 100) },
    { name: 'Neutral', value: Math.round(dashboardData.sentiment_summary.neutral * 100) },
    { name: 'Negative', value: Math.round(dashboardData.sentiment_summary.negative * 100) },
  ].filter(d => d.value > 0) : [];

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
      
      {/* ── Consolidated Header & Tab Switcher ── */}
      <div className="page-header" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: '1rem' }}>
        <div>
          <h1 className="page-title text-gradient">Dashboard Hub</h1>
          <p className="page-subtitle">Consolidated Ingestion, Multi-Agent UX Strategy Framework, and McKinsey Board Slides.</p>
        </div>

        {/* Tab switch bar */}
        <div className="glass-panel" style={{ display: 'flex', padding: '0.25rem', borderRadius: '8px', gap: '0.25rem' }}>
          <button 
            onClick={() => setActiveSection('overview')}
            style={{
              padding: '0.5rem 1rem', borderRadius: '6px', border: 'none',
              background: activeSection === 'overview' ? 'var(--accent-primary)' : 'transparent',
              color: activeSection === 'overview' ? '#fff' : 'var(--text-secondary)',
              cursor: 'pointer', fontWeight: '600', transition: 'all 0.2s ease'
            }}
          >
            Overview
          </button>
          <button 
            onClick={() => setActiveSection('steps')}
            style={{
              padding: '0.5rem 1rem', borderRadius: '6px', border: 'none',
              background: activeSection === 'steps' ? 'var(--accent-primary)' : 'transparent',
              color: activeSection === 'steps' ? '#fff' : 'var(--text-secondary)',
              cursor: 'pointer', fontWeight: '600', transition: 'all 0.2s ease',
              opacity: strategyData ? 1 : 0.5
            }}
            disabled={!strategyData}
          >
            Deep Dive Steps
          </button>
          <button 
            onClick={() => setActiveSection('slides')}
            style={{
              padding: '0.5rem 1rem', borderRadius: '6px', border: 'none',
              background: activeSection === 'slides' ? 'var(--accent-primary)' : 'transparent',
              color: activeSection === 'slides' ? '#fff' : 'var(--text-secondary)',
              cursor: 'pointer', fontWeight: '600', transition: 'all 0.2s ease',
              opacity: boardPresentation ? 1 : 0.5
            }}
            disabled={!boardPresentation}
          >
            Board Slides
          </button>
          <button 
            onClick={() => {
              setActiveSection('prototype');
              fetchPrototypeMarkdown();
            }}
            style={{
              padding: '0.5rem 1rem', borderRadius: '6px', border: 'none',
              background: activeSection === 'prototype' ? 'var(--accent-primary)' : 'transparent',
              color: activeSection === 'prototype' ? '#fff' : 'var(--text-secondary)',
              cursor: 'pointer', fontWeight: '600', transition: 'all 0.2s ease',
              opacity: strategyData ? 1 : 0.5
            }}
            disabled={!strategyData}
          >
            Prototype Markdown
          </button>
        </div>
      </div>

      {/* ── TAB CONTENT ── */}

      {/* 1. OVERVIEW TAB */}
      {activeSection === 'overview' && (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
          
          {/* Controls Panel */}
          <div className="glass-card" style={{ display: 'flex', flexDirection: 'column', gap: '1.25rem', padding: '1.5rem', textAlign: 'left' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: '0.75rem' }}>
              <h3 style={{ margin: 0, display: 'flex', alignItems: 'center', gap: '8px', color: '#fff', fontSize: '1.1rem' }}>
                <Layers size={18} color="var(--accent-primary)" /> Pipeline Configuration Controls
              </h3>
              {dashboardData?.has_cached_session && (
                <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                  <span style={{ fontSize: '0.75rem', background: 'rgba(59, 130, 246, 0.15)', color: '#93c5fd', padding: '0.25rem 0.6rem', borderRadius: '6px', border: '1px solid rgba(59, 130, 246, 0.3)', fontWeight: '600' }}>
                    ⚡ Session Restored ({dashboardData.last_updated ? new Date(dashboardData.last_updated).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }) : 'Active Cache'})
                  </span>
                  <button
                    onClick={handleClearCache}
                    style={{
                      background: 'rgba(239, 68, 68, 0.15)',
                      border: '1px solid rgba(239, 68, 68, 0.3)',
                      color: '#fca5a5',
                      padding: '0.25rem 0.6rem',
                      borderRadius: '6px',
                      cursor: 'pointer',
                      fontSize: '0.75rem',
                      fontWeight: '600'
                    }}
                    title="Clear cached session to start with empty inputs"
                  >
                    Clear Session
                  </button>
                </div>
              )}
            </div>
            
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(240px, 1fr))', gap: '1rem', marginTop: '0.5rem' }}>
              
              {/* URL Input */}
              <div style={{ background: 'rgba(255,255,255,0.01)', padding: '0.75rem', borderRadius: '8px', border: '1px solid var(--border-glass)', display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
                <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)', display: 'block', fontWeight: 'bold' }}>APP STORE OR PLAY STORE URL</span>
                <input 
                  type="text" 
                  value={appUrl} 
                  onChange={(e) => setAppUrl(e.target.value)}
                  placeholder="Enter Play Store / App Store URL (Zepto, Blinkit, etc.)"
                  style={{ width: '100%', background: 'var(--bg-secondary)', color: '#fff', border: '1px solid var(--border)', borderRadius: '4px', padding: '0.35rem 0.5rem', fontSize: '0.85rem' }}
                />
                {appUrl.trim() && (
                  <div style={{ fontSize: '0.75rem', color: getParsedUrlConfig() ? 'var(--accent-primary)' : 'var(--danger)', marginTop: '0.1rem' }}>
                    {getParsedUrlConfig() ? `Detected: ${getParsedUrlConfig().appName} (${getParsedUrlConfig().play_store_package || getParsedUrlConfig().app_store_id})` : '⚠️ Invalid App/Play Store URL'}
                  </div>
                )}
              </div>

              {/* Date Filters */}
              <div style={{ display: 'flex', gap: '0.5rem', background: 'rgba(255,255,255,0.01)', padding: '0.75rem', borderRadius: '8px', border: '1px solid var(--border-glass)' }}>
                <div style={{ flex: 1 }}>
                  <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)', display: 'block', marginBottom: '0.25rem', fontWeight: 'bold' }}>RANGE</span>
                  <select 
                    value={dateRangeOption} 
                    onChange={(e) => setDateRangeOption(e.target.value)}
                    style={{ width: '100%', background: 'var(--bg-secondary)', color: '#fff', border: '1px solid var(--border)', borderRadius: '4px', padding: '0.3rem' }}
                  >
                    <option value="7days">Past 7 Days</option>
                    <option value="14days">Past 14 Days</option>
                    <option value="30days">Past 30 Days (Recommended)</option>
                    <option value="custom">Custom Range</option>
                  </select>
                </div>
                {dateRangeOption === 'custom' && (
                  <>
                    <div>
                      <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)', display: 'block', marginBottom: '0.25rem' }}>FROM</span>
                      <input type="date" value={fromDate} onChange={(e) => setFromDate(e.target.value)} style={{ background: 'var(--bg-secondary)', color: '#fff', border: '1px solid var(--border)', borderRadius: '4px', padding: '0.2rem' }} />
                    </div>
                    <div>
                      <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)', display: 'block', marginBottom: '0.25rem' }}>TO</span>
                      <input type="date" value={toDate} onChange={(e) => setToDate(e.target.value)} style={{ background: 'var(--bg-secondary)', color: '#fff', border: '1px solid var(--border)', borderRadius: '4px', padding: '0.2rem' }} />
                    </div>
                  </>
                )}
              </div>

              {/* Keyword Filter Input */}
              <div style={{ background: 'rgba(255,255,255,0.01)', padding: '0.75rem', borderRadius: '8px', border: '1px solid var(--border-glass)', display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
                <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)', display: 'block', fontWeight: 'bold' }}>REVIEW FILTER KEYWORDS</span>
                <input 
                  type="text" 
                  value={keywords} 
                  onChange={(e) => setKeywords(e.target.value)}
                  placeholder="Enter keywords (comma-separated, e.g. delay, checkout)"
                  style={{ width: '100%', background: 'var(--bg-secondary)', color: '#fff', border: '1px solid var(--border)', borderRadius: '4px', padding: '0.35rem 0.5rem', fontSize: '0.85rem' }}
                />
                <div style={{ fontSize: '0.72rem', color: 'var(--text-muted)' }}>
                  Only process reviews containing these terms (optional)
                </div>
              </div>
            </div>

            {/* Problem Statement Box */}
            <div>
              <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)', display: 'block', marginBottom: '0.35rem', fontWeight: 'bold' }}>ACTIVE RESEARCH HYPOTHESIS / PROBLEM STATEMENT</span>
              <textarea 
                value={problemStatement}
                onChange={(e) => setProblemStatement(e.target.value)}
                style={{ width: '100%', minHeight: '80px', background: 'var(--bg-secondary)', color: '#cbd5e1', border: '1px solid var(--border)', borderRadius: '6px', padding: '0.6rem', fontSize: '0.85rem', lineHeight: '1.4' }}
              />
            </div>

            {/* Launch Button */}
            <div style={{ display: 'flex', justifyContent: 'flex-end', marginTop: '0.25rem' }}>
              <button 
                className="btn-primary" 
                onClick={handleRunPipeline}
                disabled={pipelineRunning}
                style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', padding: '0.65rem 1.75rem', fontSize: '0.9rem' }}
              >
                {pipelineRunning ? <Loader2 size={16} style={{ animation: 'spin 1s linear infinite' }} /> : <Play size={16} />}
                {pipelineRunning ? 'Ingesting & Discovering Phase 1...' : '🚀 Launch Ingestion Pipeline'}
              </button>
            </div>
          </div>

          {/* ── Phase 1 / Active Logs Panel ── */}
          {((pipelineRunning || pipelineStatus === 'complete' || pipelineStatus === 'error') && pipelineLogs.length > 0) && (
            <div className="glass-panel" style={{ 
              padding: '1.25rem', 
              border: `1px solid ${pipelineStatus === 'error' ? 'rgba(239, 68, 68, 0.4)' : pipelineStatus === 'complete' ? 'rgba(16, 185, 129, 0.4)' : 'rgba(59, 130, 246, 0.3)'}`, 
              borderRadius: '10px', 
              textAlign: 'left' 
            }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '0.75rem' }}>
                <h4 style={{ 
                  color: pipelineStatus === 'error' ? 'var(--error)' : pipelineStatus === 'complete' ? 'var(--success)' : 'var(--accent-primary)', 
                  margin: 0, 
                  display: 'flex', 
                  alignItems: 'center', 
                  gap: '6px' 
                }}>
                  {pipelineRunning && <Loader2 size={16} style={{ animation: 'spin 1s linear infinite' }} />}
                  {pipelineStatus === 'error' && '❌ Ingestion Pipeline Failed'}
                  {pipelineStatus === 'complete' && '✅ Ingestion Pipeline Complete'}
                  {pipelineStatus !== 'error' && pipelineStatus !== 'complete' && '🚀 Ingestion Pipeline Running...'}
                </h4>
                <span style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>Status: {pipelineStatus}</span>
              </div>
              
              <div style={{
                background: '#090e18', 
                color: pipelineStatus === 'error' ? '#f87171' : '#10b981', 
                fontFamily: 'monospace', 
                padding: '1rem', 
                borderRadius: '6px',
                maxHeight: '200px', 
                overflowY: 'auto', 
                fontSize: '0.8rem', 
                display: 'flex', 
                flexDirection: 'column', 
                gap: '0.25rem',
                border: '1px solid rgba(255,255,255,0.03)'
              }}>
                {pipelineLogs.map((log, idx) => <div key={idx}>{log}</div>)}
              </div>
            </div>
          )}

          {/* ── Active Awaiting Survey Validation Banner ── */}
          {strategyStatus === 'awaiting_survey' && !pipelineRunning && (
            <div className="glass-panel" style={{ padding: '1.5rem', background: 'rgba(139, 92, 246, 0.08)', border: '1px solid rgba(139, 92, 246, 0.3)', borderRadius: '12px', textAlign: 'left' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', color: '#a78bfa', marginBottom: '0.5rem' }}>
                <Shield size={20} />
                <h3 style={{ margin: 0, fontSize: '1.1rem' }}>Hypothesis Validation & Survey Upload Required</h3>
              </div>
              <p style={{ color: 'var(--text-secondary)', fontSize: '0.9rem', margin: '0 0 1.25rem 0', lineHeight: '1.5' }}>
                Phase 1 (Discovery) completed successfully. To proceed to Phase 2 (Solution Synthesis, Presentation Deck Generation, Evidence Traceability, and McKinsey Strategy Audit), generate the survey form and upload the respondents' CSV data.
              </p>

              <div style={{ display: 'flex', gap: '1rem', flexWrap: 'wrap', alignItems: 'center' }}>
                <button 
                  className="btn-primary" 
                  onClick={handleGenerateForm} 
                  disabled={generatingForm}
                  style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', background: 'linear-gradient(135deg, #8b5cf6, #7c3aed)' }}
                >
                  {generatingForm ? <Loader2 size={16} style={{ animation: 'spin 1s linear infinite' }} /> : <Layers size={16} />}
                  {generatingForm ? 'Generating Form...' : '⚡ Generate Google Form Survey'}
                </button>

                <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', background: 'var(--surface-light)', padding: '0.25rem 0.5rem', borderRadius: '6px', border: '1px solid var(--border)' }}>
                  <input 
                    type="file" 
                    accept=".csv"
                    onChange={(e) => setFile(e.target.files[0])}
                    style={{ color: '#fff', fontSize: '0.85rem' }}
                  />
                  <button 
                    className="btn-secondary" 
                    onClick={handleSurveyUpload}
                    disabled={uploading || !file}
                    style={{ padding: '0.4rem 1rem' }}
                  >
                    {uploading ? <Loader2 size={14} style={{ animation: 'spin 1s linear infinite' }} /> : <Upload size={14} />}
                    Upload CSV
                  </button>
                </div>
              </div>

              {generatedFormUrl && (
                <div style={{ marginTop: '1rem', padding: '0.75rem', background: 'rgba(16, 185, 129, 0.05)', borderRadius: '6px', border: '1px solid rgba(16, 185, 129, 0.2)' }}>
                  <span style={{ fontSize: '0.85rem', color: '#10b981' }}>👉 Form created! Send this link to respondents, then download the responses sheet as CSV: </span>
                  <a href={generatedFormUrl} target="_blank" rel="noopener noreferrer" style={{ color: 'var(--accent-primary)', fontWeight: 'bold', fontSize: '0.85rem', textDecoration: 'underline' }}>{generatedFormUrl}</a>
                </div>
              )}
            </div>
          )}

          {/* ── Phase 2 running / compile progress ── */}
          {strategyStatus === 'running' && completedSteps >= 5 && (
            <div className="glass-panel" style={{ padding: '1.5rem', border: '1px solid rgba(16, 185, 129, 0.3)', borderRadius: '12px', textAlign: 'left' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '0.5rem', alignItems: 'center' }}>
                <h4 style={{ color: '#10b981', margin: 0, display: 'flex', alignItems: 'center', gap: '6px' }}>
                  <Loader2 size={16} style={{ animation: 'spin 1s linear infinite' }} /> Running Strategy Phase 2 Compilation...
                </h4>
                <span style={{ color: 'var(--accent-primary)', fontWeight: 'bold' }}>{strategyProgress}% Complete</span>
              </div>
              <div style={{ height: '6px', background: 'var(--bg-secondary)', borderRadius: '3px', overflow: 'hidden', marginBottom: '1rem' }}>
                <div style={{ height: '100%', width: `${strategyProgress}%`, background: 'linear-gradient(90deg, #10b981, #059669)', borderRadius: '3px', transition: 'width 0.5s ease' }} />
              </div>

              <div style={{
                background: '#090e18', color: '#10b981', fontFamily: 'monospace', padding: '1rem', borderRadius: '6px',
                maxHeight: '180px', overflowY: 'auto', fontSize: '0.8rem', display: 'flex', flexDirection: 'column', gap: '0.25rem',
                border: '1px solid rgba(255,255,255,0.03)'
              }}>
                {strategyLogs.slice().reverse().map((log, idx) => <div key={idx}>{log}</div>)}
              </div>
            </div>
          )}

          {/* Telemetry charts and metrics */}
          {dashboardData ? (
            <>
              {/* Metric Cards */}
              <div className="grid-4">
                <div className="glass-panel metric-card">
                  <div className="metric-icon" style={{ color: 'var(--accent-primary)' }}><MessageSquare size={22} /></div>
                  <div className="metric-value">{dashboardData.total_signals}</div>
                  <div className="metric-label">Unified Signals Ingested</div>
                </div>
                <div className="glass-panel metric-card">
                  <div className="metric-icon" style={{ color: 'var(--success)' }}><TrendingUp size={22} /></div>
                  <div className="metric-value">
                    {Math.round((dashboardData.sentiment_summary?.positive || 0) * 100)}%
                  </div>
                  <div className="metric-label">Positive Sentiment Rate</div>
                </div>
                <div className="glass-panel metric-card">
                  <div className="metric-icon" style={{ color: 'var(--accent-secondary)' }}><Users size={22} /></div>
                  <div className="metric-value">{dashboardData.personas_count ?? 0}</div>
                  <div className="metric-label">User Segments Clustered</div>
                </div>
                <div className="glass-panel metric-card">
                  <div className="metric-icon" style={{ color: 'var(--warning)' }}><AlertTriangle size={22} /></div>
                  <div className="metric-value">{dashboardData.opportunities_count ?? 0}</div>
                  <div className="metric-label">Growth Opportunities Mapped</div>
                </div>
              </div>

              {/* Charts & Lists Row */}
              <div className="grid-2" style={{ gridTemplateColumns: '4fr 6fr', gap: '1.5rem' }}>
                
                {/* Sentiment Distribution Pie */}
                <div className="glass-panel" style={{ padding: '1.5rem', display: 'flex', flexDirection: 'column' }}>
                  <h3 style={{ margin: '0 0 1rem 0', color: '#fff', fontSize: '1rem', textAlign: 'left' }}>Sentiment Distribution</h3>
                  <div style={{ width: '100%', height: '220px', position: 'relative' }}>
                    {sentimentChartData.length > 0 ? (
                      <ResponsiveContainer width="100%" height="100%">
                        <PieChart>
                          <Pie
                            data={sentimentChartData}
                            cx="50%"
                            cy="50%"
                            innerRadius={60}
                            outerRadius={80}
                            paddingAngle={5}
                            dataKey="value"
                          >
                            <Cell fill="#10b981" />
                            <Cell fill="#64748b" />
                            <Cell fill="#ef4444" />
                          </Pie>
                          <Tooltip formatter={(value) => `${value}%`} />
                        </PieChart>
                      </ResponsiveContainer>
                    ) : (
                      <p style={{ color: 'var(--text-muted)', paddingTop: '90px' }}>No sentiment data</p>
                    )}
                    <div style={{ position: 'absolute', top: '48%', left: '50%', transform: 'translate(-50%, -50%)', textAlign: 'center' }}>
                      <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)', textTransform: 'uppercase' }}>OVERALL</span>
                      <h4 style={{ margin: 0, color: '#fff', fontSize: '1.25rem' }}>Sentiment</h4>
                    </div>
                  </div>
                  <div style={{ display: 'flex', justifyContent: 'center', gap: '1.5rem', fontSize: '0.8rem', marginTop: '0.5rem' }}>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '6px', color: '#fff' }}>
                      <div style={{ width: '8px', height: '8px', borderRadius: '50%', background: '#10b981' }}></div> Positive
                    </div>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '6px', color: '#fff' }}>
                      <div style={{ width: '8px', height: '8px', borderRadius: '50%', background: '#64748b' }}></div> Neutral
                    </div>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '6px', color: '#fff' }}>
                      <div style={{ width: '8px', height: '8px', borderRadius: '50%', background: '#ef4444' }}></div> Negative
                    </div>
                  </div>
                </div>

                {/* Top Themes & Barriers list */}
                <div style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
                  
                  {/* Top Themes */}
                  <div className="glass-panel" style={{ padding: '1.5rem', textAlign: 'left' }}>
                    <h3 style={{ margin: '0 0 1rem 0', color: '#fff', fontSize: '1.1rem' }}>Top Clustered Feedback Themes</h3>
                    <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
                      {dashboardData.top_themes?.slice(0, 3).map((theme, i) => (
                        <div key={i} style={{ background: 'rgba(255,255,255,0.02)', padding: '0.75rem', borderRadius: '8px', border: '1px solid var(--border-glass)', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                          <div>
                            <h4 style={{ margin: '0 0 0.25rem 0', color: '#fff', fontSize: '0.9rem' }}>{theme.title}</h4>
                            <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>Confidence Score: {Math.round(theme.confidence * 100)}%</span>
                          </div>
                          <span style={{ background: 'var(--accent-primary-alpha)', color: 'var(--accent-primary)', fontSize: '0.75rem', padding: '0.2rem 0.5rem', borderRadius: '4px', fontWeight: 'bold' }}>
                            {theme.mentions} Mentions
                          </span>
                        </div>
                      ))}
                    </div>
                  </div>

                  {/* Barriers */}
                  <div className="glass-panel" style={{ padding: '1.5rem', textAlign: 'left' }}>
                    <h3 style={{ margin: '0 0 1rem 0', color: '#fff', fontSize: '1.1rem' }}>Primary Category Exploration Barriers</h3>
                    <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
                      {dashboardData.top_barriers?.slice(0, 3).map((barrier, i) => (
                        <div key={i} style={{ background: 'rgba(255,255,255,0.02)', padding: '0.75rem', borderRadius: '8px', border: '1px solid var(--border-glass)', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                          <div>
                            <h4 style={{ margin: '0 0 0.25rem 0', color: '#fff', fontSize: '0.9rem' }}>{barrier.category} Avoidance</h4>
                            <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>Barrier Type: <strong style={{ color: 'var(--accent-secondary)' }}>{barrier.type}</strong></span>
                          </div>
                          <span style={{ background: 'rgba(239, 68, 68, 0.1)', color: '#ef4444', fontSize: '0.75rem', padding: '0.2rem 0.5rem', borderRadius: '4px', fontWeight: 'bold' }}>
                            Conf: {Math.round(barrier.confidence * 100)}%
                          </span>
                        </div>
                      ))}
                    </div>
                  </div>

                </div>

              </div>
            </>
          ) : (
            <div className="glass-card" style={{ padding: '4rem', textAlign: 'center' }}>
              <Database size={48} color="var(--text-muted)" style={{ marginBottom: '1rem' }} />
              <h3 style={{ color: '#fff', margin: '0 0 0.5rem 0' }}>No Ingestion Data Available</h3>
              <p style={{ color: 'var(--text-secondary)', margin: 0 }}>Select your app sources and click "Launch Ingestion Pipeline" to query and scrub customer signals.</p>
            </div>
          )}
        </div>
      )}

      {/* 2. STRATEGY DEEP DIVE STEPS TAB */}
      {activeSection === 'steps' && strategyData && (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
          
          {/* Action Bar */}
          <div style={{ display: 'flex', justifyContent: 'flex-end', gap: '1rem', flexWrap: 'wrap' }}>
            <button className="btn-secondary" onClick={handleExportDoc} disabled={exportLoading} style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
              {exportLoading ? <Loader2 size={16} style={{ animation: 'spin 1s linear infinite' }} /> : <FileText size={16} />}
              Export Google Doc
            </button>
            <button className="btn-secondary" onClick={handleExportSlides} disabled={exportSlidesLoading} style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
              {exportSlidesLoading ? <Loader2 size={16} style={{ animation: 'spin 1s linear infinite' }} /> : <Presentation size={16} />}
              Export Google Slides
            </button>
            <button className="btn-secondary" onClick={handleExportSource} disabled={exportSourceLoading} style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
              {exportSourceLoading ? <Loader2 size={16} style={{ animation: 'spin 1s linear infinite' }} /> : <Download size={16} />}
              Download Deep Dive MD
            </button>
            <button className="btn-secondary" onClick={handleResynthesizeCache} disabled={resynthesizing} style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', background: 'rgba(139, 92, 246, 0.15)', border: '1px solid rgba(139, 92, 246, 0.4)', color: '#a78bfa' }}>
              {resynthesizing ? <Loader2 size={16} style={{ animation: 'spin 1s linear infinite' }} /> : <RefreshCw size={16} />}
              Re-synthesize Outputs from Cache
            </button>
            <button className="btn-primary" onClick={handleDownloadPrototypeMarkdown} style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
              <Download size={16} />
              Download Prototype PRD (.MD)
            </button>
          </div>

          {exportDocUrl && (
            <div className="glass-panel" style={{ padding: '1rem', background: 'rgba(16, 185, 129, 0.1)', border: '1px solid rgba(16, 185, 129, 0.3)', borderRadius: '8px', textAlign: 'left' }}>
              <span style={{ color: '#10b981', fontWeight: 'bold' }}>✅ Google Doc created successfully! </span>
              <a href={exportDocUrl} target="_blank" rel="noopener noreferrer" style={{ color: 'var(--accent-primary)', textDecoration: 'underline' }}>View Google Doc</a>
            </div>
          )}

          {exportSlidesUrl && (
            <div className="glass-panel" style={{ padding: '1rem', background: 'rgba(16, 185, 129, 0.1)', border: '1px solid rgba(16, 185, 129, 0.3)', borderRadius: '8px', textAlign: 'left' }}>
              <span style={{ color: '#10b981', fontWeight: 'bold' }}>✅ Google Slides presentation generated! </span>
              <a href={exportSlidesUrl} target="_blank" rel="noopener noreferrer" style={{ color: 'var(--accent-primary)', textDecoration: 'underline' }}>View Presentation</a>
            </div>
          )}

          {/* Live Strategy Progress Bar */}
          <div style={{ padding: '0 0.5rem' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '0.5rem' }}>
              <span style={{ color: 'var(--text-secondary)', fontSize: '0.85rem' }}>Deep Strategy Framework Steps</span>
              <span style={{ color: 'var(--accent-primary)', fontWeight: 'bold', fontSize: '0.85rem' }}>
                {completedSteps}/{totalSteps} stages complete
              </span>
            </div>
            <div style={{ height: '6px', background: 'var(--bg-secondary)', borderRadius: '3px', overflow: 'hidden' }}>
              <div style={{ height: '100%', width: `${strategyProgress}%`, background: 'linear-gradient(90deg, var(--accent-primary), var(--accent-secondary))', borderRadius: '3px', transition: 'width 0.5s ease' }} />
            </div>
          </div>

          {/* collapsible steps list */}
          <div style={{ display: 'flex', flexDirection: 'column', gap: '2rem' }}>
            {[1, 2, 3, 4].map(phaseNum => {
              const phase = PHASE_META[phaseNum];
              const completedCount = phase.steps.filter(sid => strategyData.steps?.[sid]?.status === 'complete').length;
              return (
                <div key={phaseNum} style={{ marginBottom: '0.5rem' }}>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', marginBottom: '1rem', paddingBottom: '0.5rem', borderBottom: `2px solid ${phase.color}30` }}>
                    <div style={{ background: `${phase.color}20`, padding: '0.4rem', borderRadius: '6px', color: phase.color }}>{phase.icon}</div>
                    <h2 style={{ margin: 0, fontSize: '1.1rem', color: '#fff', fontWeight: 'bold' }}>Phase {phaseNum}: {phase.label}</h2>
                    <span style={{ marginLeft: 'auto', fontSize: '0.75rem', color: 'var(--text-muted)' }}>{completedCount}/{phase.steps.length} completed</span>
                  </div>

                  <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
                    {phase.steps.map(stepId => (
                      strategyData.steps?.[stepId] ? (
                        <StepCard 
                          key={stepId}
                          stepId={stepId}
                          stepData={strategyData.steps[stepId]}
                          isOpen={!!openSteps[stepId]}
                          onToggle={() => toggleStep(stepId)}
                        />
                      ) : null
                    ))}
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      )}

      {/* 3. BOARD SLIDES TAB */}
      {activeSection === 'slides' && boardPresentation && (
        <div className="grid-2" style={{ gridTemplateColumns: '7.5fr 2.5fr', gap: '1.5rem' }}>
          
          {/* Slides Deck Visualizer */}
          <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
            <div className="glass-panel" style={{ 
              minHeight: '420px', background: 'linear-gradient(135deg, #090e1a, #0b1931)', border: '2px solid rgba(255,255,255,0.06)',
              borderRadius: '16px', padding: '2rem', display: 'flex', flexDirection: 'column', position: 'relative',
              boxShadow: '0 15px 35px rgba(0,0,0,0.5)', textAlign: 'left', overflow: 'hidden'
            }}>
              {/* Branded accent tag */}
              <div style={{ position: 'absolute', top: '12px', right: '20px', display: 'flex', alignItems: 'center', gap: '6px' }}>
                <span style={{ width: '8px', height: '8px', borderRadius: '50%', background: boardPresentation.primary_color || 'var(--accent-primary)' }}></span>
                <span style={{ fontSize: '0.7rem', color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '1px', fontWeight: 'bold' }}>
                  {boardPresentation.presentation_theme || 'STRATEGY DECISION'}
                </span>
              </div>

              {/* active slide rendering */}
              <div style={{ flex: 1, display: 'flex', flexDirection: 'column', justifyContent: 'center', marginTop: '1rem' }}>
                {(() => {
                  const activeSlide = boardPresentation.slides[currentSlideIndex];
                  if (!activeSlide) return null;
                  const brandColor = boardPresentation.primary_color || 'var(--accent-primary)';
                  return renderActiveSlideContent(activeSlide, brandColor);
                })()}
              </div>

              {/* slide footer */}
              <div style={{ display: 'flex', justifyContent: 'space-between', borderTop: '1px solid rgba(255,255,255,0.06)', paddingTop: '0.75rem', marginTop: '1rem', fontSize: '0.75rem', color: 'var(--text-muted)' }}>
                <span>McKinsey Storytelling Contract</span>
                <span>Page {currentSlideIndex + 1} of {boardPresentation.slides.length}</span>
              </div>
            </div>

            {/* slide navigation buttons */}
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              <button className="btn-secondary" onClick={handlePrevSlide} disabled={currentSlideIndex === 0}>
                <ArrowLeft size={16} /> Previous
              </button>
              <button className="btn-secondary" onClick={handleNextSlide} disabled={currentSlideIndex === boardPresentation.slides.length - 1}>
                Next <ArrowRight size={16} />
              </button>
            </div>
          </div>

          {/* Speaker Notes */}
          <div className="glass-panel" style={{ padding: '1.25rem', display: 'flex', flexDirection: 'column', gap: '1rem', textAlign: 'left' }}>
            <h3 style={{ borderBottom: '1px solid var(--border-glass)', paddingBottom: '0.5rem', color: '#fff', fontSize: '1rem', margin: 0 }}>
              🎙️ Board Presenter Notes
            </h3>
            <p style={{ color: '#cbd5e1', fontSize: '0.85rem', fontStyle: 'italic', margin: 0, lineHeight: '1.5' }}>
              "{boardPresentation.slides[currentSlideIndex]?.speaker_notes || 'No notes compiled for this slide.'}"
            </p>
          </div>
        </div>
      )}

      {/* 4. PROTOTYPE MARKDOWN TAB */}
      {activeSection === 'prototype' && (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem', textAlign: 'left' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <div>
              <h2 style={{ margin: 0, fontSize: '1.25rem', color: '#fff', fontWeight: 'bold' }}>🚀 Detailed MVP Prototype PRD</h2>
              <p style={{ margin: '0.25rem 0 0 0', fontSize: '0.85rem', color: 'var(--text-secondary)' }}>
                Import directly into Lovable, Figma, or Google Stitch to build interactive prototypes.
              </p>
            </div>
            <div style={{ display: 'flex', gap: '0.75rem' }}>
              <button 
                className="btn-primary" 
                onClick={handleDownloadPrototypeMarkdown}
                disabled={!prototypeMarkdown || prototypeLoading}
                style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}
              >
                <Download size={16} /> Download .MD File
              </button>
              <button 
                className="btn-secondary" 
                onClick={() => {
                  navigator.clipboard.writeText(prototypeMarkdown);
                  alert("Prototype Markdown copied to clipboard!");
                }}
                disabled={!prototypeMarkdown || prototypeLoading}
              >
                Copy Markdown
              </button>
            </div>
          </div>

          <div className="glass-panel" style={{ padding: '1.5rem', background: '#0d111d', borderRadius: '12px', border: '1px solid rgba(255,255,255,0.08)' }}>
            {prototypeLoading ? (
              <div style={{ padding: '3rem', textAlign: 'center', color: 'var(--text-muted)' }}>
                <Loader2 size={24} style={{ animation: 'spin 1s linear infinite', marginBottom: '0.5rem' }} />
                <p>Generating detailed PRD Prototype Markdown via AI engine...</p>
              </div>
            ) : (
              <pre style={{ 
                whiteSpace: 'pre-wrap', 
                wordWrap: 'break-word', 
                fontFamily: 'monospace', 
                fontSize: '0.85rem', 
                color: '#e2e8f0',
                lineHeight: '1.6',
                margin: 0,
                maxHeight: '600px',
                overflowY: 'auto'
              }}>
                {prototypeMarkdown || "No prototype markdown available. Please complete Strategy Deep Dive first."}
              </pre>
            )}
          </div>
        </div>
      )}



      {/* Global CSS animations */}
      <style>{`@keyframes spin { from { transform: rotate(0deg); } to { transform: rotate(360deg); } }`}</style>
    </div>
  );
};

export default Dashboard;
