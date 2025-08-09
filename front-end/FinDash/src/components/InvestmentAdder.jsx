import { Link } from 'react-router-dom';
import { useState, useEffect } from 'react';
import './InvestmentAdder.css'

export default function InvestmentAdder() {  // This function wrapper was missing
    const [files, setFiles] = useState([]);  // This was missing
    const [loading, setLoading] = useState(true);  // This was missing
    const [selectedFile, setSelectedFile] = useState('');
    const [portfolioName, setPortfolioName] = useState('');
    const [processing, setProcessing] = useState(false);
    const [generatingPdf, setGeneratingPdf] = useState(false);

    // This useEffect was missing
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
                    portfolio: portfolioName
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

    

const handleGeneratePdf = async () => {
    console.log("Starting PDF generation...");  // Add this
    setGeneratingPdf(true);
    
    try {
        console.log("Fetching from:", 'http://localhost:5000/api/generate-pdf');  // Add this
        
        const response = await fetch('http://localhost:5000/api/generate-pdf', {
            method: 'GET',
        });
        
        console.log("Response received:", response);  // Add this
        console.log("Response status:", response.status);  // Add this
        console.log("Response headers:", response.headers);  // Add this
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const blob = await response.blob();
        console.log("Blob created:", blob);  // Add this
        
        const url = window.URL.createObjectURL(blob);
        window.open(url, '_blank');
        
    } catch (error) {
        console.error('Error generating PDF:', error);
        alert('Error generating PDF: ' + error.message);
    } finally {
        setGeneratingPdf(false);
    }
};

// Add this button to your JSX:


    if (loading) {
        return <p>Loading files...</p>;
    }

    return (
        <>
            <Link to="/">Home</Link>
            <h2>Investment File Processor</h2>
            <div className="select-screen">
            
            {/* File selection dropdown */}
            <select value={selectedFile} onChange={(e) => setSelectedFile(e.target.value)}>
                <option value="">-- Select a file --</option>
                {files.map((file, index) => (
                    <option key={index} value={file.name}>
                        {file.name}
                    </option>
                ))}
            </select>
            
            {/* Portfolio name input */}
            <input 
                type="text" 
                placeholder="Portfolio name (e.g., ISA, SIPP)"
                value={portfolioName}
                onChange={(e) => setPortfolioName(e.target.value)}
            />
            
            <button 
                onClick={handleSubmit} 
                disabled={!selectedFile || processing}
            >
                {processing ? 'Processing...' : 'Process File'}
            </button>
            <button 
                onClick={handleGeneratePdf} 
                disabled={generatingPdf}
            >
                {generatingPdf ? 'Generating PDF...' : 'Generate PDF Report'}
            </button>
            </div>
        </>
    );
}  