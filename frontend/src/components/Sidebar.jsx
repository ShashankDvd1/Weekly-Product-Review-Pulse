import React from 'react';
import { NavLink } from 'react-router-dom';
import { 
  LayoutDashboard, 
  Search, 
  Users, 
  Lightbulb, 
  Microscope, 
  FileText,
  BarChart3,
  Terminal,
  Table,
  Presentation,
  Award,
  Compass,
  Briefcase
} from 'lucide-react';
import './Sidebar.css';

const Sidebar = () => {
  const navItems = [
    { path: '/', label: 'Overview', icon: <LayoutDashboard size={20} /> },
    { path: '/control-center', label: 'Control Center', icon: <Terminal size={20} /> },
    { path: '/category-discovery', label: 'Category Discovery', icon: <Search size={20} /> },
    { path: '/personas', label: 'User Personas', icon: <Users size={20} /> },
    { path: '/opportunities', label: 'Growth Opportunities', icon: <Lightbulb size={20} /> },
    { path: '/research-copilot', label: 'Research Copilot', icon: <Microscope size={20} /> },
    { path: '/evidence', label: 'Evidence Explorer', icon: <FileText size={20} /> },
    { path: '/sheets', label: 'Data Sheets', icon: <Table size={20} /> },
    { path: '/deck', label: 'Executive Deck', icon: <Presentation size={20} /> },
    { path: '/review-board', label: 'Review Board', icon: <Award size={20} /> },
    { path: '/viva-defense', label: 'Viva Defense', icon: <Compass size={20} /> },
    { path: '/mvp-case', label: 'MVP Case Study', icon: <Briefcase size={20} /> },
  ];

  return (
    <aside className="sidebar glass-panel">
      <div className="sidebar-header">
        <div className="logo-icon">
          <BarChart3 size={24} color="var(--accent-primary)" />
        </div>
        <h2 className="brand-name text-gradient">Pulse Intel</h2>
      </div>

      <nav className="sidebar-nav">
        <p className="nav-section-title">INTELLIGENCE PLATFORM</p>
        <ul className="nav-list">
          {navItems.map((item) => (
            <li key={item.path} className="nav-item">
              <NavLink 
                to={item.path} 
                className={({ isActive }) => `nav-link ${isActive ? 'active' : ''}`}
                end={item.path === '/'}
              >
                <span className="nav-icon">{item.icon}</span>
                <span className="nav-label">{item.label}</span>
              </NavLink>
            </li>
          ))}
        </ul>
      </nav>

      <div className="sidebar-footer">
        <div className="status-indicator">
          <div className="status-dot"></div>
          <span>Platform Online</span>
        </div>
      </div>
    </aside>
  );
};

export default Sidebar;
