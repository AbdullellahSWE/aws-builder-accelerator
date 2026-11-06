import { useState } from 'react';
import { Authenticator } from '@aws-amplify/ui-react';
import '@aws-amplify/ui-react/styles.css';
import './config'; // Ensures Amplify is configured before rendering
import { Navbar } from './components/Navbar';
import { EmployeeList } from './components/EmployeeList';
import { HrRequests } from './components/HrRequests';
import { AgentChat } from './components/AgentChat';
import './App.css';

export default function App() {
  const [activeTab, setActiveTab] = useState<'directory' | 'requests' | 'agent'>('directory');

  return (
    <Authenticator hideSignUp={true}>
      {({ signOut, user }) => {
        const userEmail =
          user?.signInDetails?.loginId ||
          (user as any)?.username ||
          'HR Admin';

        return (
          <div className="app-container">
            <Navbar
              activeTab={activeTab}
              setActiveTab={setActiveTab}
              userEmail={userEmail}
              signOut={signOut}
            />

            <main className="main-content">
              {activeTab === 'directory' && <EmployeeList />}
              {activeTab === 'requests' && <HrRequests />}
              {activeTab === 'agent' && <AgentChat />}
            </main>

            <footer className="footer-bar">
              <p>
                HR Leave Portal • AWS Builder Accelerator • Connected to API Gateway & Bedrock AgentCore
              </p>
            </footer>
          </div>
        );
      }}
    </Authenticator>
  );
}
