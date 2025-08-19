import { Link } from 'react-router-dom';
import { useState, useEffect } from 'react';
import './InvestmentAdder.css'
import CalendarDatePicker from './calendar';

export default function InvestmentAdder() {
    const [files, setFiles] = useState([]);
    const [loading, setLoading] = useState(true);
    const [selectedFile, setSelectedFile] = useState('');
    const [portfolioName, setPortfolioName] = useState('');
    const [processing, setProcessing] = useState(false);
    
    const [selectedDate, setSelectedDate] = useState(null); // Add this for calendar

    useEffect(() => {
        const fetchFiles = async () => {
            try {
                const response = await fetch('http://localhost:5000/api/investment-files');
                
                if (!response.ok) {
                    throw new Error(`HTTP error! status: ${response.status}`);
                }
                
                const data = await response.json();
                
                if (data.success) {
                    setFiles(data.files);
                }
            } catch (error) {
                console.error('Error fetching files:', error);
            } finally {
                setLoading(false);
            }
        };

        fetchFiles();
    }, []);

    // Add this function to handle date selection
    const handleDateSelect = (dateStr, dateObj) => {
        setSelectedDate(dateStr);
        console.log('Selected date:', dateStr);
        // You can save this to database or use it in your processing
    };

    const handleSubmit = async () => {
        if (!selectedFile) return;
        
        setProcessing(true);
        
        try {
            const response = await fetch('http://localhost:5000/api/process-investment', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    filename: selectedFile,
                    portfolio: portfolioName,
                    date: selectedDate // Include the selected date
                })
            });
            
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            
            const data = await response.json();
            
            if (data.success) {
                console.log('Processing successful:', data);
                alert('Investment data processed successfully!');
            } else {
                console.error('Processing failed:', data.error);
                alert('Processing failed: ' + data.error);
            }
            
        } catch (error) {
            console.error('Error processing file:', error);
            alert('Error processing file: ' + error.message);
        } finally {
            setProcessing(false);
        }
    };

    

    if (loading) {
        return <p>Loading files...</p>;
    }

    return (
    <div className="investment-page">
        <div className="investment-form-container">
            <Link to="/" className="investment-home-link">← Home</Link>
            <h2>Investment File Processor</h2>
            
            <div className="investment-form-fields">
                <div className="investment-form-group">
                    <label>Select Date:</label>
                    <CalendarDatePicker 
                        onDateSelect={handleDateSelect}
                        placeholder="Pick a date"
                    />
                </div>

                <div className="investment-form-group">
                    <label>Select File:</label>
                    <select value={selectedFile} onChange={(e) => setSelectedFile(e.target.value)}>
                        <option value="">-- Select a file --</option>
                        {files.map((file, index) => (
                            <option key={index} value={file.name}>
                                {file.name}
                            </option>
                        ))}
                    </select>
                </div>
                
                <div className="investment-form-group">
                    <label>Portfolio Name:</label>
                    <input 
                        type="text" 
                        placeholder="Portfolio name (e.g., ISA, SIPP)"
                        value={portfolioName}
                        onChange={(e) => setPortfolioName(e.target.value)}
                    />
                </div>
                
                {selectedDate && (
                    <p className="investment-selected-date">
                        Selected Date: {new Date(selectedDate).toLocaleDateString('en-GB')}
                    </p>
                )}
                
                <div className="investment-buttons">
                    <button 
                        className="investment-btn investment-btn-process"
                        onClick={handleSubmit} 
                        disabled={!selectedFile || processing}
                    >
                        {processing ? 'Processing...' : 'Process File'}
                    </button>
                    
                    
                </div>
            </div>
        </div>
    </div>
);
}