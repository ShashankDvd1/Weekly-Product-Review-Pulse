import { useState, useEffect } from 'react';
import { 
  FileText, 
  Link as LinkIcon, 
  Search, 
  Table, 
  Download, 
  Filter, 
  Database, 
  MessageSquare 
} from 'lucide-react';
import { getBackendUrl } from '../config';

const SignalsHub = () => {
  const [activeTab, setActiveTab] = useState('explorer'); // 'explorer', 'sheets'
  
  // Explorer states
  const [explorerData, setExplorerData] = useState(null);
  const [explorerLoading, setExplorerLoading] = useState(true);

  // Sheets states
  const [signals, setSignals] = useState([]);
  const [themes, setThemes] = useState([]);
  const [barriers, setBarriers] = useState([]);
  const [sheetsLoading, setSheetsLoading] = useState(true);
  const [sheetView, setSheetView] = useState('unified'); // 'play_store', 'app_store', 'reddit', 'unified', 'insights'
  const [searchTerm, setSearchTerm] = useState('');
  const [appFilter, setAppFilter] = useState('all');

  // Load explorer (themes)
  useEffect(() => {
    if (activeTab === 'explorer' && !explorerData) {
      const fetchData = async () => {
        try {
          setExplorerLoading(true);
          const response = await fetch(`${getBackendUrl()}/api/v2/analyze/themes`);
          const result = await response.json();
          setExplorerData(result);
        } catch (err) {
          console.error(err);
        } finally {
          setExplorerLoading(false);
        }
      };
      fetchData();
    }
  }, [activeTab, explorerData]);

  // Load sheet data
  useEffect(() => {
    if (activeTab === 'sheets' && signals.length === 0) {
      const fetchData = async () => {
        try {
          setSheetsLoading(true);
          const sigRes = await fetch(`${getBackendUrl()}/api/v2/signals`);
          const sigData = await sigRes.json();
          setSignals(sigData.signals || []);

          const themeRes = await fetch(`${getBackendUrl()}/api/v2/analyze/themes`);
          const themeData = await themeRes.json();
          setThemes(themeData.themes || []);

          const barrierRes = await fetch(`${getBackendUrl()}/api/v2/analyze/barriers`);
          const barrierData = await barrierRes.json();
          setBarriers(barrierData.barriers || []);
        } catch (err) {
          console.error(err);
        } finally {
          setSheetsLoading(false);
        }
      };
      fetchData();
    }
  }, [activeTab, signals.length]);

  const downloadCSV = () => {
    const dataToExport = getFilteredSheetData();
    if (dataToExport.length === 0) return;

    let headers = [];
    let rows = [];

    if (sheetView === 'insights') {
      headers = ['Type', 'Category', 'Title', 'Confidence', 'Details', 'Apps Affected'];
      rows = dataToExport.map(r => [r.type, r.category, r.title, r.confidence, r.details, r.apps]);
    } else {
      headers = ['Date', 'Source', 'App Name', 'User Name', 'Rating', 'Sentiment Score', 'Categories', 'Content'];
      rows = dataToExport.map(r => [r.date, r.source, r.app_name, r.userName, r.rating, r.sentiment_score, (r.categories || []).join('; '), r.content]);
    }

    const csvContent = "data:text/csv;charset=utf-8," 
      + [headers.join(','), ...rows.map(e => e.map(val => `"${String(val).replace(/"/g, '""')}"`).join(','))].join('\n');
    
    const encodedUri = encodeURI(csvContent);
    const link = document.createElement("a");
    link.setAttribute("href", encodedUri);
    link.setAttribute("download", `pulse_export_${sheetView}_${new Date().toISOString().split('T')[0]}.csv`);
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  const getFilteredSheetData = () => {
    let data = [];
    if (sheetView === 'play_store') {
      data = signals.filter(s => s.source === 'play_store');
    } else if (sheetView === 'app_store') {
      data = signals.filter(s => s.source === 'app_store');
    } else if (sheetView === 'reddit') {
      data = signals.filter(s => s.source === 'reddit');
    } else if (sheetView === 'unified') {
      data = signals;
    } else if (sheetView === 'insights') {
      const themeRows = themes.map(t => ({
        type: 'Theme',
        category: t.category,
        title: t.title,
        confidence: `${Math.round(t.confidence * 100)}%`,
        details: t.summary,
        apps: t.apps_affected.join(', ') || 'N/A'
      }));
      const barrierRows = barriers.map(b => ({
        type: 'Barrier',
        category: b.barrier_type,
        title: b.name,
        confidence: `${Math.round(b.severity_score)}%`,
        details: b.description,
        apps: 'All Quick Commerce'
      }));
      data = [...themeRows, ...barrierRows];
    }

    if (appFilter !== 'all' && sheetView !== 'insights') {
      data = data.filter(s => s.app_name === appFilter);
    }

    if (searchTerm.trim() !== '') {
      const query = searchTerm.toLowerCase();
      data = data.filter(item => {
        if (sheetView === 'insights') {
          return item.title.toLowerCase().includes(query) || 
                 item.category.toLowerCase().includes(query) || 
                 item.details.toLowerCase().includes(query);
        } else {
          return (item.content || '').toLowerCase().includes(query) || 
                 (item.userName || '').toLowerCase().includes(query) ||
                 (item.app_name || '').toLowerCase().includes(query);
        }
      });
    }

    return data;
  };

  const filteredSheetData = getFilteredSheetData();

  return (
    <div>
      <div className="page-header" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <div>
          <h1 className="page-title text-gradient">Signals Database</h1>
          <p className="page-subtitle">Inspect raw quick commerce reviews, Reddit feedback, and derived evidence logs.</p>
        </div>

        {/* Tab selection switcher */}
        <div className="glass-panel" style={{ display: 'flex', padding: '0.25rem', borderRadius: '8px', gap: '0.25rem' }}>
          <button 
            onClick={() => setActiveTab('explorer')}
            style={{
              padding: '0.5rem 1rem', borderRadius: '6px', border: 'none',
              background: activeTab === 'explorer' ? 'var(--accent-primary)' : 'transparent',
              color: activeTab === 'explorer' ? '#fff' : 'var(--text-secondary)',
              cursor: 'pointer', fontWeight: '600', transition: 'all 0.2s ease'
            }}
          >
            Evidence Explorer
          </button>
          <button 
            onClick={() => setActiveTab('sheets')}
            style={{
              padding: '0.5rem 1rem', borderRadius: '6px', border: 'none',
              background: activeTab === 'sheets' ? 'var(--accent-primary)' : 'transparent',
              color: activeTab === 'sheets' ? '#fff' : 'var(--text-secondary)',
              cursor: 'pointer', fontWeight: '600', transition: 'all 0.2s ease'
            }}
          >
            Data Sheets
          </button>
        </div>
      </div>

      {/* EVIDENCE EXPLORER CONTENT */}
      {activeTab === 'explorer' && (
        <div>
          {explorerLoading ? (
            <div className="loader" style={{ margin: '4rem auto', display: 'block' }}></div>
          ) : (
            <div style={{ display: 'flex', flexDirection: 'column', gap: '2rem', textAlign: 'left' }}>
              {explorerData?.themes?.map((theme, idx) => (
                <div key={idx} className="glass-card">
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '1.5rem', paddingBottom: '1.5rem', borderBottom: '1px solid var(--border-glass)' }}>
                    <div>
                      <span className="badge" style={{ background: 'rgba(255,255,255,0.05)', marginBottom: '0.5rem' }}>Theme: {theme.category}</span>
                      <h2 style={{ fontSize: '1.5rem', margin: '0 0 0.5rem 0', color: '#fff' }}>{theme.title}</h2>
                      <p style={{ color: 'var(--text-secondary)', margin: 0 }}>{theme.summary}</p>
                    </div>
                    <div style={{ display: 'flex', gap: '0.5rem' }}>
                      <span className={`badge badge-${theme.sentiment === 'positive' ? 'success' : theme.sentiment === 'negative' ? 'danger' : 'info'}`}>
                        {theme.sentiment}
                      </span>
                      <span className="badge badge-warning">{Math.round(theme.confidence * 100)}% Conf.</span>
                    </div>
                  </div>

                  <div>
                    <h4 style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', color: 'var(--accent-primary)', marginBottom: '1rem' }}>
                      <Search size={16} /> Supporting Verbatim Evidence
                    </h4>
                    <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))', gap: '1rem' }}>
                      {theme.supporting_quotes?.map((quote, qIdx) => (
                        <div key={qIdx} style={{ background: 'var(--bg-secondary)', padding: '1.25rem', borderRadius: '8px', borderLeft: '3px solid var(--accent-primary)' }}>
                          <p style={{ fontStyle: 'italic', fontSize: '0.95rem', color: 'var(--text-primary)', margin: '0 0 1rem 0' }}>"{quote}"</p>
                          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', fontSize: '0.75rem', color: 'var(--text-muted)' }}>
                            <span>Source: App/Play Store</span>
                            <LinkIcon size={12} />
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      )}

      {/* DATA SHEETS CONTENT */}
      {activeTab === 'sheets' && (
        <div>
          {sheetsLoading ? (
            <div className="loader" style={{ margin: '4rem auto', display: 'block' }}></div>
          ) : (
            <div style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem', textAlign: 'left' }}>
              
              {/* Filter Controls Row */}
              <div className="glass-panel" style={{ display: 'flex', justifyContent: 'space-between', gap: '1rem', padding: '1rem', flexWrap: 'wrap', alignItems: 'center' }}>
                
                {/* Views selectors */}
                <div style={{ display: 'flex', gap: '0.25rem', background: 'rgba(0,0,0,0.2)', padding: '0.2rem', borderRadius: '6px' }}>
                  {['unified', 'play_store', 'app_store', 'reddit', 'insights'].map(view => (
                    <button
                      key={view}
                      onClick={() => setSheetView(view)}
                      style={{
                        padding: '0.4rem 0.8rem', borderRadius: '4px', border: 'none', fontSize: '0.8rem',
                        background: sheetView === view ? 'var(--accent-primary)' : 'transparent',
                        color: sheetView === view ? '#fff' : 'var(--text-secondary)',
                        cursor: 'pointer', transition: 'all 0.15s ease'
                      }}
                    >
                      {view.replace('_', ' ').replace(/\b\w/g, c => c.toUpperCase())}
                    </button>
                  ))}
                </div>

                {/* Filters */}
                <div style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
                  {sheetView !== 'insights' && (
                    <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', fontSize: '0.85rem' }}>
                      <span style={{ color: 'var(--text-secondary)' }}>App:</span>
                      <select
                        value={appFilter}
                        onChange={(e) => setAppFilter(e.target.value)}
                        style={{ background: 'var(--bg-secondary)', border: '1px solid var(--border-glass)', borderRadius: '4px', color: '#fff', padding: '0.25rem 0.5rem', fontFamily: 'inherit' }}
                      >
                        <option value="all">All Apps</option>
                        <option value="zepto">Zepto</option>
                        <option value="blinkit">Blinkit</option>
                        <option value="swiggy_instamart">Swiggy Instamart</option>
                      </select>
                    </div>
                  )}

                  <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', position: 'relative' }}>
                    <Search size={14} style={{ position: 'absolute', left: '8px', color: 'var(--text-muted)' }} />
                    <input 
                      type="text"
                      placeholder="Filter database..."
                      value={searchTerm}
                      onChange={(e) => setSearchTerm(e.target.value)}
                      style={{
                        background: 'var(--bg-secondary)', border: '1px solid var(--border-glass)', borderRadius: '4px',
                        color: '#fff', padding: '0.25rem 0.5rem 0.25rem 1.75rem', fontSize: '0.85rem', width: '200px'
                      }}
                    />
                  </div>

                  <button className="btn-secondary" onClick={downloadCSV} style={{ display: 'flex', alignItems: 'center', gap: '0.25rem', fontSize: '0.85rem' }}>
                    <Download size={14} /> Export CSV
                  </button>
                </div>
              </div>

              {/* Table Data Frame */}
              <div className="glass-card" style={{ padding: 0, overflowX: 'auto', maxHeight: '600px', overflowY: 'auto' }}>
                <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: '0.85rem' }}>
                  <thead>
                    <tr style={{ background: 'rgba(255,255,255,0.02)', borderBottom: '1px solid var(--border-glass)', position: 'sticky', top: 0, zIndex: 10 }}>
                      {sheetView === 'insights' ? (
                        <>
                          <th style={{ padding: '0.75rem 1rem', textAlign: 'left', color: 'var(--text-secondary)', fontWeight: '600', width: '12%' }}>Type</th>
                          <th style={{ padding: '0.75rem 1rem', textAlign: 'left', color: 'var(--text-secondary)', fontWeight: '600', width: '15%' }}>Category</th>
                          <th style={{ padding: '0.75rem 1rem', textAlign: 'left', color: 'var(--text-secondary)', fontWeight: '600', width: '20%' }}>Title</th>
                          <th style={{ padding: '0.75rem 1rem', textAlign: 'center', color: 'var(--text-secondary)', fontWeight: '600', width: '10%' }}>Severity/Conf.</th>
                          <th style={{ padding: '0.75rem 1rem', textAlign: 'left', color: 'var(--text-secondary)', fontWeight: '600', width: '28%' }}>Details / Summary</th>
                          <th style={{ padding: '0.75rem 1rem', textAlign: 'left', color: 'var(--text-secondary)', fontWeight: '600', width: '15%' }}>Apps Affected</th>
                        </>
                      ) : (
                        <>
                          <th style={{ padding: '0.75rem 1rem', textAlign: 'left', color: 'var(--text-secondary)', fontWeight: '600', width: '12%' }}>Date</th>
                          <th style={{ padding: '0.75rem 1rem', textAlign: 'left', color: 'var(--text-secondary)', fontWeight: '600', width: '10%' }}>Source</th>
                          <th style={{ padding: '0.75rem 1rem', textAlign: 'left', color: 'var(--text-secondary)', fontWeight: '600', width: '12%' }}>App Name</th>
                          <th style={{ padding: '0.75rem 1rem', textAlign: 'left', color: 'var(--text-secondary)', fontWeight: '600', width: '15%' }}>User</th>
                          <th style={{ padding: '0.75rem 1rem', textAlign: 'center', color: 'var(--text-secondary)', fontWeight: '600', width: '8%' }}>Rating</th>
                          <th style={{ padding: '0.75rem 1rem', textAlign: 'center', color: 'var(--text-secondary)', fontWeight: '600', width: '10%' }}>Sentiment</th>
                          <th style={{ padding: '0.75rem 1rem', textAlign: 'left', color: 'var(--text-secondary)', fontWeight: '600', width: '15%' }}>Categories</th>
                          <th style={{ padding: '0.75rem 1rem', textAlign: 'left', color: 'var(--text-secondary)', fontWeight: '600', width: '28%' }}>Review Content / Discussion</th>
                        </>
                      )}
                    </tr>
                  </thead>
                  <tbody>
                    {filteredSheetData.length === 0 ? (
                      <tr>
                        <td colSpan={sheetView === 'insights' ? 6 : 8} style={{ padding: '3rem', textAlign: 'center', color: 'var(--text-muted)' }}>
                          No matching entries found in this spreadsheet view. Run the analysis or adjust filters.
                        </td>
                      </tr>
                    ) : (
                      filteredSheetData.map((row, idx) => (
                        <tr 
                          key={idx} 
                          style={{ 
                            borderBottom: '1px solid rgba(255,255,255,0.03)', 
                            background: idx % 2 === 0 ? 'transparent' : 'rgba(255,255,255,0.01)',
                          }}
                        >
                          {sheetView === 'insights' ? (
                            <>
                              <td style={{ padding: '1rem' }}>
                                <span className={`badge badge-${row.type === 'Theme' ? 'info' : 'warning'}`}>{row.type}</span>
                              </td>
                              <td style={{ padding: '1rem', fontWeight: '500' }}>{row.category}</td>
                              <td style={{ padding: '1rem', color: '#fff', fontWeight: '600' }}>{row.title}</td>
                              <td style={{ padding: '1rem', textAlign: 'center' }}>
                                <span className="badge badge-success" style={{ background: 'rgba(16, 185, 129, 0.15)' }}>{row.confidence}</span>
                              </td>
                              <td style={{ padding: '1rem', color: 'var(--text-secondary)', fontSize: '0.85rem', lineHeight: '1.4' }}>{row.details}</td>
                              <td style={{ padding: '1rem', color: 'var(--text-muted)', fontSize: '0.85rem' }}>{row.apps}</td>
                            </>
                          ) : (
                            <>
                              <td style={{ padding: '1rem', color: 'var(--text-secondary)' }}>
                                {row.date ? new Date(row.date).toISOString().split('T')[0] : 'N/A'}
                              </td>
                              <td style={{ padding: '1rem' }}>
                                <span className={`badge badge-${row.source === 'play_store' ? 'success' : row.source === 'app_store' ? 'info' : 'warning'}`}>
                                  {row.source.replace('_', ' ')}
                                </span>
                              </td>
                              <td style={{ padding: '1rem', fontWeight: '500' }}>{row.app_name || 'N/A'}</td>
                              <td style={{ padding: '1rem', color: 'var(--text-secondary)' }}>{row.userName || 'Unknown'}</td>
                              <td style={{ padding: '1rem', textAlign: 'center', color: row.rating !== null && row.rating <= 2 ? 'var(--danger)' : row.rating !== null && row.rating >= 4 ? 'var(--success)' : '#fff' }}>
                                {row.rating !== null ? `${row.rating} ★` : 'N/A'}
                              </td>
                              <td style={{ padding: '1rem', textAlign: 'center' }}>
                                <span style={{ 
                                  color: row.sentiment_score < 0 ? 'var(--danger)' : row.sentiment_score > 0 ? 'var(--success)' : 'var(--info)'
                                }}>
                                  {row.sentiment_score !== undefined ? row.sentiment_score.toFixed(2) : '0.00'}
                                </span>
                              </td>
                              <td style={{ padding: '1rem' }}>
                                <div style={{ display: 'flex', flexWrap: 'wrap', gap: '0.2rem' }}>
                                  {(row.categories || []).map(cat => (
                                    <span key={cat} className="badge" style={{ background: 'rgba(255,255,255,0.05)', fontSize: '0.75rem', color: 'var(--text-muted)' }}>
                                      {cat}
                                    </span>
                                  ))}
                                </div>
                              </td>
                              <td style={{ padding: '1rem', color: 'var(--text-primary)', fontSize: '0.85rem', lineHeight: '1.4' }}>
                                {row.content}
                              </td>
                            </>
                          )}
                        </tr>
                      ))
                    )}
                  </tbody>
                </table>
              </div>
              <div style={{ marginTop: '0.5rem', display: 'flex', justifyContent: 'space-between', color: 'var(--text-muted)', fontSize: '0.85rem' }}>
                <span>Showing {filteredSheetData.length} entries</span>
                {sheetView !== 'insights' && <span>Sanitized & Semantic Deduplication Applied</span>}
              </div>

            </div>
          )}
        </div>
      )}
    </div>
  );
};

export default SignalsHub;
