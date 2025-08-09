// src/App.jsx
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom'
import Home from './pages/Home'
import About from './pages/About'
import FormEnter from './pages/FormEnter'
import RestaurantDeleter from './components/RestaurantDeleter'
import ViewRestaurants from './components/RestaurantView'
import Navigation from './components/Navigation'
import InvestmentAdder from './components/InvestmentAdder'
// import CurryHouses from './pages/CurryHouses'
// import Dashboard from './pages/Dashboard'

export default function App() {
  return (
    <Router>      
          <Routes>
            <Route path="/" element={<Navigation />} />
            <Route path="/about" element={<About />} /> 
            <Route path="/form" element={<FormEnter/>} /> 
            <Route path="/delete" element={<RestaurantDeleter />} />  
            <Route path="/view" element={<ViewRestaurants />} />  
            <Route path="/investment" element={<InvestmentAdder />} />     
          </Routes>       
    </Router>
  )
}