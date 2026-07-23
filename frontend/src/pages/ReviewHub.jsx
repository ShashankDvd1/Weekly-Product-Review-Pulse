import { useState } from 'react';
import MVPWorkspace from './MVPWorkspace';
import VivaDefense from './VivaDefense';

const ReviewHub = () => {
  const [activeTab, setActiveTab] = useState('evaluation'); // 'evaluation', 'defense'

  return (
    <div>
      <div className="page-header" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <div>
          <h1 className="page-title text-gradient">Review Board Hub</h1>
          <p className="page-subtitle">Evaluate your strategy against Google PM, McKinsey, and VC standards, and defend it in a Viva session.</p>
        </div>

        {/* Tab Selection switcher */}
        <div className="glass-panel" style={{ display: 'flex', padding: '0.25rem', borderRadius: '8px', gap: '0.25rem' }}>
          <button 
            onClick={() => setActiveTab('evaluation')}
            style={{
              padding: '0.5rem 1rem', borderRadius: '6px', border: 'none',
              background: activeTab === 'evaluation' ? 'var(--accent-primary)' : 'transparent',
              color: activeTab === 'evaluation' ? '#fff' : 'var(--text-secondary)',
              cursor: 'pointer', fontWeight: '600', transition: 'all 0.2s ease'
            }}
          >
            MVP Workspace
          </button>
          <button 
            onClick={() => setActiveTab('defense')}
            style={{
              padding: '0.5rem 1rem', borderRadius: '6px', border: 'none',
              background: activeTab === 'defense' ? 'var(--accent-primary)' : 'transparent',
              color: activeTab === 'defense' ? '#fff' : 'var(--text-secondary)',
              cursor: 'pointer', fontWeight: '600', transition: 'all 0.2s ease'
            }}
          >
            Viva Defense Q&A
          </button>
        </div>
      </div>

      {activeTab === 'evaluation' ? <MVPWorkspace /> : <VivaDefense />}
    </div>
  );
};

export default ReviewHub;
