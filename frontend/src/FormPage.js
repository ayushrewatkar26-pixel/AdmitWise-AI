import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';

const FormPage = () => {
  const navigate = useNavigate();

  const [studentData, setStudentData] = useState(null);
  const [preferences, setPreferences] = useState({
    cap: 'CAP1',
    caste_category: '',
    branch: '',
    city: 'Nagpur',
    state: 'Maharashtra'
  });
  const [options, setOptions] = useState({
    caps: [],
    casteCategories: [],
    branches: [],
    cities: [],
    states: []
  });
  const [loading, setLoading] = useState(false);
  const [error, ] = useState('');

  useEffect(() => {
    // Load student data from localStorage
    const savedData = localStorage.getItem('studentData');
    const parsed = savedData ? JSON.parse(savedData) : null;

    if (!parsed) {
      navigate('/');
      return;
    }

    // Fill extracted student data
    setStudentData({
      name: parsed.extracted_data.name || '',
      exam_year: parsed.extracted_data.year || '',
      percentile: parsed.extracted_data.percentile || '',
      caste_category: parsed.extracted_data.category || ''
    });

    // Hardcoded option lists
    const optionsData = {
      caps: ['CAP1', 'CAP2', 'CAP3'],
      casteCategories: [
        "DEFOBCS","DEFOPENS","DEFRNT1S","DEFRNT2S","DEFRNT3S","DEFROBCS","DEFRSCS","DEFRSEBC",
        "DEFRVJS","DEFSCS","DEFSEBCS","DEFSTS","EWS","GNT1H","GNT1O","GNT1S","GNT2H","GNT2O",
        "GNT2S","GNT3H","GNT3O","GNT3S","GOBCH","GOBCO","GOBCS","GOPENH","GOPENO","GOPENS",
        "GSCH","GSCO","GSCS","GSEBCH","GSEBCO","GSEBCS","GSTH","GSTO","GSTS","GVJH","GVJO",
        "GVJS","LNT1H","LNT1O","LNT1S","LNT2H","LNT2O","LNT2S","LNT3H","LNT3O","LNT3S",
        "LOBCH","LOBCO","LOBCS","LOPENH","LOPENO","LOPENS","LSCH","LSCO","LSCS","LSEBCH",
        "LSEBCO","LSEBCS","LSTH","LSTO","LSTS","LVJH","LVJO","LVJS","MI","ORPHAN","PWDOBCH",
        "PWDOBCS","PWDOPENH","PWDOPENS","PWDRNT1S","PWDRNT2S","PWDRNT3S","PWDROBC","PWDRSCS",
        "PWDRSTH","PWDRSTS","PWDRVJS","PWDSCH","PWDSCS","PWDSEBCS","TFWS"
      ],
      branches: [
        "Aeronautical Engineering",
        "Artificial Intelligence",
        "Artificial Intelligence (AI) and Data Science",
        "Artificial Intelligence and Data Science",
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
        "Computer Science and Engineering (Internet of Things and Cyber Security Including Block Chain)",
        "Computer Science and Engineering (IoT)",
        "Computer Science and Engineering (Data Science)",
        "Computer Technology",
        "Cyber Security",
        "Data Science",
        "Electrical Engg [Electronics and Power]",
        "Electrical Engineering",
        "Electronics and Communication (Advanced Communication Technology)",
        "Electronics and Communication Engineering",
        "Electronics and Computer Engineering",
        "Electronics and Computer Science",
        "Electronics and Telecommunication Engg",
        "Electronics Engineering",
        "Electronics Engineering (VLSI Design and Technology)",
        "Fibres and Textile Processing Technology",
        "Food Engineering and Technology",
        "Food Technology",
        "Industrial IoT",
        "Information Technology",
        "Instrumentation and Control Engineering",
        "Instrumentation Engineering",
        "Internet of Things (IoT)",
        "Mechanical and Mechatronics Engineering (Additive Manufacturing)",
        "Mechanical Engineering",
        "Mechanical Engineering [Sandwich]",
        "Mechanical Engineering Automobile",
        "Mechatronics Engineering",
        "Oil and Paints Technology",
        "Oil Technology",
        "Oil, Oleochemicals and Surfactants Technology",
        "Paper and Pulp Technology",
        "Petro Chemical Engineering",
        "Pharmaceutical Chemistry and Technology",
        "Plastic and Polymer Engineering",
        "Polymer Engineering and Technology",
        "Printing and Packing Technology",
        "Production Engineering [Sandwich]",
        "Robotics and Automation",
        "Robotics and Artificial Intelligence",
        "Surface Coating Technology",
        "Textile Engineering / Technology",
        "Textile Technology"
      ],
      cities: ["Nagpur", "Pune", "Mumbai", "Amravti", "Yavatmal"],
      states: ["Maharashtra"]
    };

    setOptions(optionsData);

    // Set sensible defaults (prefer extracted category if available)
    const defaultCaste = parsed?.extracted_data?.category || optionsData.casteCategories[0];
    const defaultBranch = optionsData.branches.find(b => b.toLowerCase().includes('computer science and engineering')) || optionsData.branches[0];

    setPreferences(prev => ({
      ...prev,
      cap: optionsData.caps[0],
      caste_category: defaultCaste,
      branch: defaultBranch,
      city: optionsData.cities[0],
      state: optionsData.states[0]
    }));
  }, [navigate]);

  const handlePreferenceChange = (field, value) => {
    setPreferences(prev => ({ ...prev, [field]: value }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
  
    try {
      const payload = {
        exam_year: studentData.exam_year,
        score: Number(studentData.percentile),
        cap: preferences.cap,
        caste_category: preferences.caste_category,
        branch: preferences.branch,
        city: preferences.city,
        state: preferences.state,
        // Add user data for database storage
        user_id: studentData.user_id,
        marksheet_id: studentData.marksheet_id
      };
  
      const url = "http://localhost:5000/predict";
      console.log("Posting to:", url, "with payload:", payload);
  
      const response = await axios.post(url, payload);
  
      console.log("Response received:", response.data);
  
      localStorage.setItem("predictionResults", JSON.stringify({
        results: response.data.results,
        message: response.data.message || '',
        available: response.data.available || { branches: [], categories: [] },
        exam_year: studentData.exam_year,
        user_score: studentData.percentile,
        cap: preferences.cap,
        caste_category: preferences.caste_category,
        branch: preferences.branch,
        city: preferences.city,
        state: preferences.state
      }));
  
      navigate("/results");
  
    } catch (err) {
      // Log full error object
      console.error("Axios error:", err);
  
      if (err.response) {
        // Server responded with status code outside 2xx
        console.error("Response data:", err.response.data);
        console.error("Status code:", err.response.status);
        console.error("Headers:", err.response.headers);
      } else if (err.request) {
        // Request made but no response received
        console.error("No response received:", err.request);
      } else {
        // Something else triggered the error
        console.error("Error message:", err.message);
      }
  
      alert(`Request failed: ${err.message}`);
    } finally {
      setLoading(false);
    }
  };    

  if (!studentData) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin w-8 h-8 border-4 border-primary-600 border-t-transparent rounded-full mx-auto mb-4"></div>
          <p className="text-secondary-600">Loading your data...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen py-12 px-4 sm:px-6 lg:px-8">
      <div className="max-w-4xl mx-auto">
        <div className="text-center mb-8">
          <h1 className="text-4xl font-bold text-secondary-900 mb-4">
            Review & Set Preferences
          </h1>
          <p className="text-lg text-secondary-600">
            Review your extracted details and set your college preferences
          </p>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          {/* Auto-filled Details */}
          <div className="card p-6">
            <h2 className="text-2xl font-semibold text-secondary-900 mb-6 flex items-center">
              <svg className="w-6 h-6 text-primary-600 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
              </svg>
              Auto-Extracted Details
            </h2>

            <div className="space-y-4">
              <div className="flex items-center justify-between p-3 bg-secondary-50 rounded-lg">
                <span className="font-medium text-secondary-700">Name:</span>
                <span className="text-secondary-900">{studentData.name}</span>
              </div>

              <div className="flex items-center justify-between p-3 bg-secondary-50 rounded-lg">
                <span className="font-medium text-secondary-700">Exam Year:</span>
                <span className="text-secondary-900">{studentData.exam_year}</span>
              </div>

              <div className="flex items-center justify-between p-3 bg-secondary-50 rounded-lg">
                <span className="font-medium text-secondary-700">Total Percentile:</span>
                <span className="text-secondary-900 font-semibold">{studentData.percentile}</span>
              </div>

              <div className="flex items-center justify-between p-3 bg-secondary-50 rounded-lg">
                <span className="font-medium text-secondary-700">Category:</span>
                <span className="text-secondary-900">{studentData.caste_category}</span>
              </div>
            </div>

            {/* Restored blue info box */}
            <div className="mt-6 p-4 bg-blue-50 border border-blue-200 rounded-lg">
              <div className="flex items-start">
                <svg className="w-5 h-5 text-blue-400 mt-0.5 mr-2" fill="currentColor" viewBox="0 0 20 20">
                  <path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z" clipRule="evenodd" />
                </svg>
                <div>
                  <p className="text-sm text-blue-800">
                    These details were automatically extracted from your marksheet.
                    If any information is incorrect, please re-upload your marksheet.
                  </p>
                </div>
              </div>
            </div>
          </div>

          {/* Preferences Form */}
          <div className="card p-6">
            <h2 className="text-2xl font-semibold text-secondary-900 mb-6 flex items-center">
              <svg className="w-6 h-6 text-primary-600 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 6V4m0 2a2 2 0 100 4m0-4a2 2 0 110 4m-6 8a2 2 0 100-4m0 4a2 2 0 100 4m0-4v2m0-6V4m6 6v10m6-2a2 2 0 100-4m0 4a2 2 0 100 4m0-4v2m0-6V4" />
              </svg>
              Select Your Preferences
            </h2>

            <form onSubmit={handleSubmit} className="space-y-6">
              {/* CAP */}
              <div>
                <label className="block text-sm font-medium text-secondary-700 mb-2">CAP Round</label>
                <select
                  value={preferences.cap}
                  onChange={(e) => handlePreferenceChange('cap', e.target.value)}
                  className="input-field"
                >
                  {options.caps?.map(cap => (
                    <option key={cap} value={cap}>{cap}</option>
                  ))}
                </select>
              </div>

              {/* Caste Category */}
              <div>
                <label className="block text-sm font-medium text-secondary-700 mb-2">Caste Category</label>
                <select
                  value={preferences.caste_category}
                  onChange={(e) => handlePreferenceChange('caste_category', e.target.value)}
                  className="input-field"
                >
                  {options.casteCategories?.map(cat => (
                    <option key={cat} value={cat}>{cat}</option>
                  ))}
                </select>
              </div>

              {/* Branch */}
              <div>
                <label className="block text-sm font-medium text-secondary-700 mb-2">Branch</label>
                <select
                  value={preferences.branch}
                  onChange={(e) => handlePreferenceChange('branch', e.target.value)}
                  className="input-field"
                >
                  {options.branches?.map(branch => (
                    <option key={branch} value={branch}>{branch}</option>
                  ))}
                </select>
              </div>

              {/* City */}
              <div>
                <label className="block text-sm font-medium text-secondary-700 mb-2">City</label>
                <select
                  value={preferences.city}
                  onChange={(e) => handlePreferenceChange('city', e.target.value)}
                  className="input-field"
                >
                  {options.cities?.map(city => (
                    <option key={city} value={city}>{city}</option>
                  ))}
                </select>
              </div>

              {/* State */}
              <div>
                <label className="block text-sm font-medium text-secondary-700 mb-2">State</label>
                <select
                  value={preferences.state}
                  onChange={(e) => handlePreferenceChange('state', e.target.value)}
                  className="input-field"
                >
                  {options.states?.map(state => (
                    <option key={state} value={state}>{state}</option>
                  ))}
                </select>
              </div>

              {error && (
                <div className="p-4 bg-red-50 border border-red-200 rounded-lg">
                  <div className="flex items-center">
                    <svg className="w-5 h-5 text-red-400 mr-2" fill="currentColor" viewBox="0 0 20 20">
                      <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clipRule="evenodd" />
                    </svg>
                    <p className="text-red-700">{error}</p>
                  </div>
                </div>
              )}

              <div className="flex space-x-4">
                <button
                  type="button"
                  onClick={() => navigate('/')}
                  className="btn-secondary flex-1"
                >
                  Back to Upload
                </button>
                <button
                  type="submit"
                  disabled={loading}
                  className={`btn-primary flex-1 ${loading ? 'opacity-50 cursor-not-allowed' : ''}`}
                >
                  {loading ? (
                    <div className="flex items-center justify-center space-x-2">
                      <svg className="animate-spin w-5 h-5" fill="none" viewBox="0 0 24 24">
                        <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                        <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                      </svg>
                      <span>Predicting...</span>
                    </div>
                  ) : (
                    'Get Predictions'
                  )}
                </button>
              </div>
            </form>
          </div>
        </div>

        {/* Summary Card (restored) */}
        <div className="mt-8 card p-6">
          <h3 className="text-lg font-semibold text-secondary-900 mb-4 text-center">Prediction Summary</h3>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div className="text-center p-4 bg-primary-50 rounded-lg">
              <div className="text-2xl font-bold text-primary-600">{studentData.percentile}</div>
              <div className="text-sm text-secondary-600">Your Percentile</div>
            </div>

            <div className="text-center p-4 bg-secondary-50 rounded-lg">
              <div className="text-2xl font-bold text-secondary-600">{preferences.cap}</div>
              <div className="text-sm text-secondary-600">Selected CAP</div>
            </div>

            <div className="text-center p-4 bg-secondary-50 rounded-lg">
              <div className="text-2xl font-bold text-secondary-600">{preferences.caste_category}</div>
              <div className="text-sm text-secondary-600">Caste Category</div>
            </div>

            <div className="text-center p-4 bg-secondary-50 rounded-lg">
              <div className="text-2xl font-bold text-secondary-600">{preferences.branch}</div>
              <div className="text-sm text-secondary-600">Preferred Branch</div>
            </div>

            <div className="text-center p-4 bg-secondary-50 rounded-lg">
              <div className="text-2xl font-bold text-secondary-600">{preferences.city}</div>
              <div className="text-sm text-secondary-600">Preferred City</div>
            </div>

            <div className="text-center p-4 bg-secondary-50 rounded-lg">
              <div className="text-2xl font-bold text-secondary-600">{preferences.state}</div>
              <div className="text-sm text-secondary-600">Preferred State</div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default FormPage;
