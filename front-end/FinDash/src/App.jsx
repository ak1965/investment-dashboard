// src/App.jsx
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom'


import Navigation from './components/Navigation'
import InvestmentAdder from './components/InvestmentAdder'
import ReportGenerator from './components/ReportGenerator'
import InvestmentDashboard from './components/InvestmentDashboard';
import StockDataFetcher from './components/StockDataFetcher';
// import CurryHouses from './pages/CurryHouses'
// import Dashboard from './pages/Dashboard'

export default function App() {
  return (
    <Router>      
          <Routes>
            <Route path="/" element={<Navigation />} />             
            <Route path="/investment" element={<InvestmentAdder />} /> 
            <Route path="/reports" element={<ReportGenerator />} />   
            <Route path="/investment-chart" element={<InvestmentDashboard />} />  
            <Route path="/stock-performance" element={<StockDataFetcher />} />  
          </Routes>       
    </Router>
  )
}