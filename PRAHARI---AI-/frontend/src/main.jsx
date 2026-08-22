import React from 'react';
import ReactDOM from 'react-dom/client';
import { BrowserRouter, Routes, Route } from 'react-router-dom';
import Layout from './components/Layout';
import Dashboard from './pages/Dashboard';
import Scam from './pages/Scam';
import Currency from './pages/Currency';
import Fraud from './pages/Fraud';
import Geo from './pages/Geo';
import Shield from './pages/Shield';
import './index.css';
import 'leaflet/dist/leaflet.css';

ReactDOM.createRoot(document.getElementById('root')).render(
  <React.StrictMode>
    <BrowserRouter>
      <Layout>
        <Routes>
          <Route path="/" element={<Dashboard />} />
          <Route path="/scam" element={<Scam />} />
          <Route path="/currency" element={<Currency />} />
          <Route path="/fraud" element={<Fraud />} />
          <Route path="/geo" element={<Geo />} />
          <Route path="/shield" element={<Shield />} />
        </Routes>
      </Layout>
    </BrowserRouter>
  </React.StrictMode>
);
