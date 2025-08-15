// src/App.jsx
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom'


import Navigation from './components/Navigation'
import InvestmentAdder from './components/InvestmentAdder'
// import CurryHouses from './pages/CurryHouses'
// import Dashboard from './pages/Dashboard'

export default function App() {
  return (
    <Router>      
          <Routes>
            <Route path="/" element={<Navigation />} />
             
            <Route path="/investment" element={<InvestmentAdder />} />     
          </Routes>       
    </Router>
  )
}