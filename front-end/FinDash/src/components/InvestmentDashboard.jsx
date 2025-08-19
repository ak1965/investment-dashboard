import React, { useState, useEffect } from 'react';
import InvestmentChart from './InvestmentChart';
import './InvestmentChart.css';
import {Link} from 'react-router-dom';

const InvestmentDashboard = () => {
  const [companies, setCompanies] = useState([]);
  const [selectedCompany, setSelectedCompany] = useState('');
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    fetchCompanies();
  }, []);

  const fetchCompanies = async () => {
    setLoading(true);
    try {
      // Fetch list of all companies from your investments
      const response = await fetch('http://localhost:5000/api/companies');
      
      if (response.ok) {
        const result = await response.json();
        if (result.success) {
          setCompanies(result.companies);
        }
      }
    } catch (error) {
      console.error('Error fetching companies:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleCompanySelect = (event) => {
    setSelectedCompany(event.target.value);
  };

  return (
    <div className="investment-dashboard">
      <div className="dashboard-header">
        <Link to='/'>Home</Link>
        <h2>Investment Valuation Tracker</h2>
        <p>Select a company to view its valuation history over time</p>
      </div>

      <div className="company-selector">
        <label htmlFor="company-select">Select Company:</label>
        <select 
          id="company-select"
          value={selectedCompany} 
          onChange={handleCompanySelect}
          disabled={loading}
          className="company-dropdown"
        >
          <option value="">Choose a company...</option>
          {companies.map((company, index) => (
            <option key={index} value={company}>
              {company}
            </option>
          ))}
        </select>
        <button>Generate PDF</button>
      </div>

      <InvestmentChart companyName={selectedCompany} />
    </div>
  );
};

export default InvestmentDashboard;