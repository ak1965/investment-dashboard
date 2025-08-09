import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';


function RestaurantDeleter() {
  const [restaurants, setRestaurants] = useState([]);
  const [selectedId, setSelectedId] = useState('');
  const [message, setMessage] = useState({ text: '', type: '' });

  useEffect(() => {
    console.log('Component mounted, fetching restaurants...'); // Debug
    fetchRestaurants();
  }, []);

  const fetchRestaurants = async () => {
    console.log('fetchRestaurants called'); // Debug
    try {
      const response = await fetch('http://localhost:5000/api/restaurants', {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json'
        }
      });
      
      console.log('Response status:', response.status); // Debug
      console.log('Response ok:', response.ok); // Debug
      
      if (response.ok) {
        const data = await response.json();
        console.log('Raw API response:', data); // Debug
        console.log('Is data an array?', Array.isArray(data)); // Debug
        console.log('Data length:', data?.length); // Debug
        
        setRestaurants(data.data);
      } else {
        console.log('Response not ok:', response.status); // Debug
        setMessage({ text: 'Failed to fetch restaurants', type: 'error' });
      }
    } catch (error) {
      console.error('Fetch error:', error); // Debug
      setMessage({ text: 'Failed to load restaurants', type: 'error' });
    }
  };

  // 👈 ADD THIS MISSING FUNCTION
  const deleteRestaurant = async () => {
    if (!selectedId) {
      setMessage({ text: 'Please select a restaurant to delete', type: 'error' });
      return;
    }

    if (window.confirm('Are you sure you want to delete this restaurant?')) {
      try {
        const response = await fetch(`http://localhost:5000/api/restaurants/${selectedId}`, {
          method: 'DELETE'
        });
        
        if (response.ok) {
          // Remove from local state
          setRestaurants(prev => prev.filter(restaurant => restaurant.id !== parseInt(selectedId)));
          setSelectedId(''); // Reset selection
          setMessage({ text: 'Restaurant deleted successfully!', type: 'success' });
        } else {
          setMessage({ text: 'Failed to delete restaurant', type: 'error' });
        }
      } catch (error) {
        setMessage({ text: 'Error: ' + error.message, type: 'error' });
      }
    }
  };

  // Debug current state
  console.log('Current restaurants state:', restaurants);
  console.log('Restaurants length:', restaurants.length);

  return (
    <div>
        <Link to='/'>Home</Link>
      <h3>Delete Restaurant</h3>
      
      {message.text && <div className={`message ${message.type}`}>{message.text}</div>}
      
      {/* Debug display */}
      <p>Debug: Found {restaurants.length} restaurants</p>
      
      <div className="delete-form">
        <label htmlFor="restaurant-select">Select Restaurant to Delete:</label>
        <select 
          id="restaurant-select"
          value={selectedId} 
          onChange={(e) => setSelectedId(e.target.value)}
        >
          <option value="">-- Choose a restaurant ({restaurants.length} available) --</option>
          {restaurants.map(restaurant => (
            <option key={restaurant.id} value={restaurant.id}>
              {restaurant.name} - {restaurant.town}
            </option>
          ))}
        </select>
        
        <button 
          onClick={deleteRestaurant} 
          disabled={!selectedId}
          className="delete-btn"
        >
          Delete Selected Restaurant
        </button>
      </div>
      
    </div>
  );
}

export default RestaurantDeleter;