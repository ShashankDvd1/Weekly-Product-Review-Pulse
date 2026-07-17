import React, { useState, useEffect } from 'react';
import { Table, Download, Search, Filter, Database, MessageSquare } from 'lucide-react';
import { getBackendUrl } from '../config';

const DataSheets = () => {
  const [signals, setSignals] = useState([]);
  const [themes, setThemes] = useState([]);
  const [barriers, setBarriers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState('unified'); // 'play_store', 'app_store', 'reddit', 'unified', 'insights'
  const [searchTerm, setSearchTerm] = useState('');
  const [appFilter, setAppFilter] = useState('all');

  useEffect(() => {
    const fetchData = async () => {
      try {
        setLoading(true);
        // Fetch raw signals
        const sigRes = await fetch(`${getBackendUrl()}/api/v2/signals`);
        const sigData = await sigRes.json();
        setSignals(sigData.signals || []);

        // Fetch themes and barriers
        const themeRes = await fetch(`${getBackendUrl()}/api/v2/analyze/themes`);
        const themeData = await themeRes.json();
        setThemes(themeData.themes || []);

        const barrierRes = await fetch(`${getBackendUrl()}/api/v2/analyze/barriers`);
        const barrierData = await barrierRes.json();
        setBarriers(barrierData.barriers || []);
      } catch (err) {
        console.error('Error fetching data for sheets', err);
      } finally {
        setLoading(false);
      }
    };
    fetchData();
  }, []);

  const getFilteredData = () => {
    let data = [];
    if (activeTab === 'play_store') {
      data = signals.filter(s => s.source === 'play_store');
    } else if (activeTab === 'app_store') {
      data = signals.filter(s => s.source === 'app_store');
    } else if (activeTab === 'reddit') {
      data = signals.filter(s => s.source === 'reddit');
    } else if (activeTab === 'unified') {
      data = signals;
    } else if (activeTab === 'insights') {
      // Combine themes and barriers in a unified format
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
        category: b.category,
        title: `${b.barrier_type} barrier`,
        confidence: `${Math.round(b.confidence * 100)}%`,
        details: b.description,
        apps: b.apps_affected.join(', ') || 'N/A'
      }));
      return [...themeRows, ...barrierRows].filter(row => 
        row.title.toLowerCase().includes(searchTerm.toLowerCase()) ||
        row.details.toLowerCase().includes(searchTerm.toLowerCase())
      );
    }

    // Apply App Filter
    if (appFilter !== 'all') {
      data = data.filter(s => s.app_name?.toLowerCase() === appFilter.toLowerCase());
    }

    // Apply Search Term
    if (searchTerm.trim() !== '') {
      data = data.filter(s => 
        s.content?.toLowerCase().includes(searchTerm.toLowerCase()) ||
        s.userName?.toLowerCase().includes(searchTerm.toLowerCase())
      );
    }

    return data;
  };

  const downloadCSV = () => {
    const data = getFilteredData();
    if (data.length === 0) return;

    let headers = [];
    let rows = [];

    if (activeTab === 'insights') {
      headers = ['Type', 'Category', 'Title/Type', 'Confidence', 'Details', 'Apps Affected'];
      rows = data.map(r => [r.type, r.category, r.title, r.confidence, r.details, r.apps]);
    } else {
      headers = ['Date', 'Source', 'App Name', 'Author/User', 'Rating', 'Sentiment Score', 'Categories', 'Content'];
      rows = data.map(s => [
        s.date ? new Date(s.date).toISOString().split('T')[0] : 'N/A',
        s.source,
        s.app_name || 'N/A',
        s.userName || 'N/A',
        s.rating !== null ? s.rating : 'N/A',
        s.sentiment_score !== undefined ? s.sentiment_score.toFixed(2) : 'N/A',
        (s.categories || []).join('; '),
        s.content.replace(/"/g, '""')
      ]);
    }

    const csvContent = "data:text/csv;charset=utf-8," 
      + [headers.join(','), ...rows.map(e => e.map(val => `"${val}"`).join(','))].join('\n');
    
    const encodedUri = encodeURI(csvContent);
    const link = document.createElement("a");
    link.setAttribute("href", encodedUri);
    link.setAttribute("download", `${activeTab}_sheet_export.csv`);
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  const filteredData = getFilteredData();
  const uniqueApps = Array.from(new Set(signals.map(s => s.app_name).filter(Boolean)));

  if (loading) return (
    <div className="flex-center" style={{ height: '80vh', display: 'flex', justifyContent: 'center', alignItems: 'center', flexDirection: 'column', gap: '1rem' }}>
      <div className="loader" style={{ width: '40px', height: '40px', borderColor: 'rgba(99, 102, 241, 0.3)', borderTopColor: 'var(--accent-primary)' }}></div>
      <p style={{ color: 'var(--text-secondary)' }}>Loading Sheets Engine...</p>
    </div>
  );

  return (
    <div>
      <div className="page-header" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: '1rem' }}>
        <div>
          <h1 className="page-title text-gradient">Data Sheets</h1>
          <p className="page-subtitle">Interact with tabular views of reviews, Reddit logs, and analysis insights.</p>
        </div>
        <button className="btn-primary" onClick={downloadCSV} disabled={filteredData.length === 0}>
          <Download size={18} /> Export CSV
        </button>
      </div>

      {/* Spreadsheet Tabs Selector */}
      <div style={{ display: 'flex', borderBottom: '1px solid var(--border-glass)', marginBottom: '1.5rem', overflowX: 'auto', gap: '0.5rem' }}>
        {[
          { id: 'unified', label: 'Unified Dataset', icon: <Database size={16} /> },
          { id: 'play_store', label: 'Play Store Sheet', icon: <Table size={16} /> },
          { id: 'app_store', label: 'App Store Sheet', icon: <Table size={16} /> },
          { id: 'reddit', label: 'Reddit Logs', icon: <MessageSquare size={16} /> },
          { id: 'insights', label: 'AI Insights Sheet', icon: <Table size={16} /> },
        ].map(tab => (
          <button
            key={tab.id}
            onClick={() => { setActiveTab(tab.id); setSearchTerm(''); }}
            style={{
              display: 'flex',
              alignItems: 'center',
              gap: '0.5rem',
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
            {tab.icon}
            {tab.label}
          </button>
        ))}
      </div>

      {/* Filter and Search Bar */}
      <div style={{ display: 'flex', gap: '1rem', marginBottom: '1.5rem', flexWrap: 'wrap' }}>
        <div style={{ flex: 1, minWidth: '250px', position: 'relative' }}>
          <Search size={18} style={{ position: 'absolute', left: '12px', top: '50%', transform: 'translateY(-50%)', color: 'var(--text-muted)' }} />
          <input
            type="text"
            placeholder={activeTab === 'insights' ? "Search themes, categories..." : "Search review content, authors..."}
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            style={{
              width: '100%',
              padding: '0.6rem 1rem 0.6rem 2.5rem',
              background: 'var(--bg-secondary)',
              border: '1px solid var(--border-glass)',
              borderRadius: '6px',
              color: '#fff',
              outline: 'none'
            }}
          />
        </div>

        {activeTab !== 'insights' && (
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
            <Filter size={16} style={{ color: 'var(--text-secondary)' }} />
            <select
              value={appFilter}
              onChange={(e) => setAppFilter(e.target.value)}
              style={{
                background: 'var(--bg-secondary)',
                border: '1px solid var(--border-glass)',
                borderRadius: '6px',
                color: '#fff',
                padding: '0.6rem 1rem',
                cursor: 'pointer',
                outline: 'none'
              }}
            >
              <option value="all">All Apps</option>
              {uniqueApps.map(app => (
                <option key={app} value={app}>{app}</option>
              ))}
            </select>
          </div>
        )}
      </div>

      {/* Spreadsheet Table Container */}
      <div className="glass-card" style={{ padding: 0, overflowX: 'auto', maxHeight: '550px', border: '1px solid var(--border-glass)' }}>
        <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: '0.9rem', color: '#fff', minWidth: '800px' }}>
          <thead>
            <tr style={{ background: 'rgba(255,255,255,0.03)', borderBottom: '1px solid var(--border-glass)' }}>
              {activeTab === 'insights' ? (
                <>
                  <th style={{ padding: '0.75rem 1rem', textAlign: 'left', color: 'var(--text-secondary)', fontWeight: '600', width: '10%' }}>Type</th>
                  <th style={{ padding: '0.75rem 1rem', textAlign: 'left', color: 'var(--text-secondary)', fontWeight: '600', width: '15%' }}>Category</th>
                  <th style={{ padding: '0.75rem 1rem', textAlign: 'left', color: 'var(--text-secondary)', fontWeight: '600', width: '25%' }}>Title / Barrier Type</th>
                  <th style={{ padding: '0.75rem 1rem', textAlign: 'left', color: 'var(--text-secondary)', fontWeight: '600', width: '10%' }}>Confidence</th>
                  <th style={{ padding: '0.75rem 1rem', textAlign: 'left', color: 'var(--text-secondary)', fontWeight: '600', width: '30%' }}>Description</th>
                  <th style={{ padding: '0.75rem 1rem', textAlign: 'left', color: 'var(--text-secondary)', fontWeight: '600', width: '10%' }}>Apps</th>
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
            {filteredData.length === 0 ? (
              <tr>
                <td colSpan={activeTab === 'insights' ? 6 : 8} style={{ padding: '3rem', textAlign: 'center', color: 'var(--text-muted)' }}>
                  No matching entries found in this spreadsheet view. Run the analysis or adjust filters.
                </td>
              </tr>
            ) : (
              filteredData.map((row, idx) => (
                <tr 
                  key={idx} 
                  style={{ 
                    borderBottom: '1px solid rgba(255,255,255,0.03)', 
                    background: idx % 2 === 0 ? 'transparent' : 'rgba(255,255,255,0.01)',
                  }}
                >
                  {activeTab === 'insights' ? (
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
      <div style={{ marginTop: '1rem', display: 'flex', justifyContent: 'space-between', color: 'var(--text-muted)', fontSize: '0.85rem' }}>
        <span>Showing {filteredData.length} entries</span>
        {activeTab !== 'insights' && <span>PII Sanitized & Semantic Deduplication Applied</span>}
      </div>
    </div>
  );
};

export default DataSheets;
