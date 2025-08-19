import { Link } from 'react-router-dom';
import React, { useState, useEffect } from 'react';

export default function ReportGenerator() {
    const [generatingPdf, setGeneratingPdf] = useState(false);
    const [uniqueDates, setUniqueDates] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);

    // Fetch unique dates when component mounts
    useEffect(() => {
        fetchUniqueDates();
    }, []);

    const fetchUniqueDates = async () => {
        try {
            setLoading(true);
            const response = await fetch('http://localhost:5000/api/unique-dates');
            
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            
            const data = await response.json();
            
            if (data.success) {
                setUniqueDates(data.dates);
            } else {
                throw new Error(data.error || 'Failed to fetch dates');
            }
            
        } catch (error) {
            console.error('Error fetching unique dates:', error);
            setError(error.message);
        } finally {
            setLoading(false);
        }
    };

    const handleSelect = (event) => {
        const selectedValue = event.target.value;
        
        if (selectedValue === "all-investments") {
            handleGeneratePdf();
        } else if (selectedValue.startsWith("date-")) {
            // Extract date from the value (format: "date-YYYY-MM-DD")
            const selectedDate = selectedValue.replace("date-", "");
            handleGeneratePdf(selectedDate);
        }
    };

    const handleGeneratePdf = async (selectedDate = null) => {
        console.log(`Starting PDF generation for date: ${selectedDate || 'all dates'}...`);
        setGeneratingPdf(true);

        try {
            // Build URL with optional date parameter
            let url = 'http://localhost:5000/api/generate-pdf';
            if (selectedDate) {
                url += `?date=${selectedDate}`;
            }
            
            console.log("Fetching from:", url);

            const response = await fetch(url, {
                method: 'GET',
            });

            console.log("Response received:", response);
            console.log("Response status:", response.status);

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            const blob = await response.blob();
            console.log("Blob created:", blob);

            const downloadUrl = window.URL.createObjectURL(blob);
            window.open(downloadUrl, '_blank');

        } catch (error) {
            console.error('Error generating PDF:', error);
            alert('Error generating PDF: ' + error.message);
        } finally {
            setGeneratingPdf(false);
        }
    };

    // Format date for display (convert YYYY-MM-DD to more readable format)
    const formatDateForDisplay = (dateString) => {
        const date = new Date(dateString);
        return date.toLocaleDateString('en-GB', {
            year: 'numeric',
            month: 'long',
            day: 'numeric'
        });
    };

    return (
        <div>
            <Link to='/'>Home</Link>
            <h2>Investment Report Generator</h2>

            {loading && (
                <div>Loading available dates...</div>
            )}

            {error && (
                <div style={{ color: 'red' }}>
                    Error loading dates: {error}
                    <button onClick={fetchUniqueDates} style={{ marginLeft: '10px' }}>
                        Retry
                    </button>
                </div>
            )}

            {!loading && !error && (
                <div>
                    <label htmlFor="report-select">Select a Report:</label>
                    <select id="report-select" onChange={handleSelect} defaultValue="">
                        <option value="" disabled>
                            Select a Report
                        </option>
                        <option value="all-investments">
                            All Investments (All Dates)
                        </option>
                        {uniqueDates.length > 0 && (
                            <optgroup label="Reports by Date">
                                {uniqueDates.map((date, index) => (
                                    <option key={index} value={`date-${date}`}>
                                        {formatDateForDisplay(date)}
                                    </option>
                                ))}
                            </optgroup>
                        )}
                    </select>
                </div>
            )}

            {generatingPdf && (
                <div className="generating-message" style={{ 
                    marginTop: '20px', 
                    padding: '10px', 
                    backgroundColor: '#f0f0f0', 
                    borderRadius: '5px' 
                }}>
                    Generating PDF, please wait...
                </div>
            )}

            {uniqueDates.length === 0 && !loading && !error && (
                <div style={{ marginTop: '20px', color: '#666' }}>
                    No investment data found in the database.
                </div>
            )}
        </div>
    );
}