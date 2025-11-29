import React, { useState, useEffect, useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import jsPDF from 'jspdf';
import * as XLSX from 'xlsx';
import axios from 'axios'; // <-- Added for API calls

const ResultsPage = () => {
  const [results, setResults] = useState(null);
  const [filteredResults, setFilteredResults] = useState([]);
  const [sortBy, setSortBy] = useState('admission_chance');
  const [sortOrder, setSortOrder] = useState('desc');
  const [filters, setFilters] = useState({
    city: '',
    branch: ''
  });
  const [loading, setLoading] = useState(true);
  const navigate = useNavigate();
  const isInitialMount = useRef(true);

  const sortResults = (data, column, order) => {
    return [...data].sort((a, b) => {
      let valA = a[column];
      let valB = b[column];
  
      if (typeof valA === 'string') valA = valA.toLowerCase();
      if (typeof valB === 'string') valB = valB.toLowerCase();
  
      if (valA > valB) return order === 'asc' ? 1 : -1;
      if (valA < valB) return order === 'asc' ? -1 : 1;
      return 0;
    });
  };

  const cities = ["Nagpur", "Pune", "Mumbai", "Amravti", "Yavatmal"];
  const branches = [
    "Aeronautical Engineering",
    "Artificial Intelligence",
    "Artificial Intelligence (AI) and Data Science",
    "Artificial Intelligence and Machine Learning",
    "Automobile Engineering",
    "Automation and Robotics",
    "Bio Medical Engineering",
    "Bio Technology",
    "Chemical Engineering",
    "Civil and infrastructure Engineering",
    "Civil Engineering",
    "Computer Engineering",
    "Computer Engineering (Software Engineering)",
    "Computer Science",
    "Computer Science and Design",
    "Computer Science and Business Systems",
    "Computer Science and Engineering",
    "Computer Science and Engineering (Artificial Intelligence)",
    "Computer Science and Engineering (Artificial Intelligence and Machine Learning)",
    "Computer Science and Engineering (Cyber Security)",
    "Computer Science and Engineering (IoT)",
    "Computer Science and Engineering (Data Science)",
    "Computer Technology",
    "Cyber Security",
    "Data Science",
    "Electrical Engg [Electronics and Power]",
    "Electrical Engineering",
    "Electronics and Communication Engineering",
    "Electronics and Computer Engineering",
    "Electronics and Telecommunication Engg",
    "Electronics Engineering",
    "Mechanical Engineering",
    "Mechatronics Engineering",
    "Textile Engineering / Technology"
  ];

  useEffect(() => {
    const savedResults = localStorage.getItem('predictionResults');
    if (savedResults) {
      const data = JSON.parse(savedResults);
      setResults(data);
      setFilteredResults(data.results || []);
      // If there are no results, we still keep message and available options
      setFilters({
        city: data.city || '',
        branch: data.branch || ''
      });
    } else {
      navigate('/');
    }
    setLoading(false);
  }, [navigate]);

  // Auto-apply filters when they change (but not on initial mount)
  useEffect(() => {
    // Skip if no results
    if (!results) {
      return;
    }

    // On first run after results are loaded, skip applying filters
    // This prevents applying filters when component first mounts with saved filter values
    if (isInitialMount.current) {
      isInitialMount.current = false;
      return;
    }

    // Debounce to avoid too many API calls
    const timer = setTimeout(() => {
      applyFilters();
    }, 300);
    return () => clearTimeout(timer);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [filters.city, filters.branch]);

  // ------------------ UPDATED ------------------
  const applyFilters = async () => {
    try {
      if (!results) return;

      setLoading(true);

      // Use selected city or fallback to original city from results
      // Backend requires a city, so we always use a valid one
      const selectedCity = filters.city || results.city || '';
      if (!selectedCity) {
        console.error("No city available for filtering");
        setLoading(false);
        return;
      }

      // Construct payload with all required values
      const payload = {
        exam_year: results.exam_year,              // current exam year
        score: results.user_score,                 // user's score
        cap: results.cap,                          // CAP value (CAP1/CAP2)
        caste_category: results.caste_category,   // caste category (GENERAL/OBC/etc.)
        city: selectedCity,                        // selected city or original
        branch: filters.branch || ''               // selected branch, empty = all branches
      };

      console.log("Applying filters with payload:", payload);

      // POST request to filter-results endpoint
      const response = await axios.post("http://localhost:5000/filter-results", payload);

      let filtered = response.data.results || [];

      // Apply frontend sorting after filtering
      filtered = sortResults(filtered, sortBy, sortOrder);

      setFilteredResults(filtered);
      console.log("Filtered results count:", filtered.length);

    } catch (err) {
      console.error("Filter error:", err);
      if (err.response) {
        console.error("Response data:", err.response.data);
        console.error("Status code:", err.response.status);
      }
      setFilteredResults([]);
    } finally {
      setLoading(false);
    }
  };
    
  // ----------------------------------------------

  const handleSort = (column) => {
    let newOrder = sortOrder;
    if (sortBy === column) {
      newOrder = sortOrder === 'asc' ? 'desc' : 'asc';
      setSortOrder(newOrder);
    } else {
      setSortBy(column);
      newOrder = 'desc';
      setSortOrder(newOrder);
    }
  
    setFilteredResults(sortResults(filteredResults, column, newOrder));
  };  

  const handleFilterChange = (field, value) => {
    setFilters(prev => ({ ...prev, [field]: value }));
  };

  const clearFilters = () => {
    // Reset filters to original values from results
    setFilters({ 
      city: results?.city || '', 
      branch: results?.branch || '' 
    });
    // Reset to original results
    if (results) {
      setFilteredResults(results.results || []);
    }
  };

  const exportToPDF = () => {
    const doc = new jsPDF('landscape', 'mm', 'a4');
    const pageWidth = doc.internal.pageSize.getWidth();
    const pageHeight = doc.internal.pageSize.getHeight();
    
    // Title and header
    doc.setFontSize(20);
    doc.setFont(undefined, 'bold');
    doc.text('CET Admission Prediction Results', pageWidth / 2, 20, { align: 'center' });
    
    doc.setFontSize(12);
    doc.setFont(undefined, 'normal');
    doc.text(`Exam Year: ${results?.exam_year}`, pageWidth / 2, 30, { align: 'center' });
    
    // Table setup with better proportions
    const headers = ['College', 'Code', 'Branch', 'Category', 'Cutoffs', 'Chance %'];
    const colWidths = [75, 25, 40, 30, 85, 25]; // Adjusted widths to fit better
    const rowHeight = 12;
    const startX = 10; // Moved left to give more space
    const startY = 45;
    let currentY = startY;
    
    // Helper function to truncate text properly
    const truncateText = (text, maxWidth) => {
      const words = text.toString().split(' ');
      let result = '';
      let testLine = '';
      
      for (let i = 0; i < words.length; i++) {
        testLine = result + (result ? ' ' : '') + words[i];
        const testWidth = doc.getTextWidth(testLine);
        
        if (testWidth > maxWidth - 4) { // 4mm padding
          break;
        }
        result = testLine;
      }
      
      if (result.length < text.length) {
        result = result.substring(0, result.length - 3) + '...';
      }
      
      return result;
    };
    
    // Draw table header - GUARANTEED VISIBLE
    doc.setFontSize(11);
    doc.setFont('helvetica', 'bold');
    
    let x = startX;
    headers.forEach((header, i) => {
      // Draw header cell background first
      doc.setFillColor(59, 130, 246);
      doc.rect(x, currentY, colWidths[i], rowHeight, 'F');
      
      // Draw header cell border
      doc.setDrawColor(0, 0, 0);
      doc.setLineWidth(0.5);
      doc.rect(x, currentY, colWidths[i], rowHeight, 'S');
      
      // Draw text with guaranteed visibility
      doc.setTextColor(255, 255, 255);
      doc.text(header, x + 4, currentY + 8);
      
      x += colWidths[i];
    });
    
    currentY += rowHeight;
    doc.setTextColor(0, 0, 0);
    doc.setFont('helvetica', 'normal');
    
    // Draw table rows
    filteredResults.forEach((college, index) => {
      // Check for page break
      if (currentY > pageHeight - 40) {
        doc.addPage('landscape', 'mm', 'a4');
        currentY = 20;
        
        // Redraw header - GUARANTEED VISIBLE
        doc.setFontSize(11);
        doc.setFont('helvetica', 'bold');
        x = startX;
        headers.forEach((header, i) => {
          // Draw header cell background first
          doc.setFillColor(59, 130, 246);
          doc.rect(x, currentY, colWidths[i], rowHeight, 'F');
          
          // Draw header cell border
          doc.setDrawColor(0, 0, 0);
          doc.setLineWidth(0.5);
          doc.rect(x, currentY, colWidths[i], rowHeight, 'S');
          
          // Draw text with guaranteed visibility
          doc.setTextColor(255, 255, 255);
          doc.text(header, x + 4, currentY + 8);
          
          x += colWidths[i];
        });
        currentY += rowHeight;
        doc.setTextColor(0, 0, 0);
        doc.setFont('helvetica', 'normal');
      }
      
      // Prepare row data
      const last5Years = [];
      const startYear = parseInt(results.exam_year) - 1;
      for (let i = 0; i < 5; i++) last5Years.push(startYear - i);
      const cutoffRow = last5Years.reverse().map(year => college.previous_cutoffs?.[year] ?? "-").join(", ");
      
      const rowData = [
        college.college_name || '',
        college.college_code || '',
        college.branch_name || '',
        college.seat_type || '',
        cutoffRow,
        `${college.admission_chance || 0}%`
      ];
      
      // Draw row background
      if (index % 2 === 0) {
        doc.setFillColor(248, 250, 252);
        x = startX;
        headers.forEach((_, i) => {
          doc.rect(x, currentY, colWidths[i], rowHeight, 'F');
          x += colWidths[i];
        });
      }
      
      // Draw cell borders and content
      x = startX;
      rowData.forEach((data, i) => {
        // Draw cell border
        doc.setDrawColor(0, 0, 0);
        doc.setLineWidth(0.1);
        doc.rect(x, currentY, colWidths[i], rowHeight);
        
        // Truncate and draw text
        const truncatedText = truncateText(data, colWidths[i]);
        doc.text(truncatedText, x + 2, currentY + 8);
        x += colWidths[i];
      });
      
      currentY += rowHeight;
    });
    
    // Add footer
    doc.setFontSize(8);
    doc.setTextColor(128, 128, 128);
    doc.text('Generated by AdmitWise AI', pageWidth / 2, pageHeight - 10, { align: 'center' });
    
    doc.save('cet-admission-results.pdf');
  };

  const exportToExcel = () => {
    const worksheet = XLSX.utils.json_to_sheet(filteredResults.map(college => {
      const last5Years = [];
      const startYear = parseInt(results.exam_year) - 1;
      for (let i = 0; i < 5; i++) last5Years.push(startYear - i);
      const cutoffRow = last5Years.reverse().map(year => college.previous_cutoffs?.[year] ?? "-").join(", ");

      return {
        'College Name': college.college_name,
        'College Code': college.college_code,
        'Branch': college.branch_name,
        'Branch code': college.branch_code,
        'Caste Category': college.seat_type,
        'Previous Years Cutoffs': cutoffRow,
        'Admission Chance %': college.admission_chance
      };
    }));
    const workbook = XLSX.utils.book_new();
    XLSX.utils.book_append_sheet(workbook, worksheet, 'Admission Results');
    XLSX.writeFile(workbook, 'cet-admission-results.xlsx');
  };

  const getChanceColor = (chance) => {
    if (chance >= 80) return 'text-green-600 bg-green-100';
    if (chance >= 60) return 'text-yellow-600 bg-yellow-100';
    if (chance >= 40) return 'text-orange-600 bg-orange-100';
    return 'text-red-600 bg-red-100';
  };

  if (loading) return <div className="min-h-screen flex items-center justify-center"><p>Loading...</p></div>;
  if (!results) return <div>No results found. <button onClick={() => navigate('/')}>Go to Upload</button></div>;

  return (
    <div className="min-h-screen py-12 px-4 sm:px-6 lg:px-8">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="text-center mb-8">
          <h1 className="text-4xl font-bold text-secondary-900 mb-4">Admission Prediction Results</h1>
          <div className="flex flex-wrap items-center justify-center space-x-8 text-lg">
            <div>Your Score: <span className="font-bold text-primary-600">{results.user_score}</span></div>
            <div>Exam Year: <span className="font-bold text-primary-600">{results.exam_year}</span></div>
            <div>CAP: <span className="font-bold text-primary-600">{results.cap}</span></div>
            <div>Caste Category: <span className="font-bold text-primary-600">{results.caste_category}</span></div>
            <div>Colleges Found: <span className="font-bold text-primary-600">{filteredResults.length}</span></div>
          </div>
        </div>

        {/* Filters */}
        <div className="card p-6 mb-6">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-4">
            <div>
              <label className="block text-sm font-medium mb-2">Filter by City</label>
              <select
               value={filters.city}
               onChange={(e) => handleFilterChange('city', e.target.value)}
               className="input-field w-full"
              >
               <option value="">All Cities</option>
               {cities.map(city => <option key={city} value={city}>{city}</option>)}
              </select>
            </div>

            <div>
              <label className="block text-sm font-medium mb-2">Filter by Branch</label>
              <select
               value={filters.branch}
               onChange={(e) => handleFilterChange('branch', e.target.value)}
               className="input-field w-full"
              >
               <option value="">All Branches</option>
               {branches.map(branch => <option key={branch} value={branch}>{branch}</option>)}
              </select>
            </div>

            <div className="flex flex-col justify-end space-y-2">
              <button onClick={applyFilters} className="btn-primary w-full">Apply Filters</button>
              <button onClick={clearFilters} className="btn-secondary w-full">Clear Filters</button>
            </div>
          </div>

          {/* Export & Sort */}
          <div className="flex flex-wrap items-center justify-between gap-4">
            <div className="flex items-center space-x-4">
              <span>Sort by:</span>
              <select value={sortBy} onChange={(e) => setSortBy(e.target.value)} className="input-field w-auto">
                <option value="admission_chance">Admission Chance</option>
                <option value="college_name">College Name</option>
                <option value="college_code">College Code</option>
              </select>
              <button onClick={() => setSortOrder(sortOrder === 'asc' ? 'desc' : 'asc')} className="btn-secondary">
                {sortOrder === 'asc' ? '↑' : '↓'}
              </button>
            </div>

            <div className="flex items-center space-x-2">
              <button onClick={exportToPDF} className="btn-secondary">Export PDF</button>
              <button onClick={exportToExcel} className="btn-secondary">Export Excel</button>
            </div>
          </div>
        </div>

        {/* Empty state with suggestions */}
        {filteredResults.length === 0 && (
          <div className="card p-6 mb-6">
            <h3 className="text-xl font-semibold mb-2">No matching results</h3>
            {results?.message && (
              <p className="text-secondary-700 mb-4">{results.message}</p>
            )}
            {(results?.available?.branches?.length || results?.available?.categories?.length) ? (
              <div className="space-y-2">
                {results.available.branches?.length > 0 && (
                  <div>
                    <div className="font-medium mb-1">Available branches for your City+CAP:</div>
                    <div className="flex flex-wrap gap-2">
                      {results.available.branches.slice(0, 12).map(b => (
                        <span key={b} className="px-2 py-1 bg-secondary-100 rounded text-sm">{b}</span>
                      ))}
                    </div>
                  </div>
                )}
                {results.available.categories?.length > 0 && (
                  <div>
                    <div className="font-medium mb-1">Available categories for your City+CAP:</div>
                    <div className="flex flex-wrap gap-2">
                      {results.available.categories.slice(0, 12).map(c => (
                        <span key={c} className="px-2 py-1 bg-secondary-100 rounded text-sm">{c}</span>
                      ))}
                    </div>
                  </div>
                )}
            </div>
            ) : (
              <p className="text-secondary-700">Try changing branch, category, or CAP round.</p>
            )}
          </div>
        )}

        {/* Table */}
        <div className="card overflow-hidden">
          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-secondary-200">
              <thead className="bg-secondary-50">
                <tr>
                  <th onClick={() => handleSort('college_name')} className="px-6 py-3 cursor-pointer">College Name</th>
                  <th onClick={() => handleSort('college_code')} className="px-6 py-3 cursor-pointer">College Code</th>
                  <th className="px-6 py-3">Branch</th>
                  <th className="px-6 py-3">Branch Code</th>
                  <th className="px-6 py-3">Caste Category</th>
                  <th className="px-6 py-3">Previous 5 Years' Cutoffs</th>
                  <th onClick={() => handleSort('admission_chance')} className="px-6 py-3 cursor-pointer">Admission Chance %</th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-secondary-200">
                {filteredResults.map((college, index) => (
                  <tr key={index} className="hover:bg-secondary-50">
                    <td className="px-6 py-4">{college.college_name}</td>
                    <td className="px-6 py-4">{college.college_code}</td>
                    <td className="px-6 py-4">{college.branch_name}</td>
                    <td className="px-6 py-4">{college.branch_code}</td>
                    <td className="px-6 py-4">{college.seat_type}</td>
                    <td className="px-6 py-4">
                      <table className="cutoff-table border border-secondary-200 w-full text-center">
                        <thead>
                          <tr>
                            {Object.keys(college.previous_cutoffs || {}).map(year => (
                              <th key={year} className="border px-2 py-1">{year}</th>
                            ))}
                          </tr>
                        </thead>
                        <tbody>
                          <tr>
                            {Object.values(college.previous_cutoffs || {}).map((val, idx) => (
                              <td key={idx} className="border px-2 py-1">{val !== null ? val.toFixed(2) : "-"}</td>
                            ))}
                          </tr>
                        </tbody>
                      </table>
                    </td>
                    <td className="px-6 py-4">
                      <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${getChanceColor(college.admission_chance)}`}>
                        {college.admission_chance}%
                      </span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
          {filteredResults.length === 0 && (
            <div className="text-center py-8 text-secondary-600">Adjust filters above to see available results.</div>
          )}
        </div>

        {/* Action Buttons */}
        <div className="mt-8 flex justify-center space-x-4">
          <button onClick={() => navigate('/form')} className="btn-secondary">Change Preferences</button>
          <button onClick={() => navigate('/')} className="btn-primary">Start Over</button>
        </div>
      </div>
    </div>
  );
};

export default ResultsPage;
