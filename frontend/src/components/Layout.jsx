import { Outlet } from 'react-router-dom';
import Sidebar from './Sidebar';
import './Layout.css';

const Layout = () => {
  return (
    <div className="app-container">
      {/* Background ambient effects */}
      <div className="ambient-glow"></div>
      <div className="ambient-glow-2"></div>
      
      <Sidebar />
      
      <main className="main-content">
        <div className="content-wrapper">
          <Outlet />
        </div>
      </main>
    </div>
  );
};

export default Layout;
