import { NavLink } from 'react-router-dom';
import { 
  LayoutDashboard, 
  Users, 
  Award,
  Table,
  BarChart3,
  Smartphone
} from 'lucide-react';
import './Sidebar.css';

const Sidebar = () => {
  const navItems = [
    { path: '/', label: 'Overview', icon: <LayoutDashboard size={20} /> },
    { path: '/insights', label: 'Consumer Insights', icon: <Users size={20} /> },
    { path: '/signals', label: 'Signals Database', icon: <Table size={20} /> },
    { path: '/review', label: 'Review Board', icon: <Award size={20} /> },
    { path: '/mypicks', label: 'Myntra My Picks', icon: <Smartphone size={20} /> },
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
