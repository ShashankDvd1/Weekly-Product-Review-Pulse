import React from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';

// Layout
import Layout from './components/Layout';

// Pages
import Dashboard from './pages/Dashboard';
import ControlCenter from './pages/ControlCenter';
import CategoryDiscovery from './pages/CategoryDiscovery';
import Personas from './pages/Personas';
import Opportunities from './pages/Opportunities';
import ResearchCopilot from './pages/ResearchCopilot';
import EvidenceExplorer from './pages/EvidenceExplorer';
import DataSheets from './pages/DataSheets';
import ExecutiveDeck from './pages/ExecutiveDeck';
import ReviewBoard from './pages/ReviewBoard';
import VivaDefense from './pages/VivaDefense';
import MvpCaseStudy from './pages/MvpCaseStudy';
import StrategyDeepDive from './pages/StrategyDeepDive';

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<Layout />}>
          <Route index element={<Dashboard />} />
          <Route path="control-center" element={<ControlCenter />} />
          <Route path="category-discovery" element={<CategoryDiscovery />} />
          <Route path="personas" element={<Personas />} />
          <Route path="opportunities" element={<Opportunities />} />
          <Route path="research-copilot" element={<ResearchCopilot />} />
          <Route path="evidence" element={<EvidenceExplorer />} />
          <Route path="sheets" element={<DataSheets />} />
          <Route path="deck" element={<ExecutiveDeck />} />
          <Route path="review-board" element={<ReviewBoard />} />
          <Route path="viva-defense" element={<VivaDefense />} />
          <Route path="mvp-case" element={<MvpCaseStudy />} />
          <Route path="strategy-deep-dive" element={<StrategyDeepDive />} />
          <Route path="*" element={<Navigate to="/" replace />} />
        </Route>
      </Routes>
    </BrowserRouter>
  );
}

export default App;
