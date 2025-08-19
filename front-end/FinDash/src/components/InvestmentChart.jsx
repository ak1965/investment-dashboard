import React, { useState, useEffect } from 'react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';
import './InvestmentChart.css'


const InvestmentChart = ({ companyName }) => {
  const [chartData, setChartData] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  useEffect(() => {
    if (companyName) {
      fetchInvestmentHistory();
    }
  }, [companyName]);

  const fetchInvestmentHistory = async () => {
    setLoading(true);
    setError(null);
    
    try {
      const response = await fetch(`http://localhost:5000/api/investment-history/${encodeURIComponent(companyName)}`);
      
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      
      const result = await response.json();
      
      if (result.success) {
        setChartData(result.data);
      } else {
        setError(result.error || 'Failed to fetch data');
      }
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const formatCurrency = (value) => {
    return new Intl.NumberFormat('en-GB', {
      style: 'currency',
      currency: 'GBP',
      minimumFractionDigits: 0,
      maximumFractionDigits: 0
    }).format(value);
  };

  const formatDate = (dateString) => {
    const date = new Date(dateString);
    return date.toLocaleDateString('en-GB', {
      day: '2-digit',
      month: 'short',
      year: 'numeric'
    });
  };

  if (loading) {
    return (
      <div className="chart-container">
        <div className="loading">Loading chart data...</div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="chart-container">
        <div className="error">Error: {error}</div>
      </div>
    );
  }

  if (!companyName) {
    return (
      <div className="chart-container">
        <div className="no-company">Select a company to view its valuation history</div>
      </div>
    );
  }

  if (chartData.length === 0) {
    return (
      <div className="chart-container">
        <div className="no-data">No valuation data found for {companyName}</div>
      </div>
    );
  }

  return (
    <div className="chart-container">
      <h3 className="chart-title">
        {companyName} - Valuation History
      </h3>
      
      <div className="chart-wrapper">
        <ResponsiveContainer width="100%" height={400}>
          <LineChart
            data={chartData}
            margin={{
              top: 20,
              right: 30,
              left: 20,
              bottom: 20,
            }}
          >
            <CartesianGrid strokeDasharray="3 3" stroke="#e0e0e0" />
            <XAxis 
              dataKey="date"
              tickFormatter={formatDate}
              stroke="#666"
              fontSize={12}
            />
            <YAxis 
              tickFormatter={formatCurrency}
              stroke="#666"
              fontSize={12}
            />
            <Tooltip 
              formatter={(value) => [formatCurrency(value), 'Valuation']}
              labelFormatter={(label) => `Date: ${formatDate(label)}`}
              contentStyle={{
                backgroundColor: '#fff',
                border: '1px solid #ccc',
                borderRadius: '4px'
              }}
            />
            <Legend />
            <Line 
              type="monotone" 
              dataKey="value" 
              stroke="#2563eb" 
              strokeWidth={3}
              dot={{ fill: '#2563eb', strokeWidth: 2, r: 5 }}
              activeDot={{ r: 7, stroke: '#2563eb', strokeWidth: 2 }}
              name="Valuation (£)"
            />
          </LineChart>
        </ResponsiveContainer>
      </div>
      
      <div className="chart-stats">
        <div className="stat">
          <span className="stat-label">Data Points:</span>
          <span className="stat-value">{chartData.length}</span>
        </div>
        <div className="stat">
          <span className="stat-label">Latest Value:</span>
          <span className="stat-value">
            {chartData.length > 0 ? formatCurrency(chartData[chartData.length - 1].value) : 'N/A'}
          </span>
        </div>
        <div className="stat">
          <span className="stat-label">Period:</span>
          <span className="stat-value">
            {chartData.length > 0 ? 
              `${formatDate(chartData[0].date)} - ${formatDate(chartData[chartData.length - 1].date)}` 
              : 'N/A'
            }
          </span>
        </div>
      </div>
    </div>
  );
};

export default InvestmentChart;