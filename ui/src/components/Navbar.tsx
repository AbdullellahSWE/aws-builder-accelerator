import React from 'react';

interface NavbarProps {
  activeTab: 'directory' | 'requests' | 'agent';
  setActiveTab: (tab: 'directory' | 'requests' | 'agent') => void;
  userEmail?: string;
  signOut?: () => void;
}

export const Navbar: React.FC<NavbarProps> = ({
  activeTab,
  setActiveTab,
  userEmail,
  signOut,
}) => {
  return (
    <header className="navbar-container">
      <div className="navbar-content">
        <div className="navbar-brand">
          <div className="brand-icon">HR</div>
          <div>
            <h1 className="brand-title">Leave Portal</h1>
            <span className="brand-subtitle">Employee & Leave Operations</span>
          </div>
        </div>

        <nav className="navbar-nav">
          <button
            type="button"
            className={`nav-tab ${activeTab === 'directory' ? 'active' : ''}`}
            onClick={() => setActiveTab('directory')}
          >
            👥 Directory
          </button>
          <button
            type="button"
            className={`nav-tab ${activeTab === 'requests' ? 'active' : ''}`}
            onClick={() => setActiveTab('requests')}
          >
            📨 HR Requests
          </button>
          <button
            type="button"
            className={`nav-tab agent-tab ${activeTab === 'agent' ? 'active' : ''}`}
            onClick={() => setActiveTab('agent')}
          >
            ✨ AI Assistant
          </button>
        </nav>

        <div className="navbar-user">
          {userEmail && <span className="user-badge">{userEmail}</span>}
          {signOut && (
            <button type="button" className="btn-secondary btn-sm" onClick={signOut}>
              Sign Out
            </button>
          )}
        </div>
      </div>
    </header>
  );
};

