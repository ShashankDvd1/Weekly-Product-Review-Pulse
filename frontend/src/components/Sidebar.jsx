import { useState } from 'react';
import { NavLink } from 'react-router-dom';
import { 
  LayoutDashboard, 
  Users, 
  Award,
  Table,
  BarChart3,
  Smartphone,
  Menu,
  X
} from 'lucide-react';
import './Sidebar.css';

const Sidebar = () => {
  const [isOpen, setIsOpen] = useState(false);

  const navItems = [
    { path: '/', label: 'Overview', icon: <LayoutDashboard size={20} /> },
    { path: '/insights', label: 'Consumer Insights', icon: <Users size={20} /> },
    { path: '/signals', label: 'Signals Database', icon: <Table size={20} /> },
    { path: '/review', label: 'Review Board', icon: <Award size={20} /> },
    { path: '/intent-sense', label: 'Intent Sense MVP', icon: <Smartphone size={20} /> },
  ];

  const toggleSidebar = () => setIsOpen(!isOpen);
  const closeSidebar = () => setIsOpen(false);

  return (
    <>
      {/* Mobile Top Header Bar */}
      <div className="mobile-header-bar glass-panel">
        <div className="mobile-logo-section">
          <div className="logo-icon-sm">
            <BarChart3 size={18} color="var(--accent-primary)" />
          </div>
          <h3 className="brand-name-sm text-gradient">Pulse Intel</h3>
        </div>
        <button className="menu-toggle-btn" onClick={toggleSidebar}>
          {isOpen ? <X size={20} /> : <Menu size={20} />}
        </button>
      </div>

      {/* Backdrop for Mobile */}
      {isOpen && <div className="sidebar-backdrop" onClick={closeSidebar} />}

      <aside className={`sidebar glass-panel ${isOpen ? 'open' : ''}`}>
        <div className="sidebar-header">
          <div className="logo-icon">
            <BarChart3 size={24} color="var(--accent-primary)" />
          </div>
          <h2 className="brand-name text-gradient">Pulse Intel</h2>
          <button className="sidebar-close-btn" onClick={closeSidebar}>
            <X size={20} />
          </button>
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
                  onClick={closeSidebar}
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
    </>
  );
};

export default Sidebar;
