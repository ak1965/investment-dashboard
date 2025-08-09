import './FormEnter.css'
import { Link } from 'react-router-dom';


export default function FormEnter() {
  const sendInputValueToApi = async (restaurant, location, website, score) => {
    const response = await fetch('http://localhost:5000/api/curry', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ 
          restaurant: restaurant,
          location: location,
          website: website,
          score: score
        })
    });

    
    
    if (!response.ok) {
      throw new Error('Failed to submit');
    }
    
    return response.json();
  };

  const handleSubmit = async (event) => {
    event.preventDefault();

    const formData = new FormData(event.target);
    const restaurant = formData.get('inputName');
    const location = formData.get('locName');
    const website = formData.get('website');
    const score = formData.get('score');

    try {
      await sendInputValueToApi(restaurant, location, website, score);
      console.log('Form submitted successfully!');
      event.target.reset(); // Clear the form
    } catch (error) {
      console.error('Error submitting form:', error);
      // You might want to show an error message to the user
    }
  };

  return (<>
    <Link to="/" className="nav-link">🏠 Home</Link>
    <form onSubmit={handleSubmit}>
      <label>Restaurant name</label>
        <input type="text" name="inputName" required />
      <br/>
      <label>City</label>
        <input type="text" name="locName" required />
      <br/>
      <label>Website</label>
        <input type="text" name="website" required />
      <br/>
      <label>Score</label>
        <input type="text" name="score" required />
      <br/>
      <button type="submit">Send</button>
    </form>
    <div className="page-navigation">
        {/* <Link to="/delete" className="nav-link">🗑️ Delete Restaurant</Link>
        <Link to="/view" className="nav-link">📋 View All Restaurants</Link> */}
        
      </div>
      </>
  );
}