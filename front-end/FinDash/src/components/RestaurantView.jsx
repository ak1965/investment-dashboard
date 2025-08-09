import React, { useState, useEffect } from 'react';
import './Restaurant.css'
import { Link } from 'react-router-dom';


function ViewRestaurants() {
  const [restaurants, setRestaurants] = useState([]); // ✅ Start with empty array
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    fetchRestaurants();
  }, []);

  const fetchRestaurants = async () => {
    try {
      const response = await fetch('http://localhost:5000/api/restaurants', {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json'
        }
      });
      
      if (response.ok) {
        const data = await response.json();
        console.log('API Response:', data); // Debug line
        
        // Handle different response formats
        if (Array.isArray(data)) {
          setRestaurants(data);
        } else if (data.restaurants && Array.isArray(data.restaurants)) {
          setRestaurants(data.restaurants);
        } else if (data.data && Array.isArray(data.data)) {
          setRestaurants(data.data);
        } else {
          console.error('Unexpected data format:', data);
          setError('Unexpected data format from server');
        }
      } else {
        setError('Failed to fetch restaurants');
      }
    } catch (err) {
      console.error('Fetch error:', err);
      setError('Error: ' + err.message);
    } finally {
      setLoading(false);
    }
  };

  if (loading) return <div>Loading restaurants...</div>;
  if (error) return <div className="error">{error}</div>;

  return (
    <div className="view-restaurants">
        <Link to='/'>Home</Link>
      <h2>All Restaurants ({restaurants.length})</h2>
      
      {restaurants.length === 0 ? (
        <p>No restaurants found. <a href="/form">Add one now!</a></p>
      ) : (
        <div className="restaurant-grid">
          {restaurants.map(restaurant => (
            <div key={restaurant.id} className="restaurant-box">
              <h3>{restaurant.name}</h3>
              <div className="restaurant-details">
                <p><strong>📍 Town:</strong> {restaurant.location}</p>
                <p><strong>⭐ Score:</strong> {restaurant.score}</p>
                <p><strong>🌐 Website:</strong> 
                  <a href={restaurant.website} target="_blank" rel="noopener noreferrer">
                    {restaurant.website}
                  </a>
                </p>
              </div>
            </div>
          ))}
        </div>
      )}
      
    </div>
  );
}

export default ViewRestaurants;