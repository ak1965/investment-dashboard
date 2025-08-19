import React, { useState } from 'react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';
import './StockDataFetcher.css';
import {Link} from 'react-router-dom';

const StockDataFetcher = () => {
  const [symbol, setSymbol] = useState('');
  const [stockData, setStockData] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [metadata, setMetadata] = useState(null);

  const fetchStockData = async () => {
    if (!symbol.trim()) {
      setError('Please enter a stock symbol');
      return;
    }

    setLoading(true);
    setError(null);
    
    try {
      const response = await fetch(`http://localhost:5000/api/stock-data/${symbol.toUpperCase()}`);
      
      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.error || `HTTP error! status: ${response.status}`);
      }
      
      const result = await response.json();
      
      if (result.success) {
        // Take only last 30 days for chart
        const chartData = result.data.slice(0, 30).reverse();
        setStockData(chartData);
        setMetadata(result.metadata);
      } else {
        setError(result.error || 'Failed to fetch data');
      }
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    fetchStockData();
  };

  const formatCurrency = (value) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
      minimumFractionDigits: 2,
      maximumFractionDigits: 2
    }).format(value);
  };

  const formatDate = (dateString) => {
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', {
      month: 'short',
      day: 'numeric'
    });
  };

  return (
    <div className="stock-data-container">
      <div className="stock-input-section">
        <Link to='/'>Home</Link>
        <h2>Stock Price Tracker</h2>
        <form onSubmit={handleSubmit} className="stock-form">
          <div className="input-group">
            <input
              type="text"
              value={symbol}
              onChange={(e) => setSymbol(e.target.value)}
              placeholder="Enter stock symbol (e.g., AAPL, MSFT)"
              className="stock-input"
              disabled={loading}
            />
            <button 
              type="submit" 
              className="fetch-button"
              disabled={loading || !symbol.trim()}
            >
              {loading ? 'Fetching...' : 'Get Stock Data'}
            </button>
          </div>
        </form>
      </div>

      {error && (
        <div className="error-message">
          <strong>Error:</strong> {error}
        </div>
      )}

      {metadata && (
        <div className="stock-metadata">
          <h3>{metadata.symbol} - Stock Price History</h3>
          <p>Last Updated: {metadata.last_refreshed}</p>
          <p>Timezone: {metadata.timezone}</p>
        </div>
      )}

      {stockData.length > 0 && (
        <div className="chart-section">
          <div className="chart-wrapper">
            <ResponsiveContainer width="100%" height={400}>
              <LineChart data={stockData} margin={{ top: 20, right: 30, left: 20, bottom: 20 }}>
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
                  formatter={(value, name) => [formatCurrency(value), name]}
                  labelFormatter={(label) => `Date: ${new Date(label).toLocaleDateString()}`}
                  contentStyle={{
                    backgroundColor: '#fff',
                    border: '1px solid #ccc',
                    borderRadius: '4px'
                  }}
                />
                <Legend />
                <Line 
                  type="monotone" 
                  dataKey="close" 
                  stroke="#2563eb" 
                  strokeWidth={2}
                  dot={{ fill: '#2563eb', strokeWidth: 2, r: 3 }}
                  name="Closing Price"
                />
                <Line 
                  type="monotone" 
                  dataKey="open" 
                  stroke="#10b981" 
                  strokeWidth={1}
                  dot={false}
                  name="Opening Price"
                />
              </LineChart>
            </ResponsiveContainer>
          </div>

          <div className="stock-stats">
            {stockData.length > 0 && (
              <>
                <div className="stat">
                  <span className="stat-label">Latest Close:</span>
                  <span className="stat-value">{formatCurrency(stockData[stockData.length - 1].close)}</span>
                </div>
                <div className="stat">
                  <span className="stat-label">Highest (30d):</span>
                  <span className="stat-value">
                    {formatCurrency(Math.max(...stockData.map(d => d.high)))}
                  </span>
                </div>
                <div className="stat">
                  <span className="stat-label">Lowest (30d):</span>
                  <span className="stat-value">
                    {formatCurrency(Math.min(...stockData.map(d => d.low)))}
                  </span>
                </div>
                <div className="stat">
                  <span className="stat-label">Data Points:</span>
                  <span className="stat-value">{stockData.length}</span>
                </div>
              </>
            )}
          </div>
        </div>
      )}
    </div>
  );
};

export default StockDataFetcher;