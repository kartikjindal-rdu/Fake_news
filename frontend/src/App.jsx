import React, { useState } from 'react';
import { ThemeProvider } from './context/ThemeContext';
import { AuthProvider } from './context/AuthContext';
import { Navbar } from './components/Navbar';
import { Footer } from './components/Footer';

// Pages
import { LandingPage } from './pages/LandingPage';
import { ScannerPage } from './pages/ScannerPage';
import { HistoryPage } from './pages/HistoryPage';
import { DashboardPage } from './pages/DashboardPage';
import { ModelStudioPage } from './pages/ModelStudioPage';
import { DomainCheckerPage } from './pages/DomainCheckerPage';
import { ClaimIntelligencePage } from './pages/ClaimIntelligencePage';
import { AdminPage } from './pages/AdminPage';

export function App() {
  const [activePage, setActivePage] = useState('landing');
  const [scannerPayload, setScannerPayload] = useState(null);

  const handleAnalyzeArticleInScanner = (payload) => {
    setScannerPayload(payload);
    setActivePage('scanner');
  };

  const renderActivePage = () => {
    switch (activePage) {
      case 'landing':
        return (
          <LandingPage
            setActivePage={setActivePage}
            onAnalyzeArticle={handleAnalyzeArticleInScanner}
          />
        );
      case 'scanner':
        return (
          <ScannerPage
            initialPayload={scannerPayload}
            onClearInitialPayload={() => setScannerPayload(null)}
          />
        );
      case 'claims':
        return <ClaimIntelligencePage />;
      case 'domain':
        return <DomainCheckerPage />;
      case 'history':
        return <HistoryPage />;
      case 'dashboard':
        return <DashboardPage />;
      case 'model':
        return <ModelStudioPage />;
      case 'admin':
        return <AdminPage />;
      default:
        return (
          <LandingPage
            setActivePage={setActivePage}
            onAnalyzeArticle={handleAnalyzeArticleInScanner}
          />
        );
    }
  };

  return (
    <ThemeProvider>
      <AuthProvider>
        <div className="min-h-screen flex flex-col bg-[#0b0f19] text-slate-100 radial-bg">
          <Navbar activePage={activePage} setActivePage={setActivePage} />
          
          <main className="flex-1">
            {renderActivePage()}
          </main>

          <Footer setActivePage={setActivePage} />
        </div>
      </AuthProvider>
    </ThemeProvider>
  );
}

export default App;
