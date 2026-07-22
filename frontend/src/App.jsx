import { useState, useEffect } from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';

// Layout
import Layout from './components/Layout';

// Pages
import Dashboard from './pages/Dashboard';
import InsightsHub from './pages/InsightsHub';
import StrategyHub from './pages/StrategyHub';
import SignalsHub from './pages/SignalsHub';
import ReviewHub from './pages/ReviewHub';

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<Layout />}>
          <Route index element={<Dashboard />} />
          <Route path="insights" element={<InsightsHub />} />
          <Route path="strategy" element={<StrategyHub />} />
          <Route path="signals" element={<SignalsHub />} />
          <Route path="review" element={<ReviewHub />} />
          <Route path="*" element={<Navigate to="/" replace />} />
        </Route>
      </Routes>
    </BrowserRouter>
  );
}

export default App;
