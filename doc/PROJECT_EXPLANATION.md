# AdmitWise AI - Comprehensive Project Explanation

## 📋 Table of Contents
1. [Project Overview](#project-overview)
2. [Architecture](#architecture)
3. [Technology Stack](#technology-stack)
4. [System Components](#system-components)
5. [Data Flow](#data-flow)
6. [Database Schema](#database-schema)
7. [API Endpoints](#api-endpoints)
8. [Key Features](#key-features)
9. [Machine Learning Integration](#machine-learning-integration)
10. [User Journey](#user-journey)

---

## 🎯 Project Overview

**AdmitWise AI** is a full-stack web application designed to help students in India predict their admission chances into engineering colleges based on their CET (Common Entrance Test) scores. The system uses:

- **OCR Technology** to automatically extract data from marksheets
- **Machine Learning (XGBoost)** for admission chance predictions
- **Historical Cutoff Data** from MySQL database
- **AI Chatbot (Google Gemini)** for student guidance
- **User Authentication** via Clerk for personalized experience

### Purpose
The application helps students:
- Upload their CET marksheet and automatically extract details
- Get personalized admission predictions for various colleges
- Filter results by city, branch, and other preferences
- Export results to PDF/Excel
- Get AI-powered guidance through a chatbot

---

## 🏗️ Architecture

The project follows a **client-server architecture** with clear separation:

```
┌─────────────────────────────────────────────────────────────┐
│                     FRONTEND (React)                         │
│  - UploadPage.js (File Upload)                               │
│  - FormPage.js (User Preferences)                            │
│  - ResultsPage.js (Display Predictions)                     │
│  - Chatbot.js (AI Assistant)                                │
└──────────────────────┬──────────────────────────────────────┘
                       │ HTTP/REST API
┌──────────────────────▼──────────────────────────────────────┐
│                  BACKEND (Flask)                            │
│  - app.py (Main API Server)                                 │
│  - user_data_manager.py (Database Operations)               │
│  - OCR Processing (Tesseract + OpenCV)                      │
│  - ML Model (XGBoost)                                        │
└──────────────────────┬──────────────────────────────────────┘
                       │
        ┌──────────────┼──────────────┐
        │              │              │
┌───────▼──────┐ ┌─────▼──────┐ ┌────▼─────┐
│   MySQL      │ │  Gemini AI │ │  Clerk   │
│  cutoff_db   │ │   API      │ │  Auth    │
│  user_data   │ │            │ │          │
└──────────────┘ └───────────┘ └──────────┘
```

---

## 💻 Technology Stack

### Backend
- **Flask** (v2.3.0+) - Web framework
- **Python 3.8+** - Programming language
- **XGBoost** (v1.7.0+) - Machine learning model
- **scikit-learn** - Feature preprocessing
- **OpenCV** (v4.8.0+) - Image processing
- **Tesseract OCR** - Text extraction from images
- **PyMuPDF (fitz)** - PDF text extraction
- **Pandas & NumPy** - Data manipulation
- **MySQL Connector** - Database connectivity
- **Google Generative AI** - Chatbot integration
- **Flask-CORS** - Cross-origin resource sharing

### Frontend
- **React** (v18.2.0) - UI framework
- **React Router** (v6.8.1) - Navigation
- **Tailwind CSS** (v3.2.7) - Styling
- **Axios** (v1.3.4) - HTTP client
- **React Dropzone** (v14.2.3) - File upload
- **jsPDF** (v2.5.1) - PDF generation
- **XLSX** (v0.18.5) - Excel export
- **Clerk React** (v5.48.1) - Authentication

### Database
- **MySQL** - Two schemas:
  - `cutoff_db` - Historical cutoff data
  - `user_data` - User information and predictions

### External Services
- **Clerk** - User authentication
- **Google Gemini AI** - Chatbot responses

---

## 🔧 System Components

### 1. **Backend (`app.py`)**

The main Flask application with the following key sections:

#### A. **Configuration & Setup**
- Flask app initialization with CORS
- Gemini AI model configuration (with fallback models)
- Database connection setup
- Upload folder configuration

#### B. **Helper Functions**

**`calculate_weighted_cutoff(previous_cutoffs, exam_year)`**
- Calculates weighted average cutoff from 5 years of data
- Weight distribution:
  - Year -1 (most recent): 60%
  - Year -2: 15%
  - Year -3: 15%
  - Year -4: 5%
  - Year -5: 5%
- Handles missing years by redistributing weights

**`parse_marksheet(text)`**
- Extracts student information from OCR text:
  - Name
  - Exam Year
  - Percentile/Score
  - Caste Category
- Uses regex patterns for extraction

**`extract_text_from_image(filepath)`**
- Uses OpenCV for image preprocessing
- Tesseract OCR for text extraction

**`extract_text_from_pdf(filepath)`**
- Uses PyMuPDF to extract text from PDF files

**`prepare_features(df)` & `train_model()`**
- Prepares features for XGBoost model:
  - Branch encoding
  - Category encoding
  - Average cutoff
  - Cutoff standard deviation
  - Cutoff trend
  - Cutoff volatility
- Trains XGBoost regressor (currently not used in predictions)

#### C. **Chatbot Functions**
- `call_gemini_api()` - Calls Google Gemini for responses
- `get_fallback_response()` - Provides responses when Gemini is unavailable
- `get_chat_history()` / `save_to_chat_history()` - Manages conversation history

### 2. **User Data Manager (`user_data_manager.py`)**

Handles all database operations for user data:

- **`create_or_update_user()`** - Creates/updates user from Clerk
- **`save_marksheet_data()`** - Saves extracted marksheet data
- **`save_user_preferences()`** - Saves form preferences (CAP, branch, city, etc.)
- **`save_prediction_results()`** - Saves prediction results
- **`get_user_history()`** - Retrieves user's complete history

### 3. **Frontend Components**

#### **UploadPage.js**
- File upload interface with drag-and-drop
- Supports PDF, PNG, JPG, JPEG
- Integrates with Clerk for authentication
- Sends file to `/upload` endpoint
- Stores extracted data in localStorage

#### **FormPage.js**
- Displays extracted marksheet data
- Allows user to set preferences:
  - CAP Round (CAP1/CAP2)
  - Caste Category
  - Branch
  - City
  - State
- Submits to `/predict` endpoint
- Stores results in localStorage

#### **ResultsPage.js**
- Displays admission predictions in a table
- Features:
  - **Filtering**: By city and branch (with auto-apply)
  - **Sorting**: By admission chance, college name, code
  - **Export**: PDF and Excel formats
  - **Previous 5 years cutoffs**: Displayed in nested table
- Uses `/filter-results` endpoint for dynamic filtering

#### **Chatbot.js**
- Floating chatbot widget (available on all pages)
- Integrates with `/chat` endpoint
- Uses Gemini AI for responses
- Maintains conversation history

#### **Navbar.js**
- Navigation bar with links to all pages
- User authentication status display

---

## 🔄 Data Flow

### Complete User Journey Flow:

```
1. USER UPLOADS MARKSHEET
   └─> UploadPage.js
       └─> POST /upload (with file)
           └─> Backend: OCR Processing
               ├─> Extract text (Tesseract/PDF)
               ├─> Parse marksheet (regex)
               ├─> Save to user_data.marksheet_data (if authenticated)
               └─> Return: {name, exam_year, percentile, category}
           └─> Store in localStorage
           └─> Navigate to /form

2. USER SETS PREFERENCES
   └─> FormPage.js
       └─> Display extracted data
       └─> User selects: CAP, Branch, City, Category
       └─> POST /predict
           └─> Backend: Prediction Logic
               ├─> Query cutoff_db for city+CAP table
               ├─> Filter by branch & category
               ├─> For each college:
               │   ├─> Collect 5 years of cutoffs
               │   ├─> Calculate weighted cutoff
               │   └─> Calculate admission chance
               ├─> Save preferences & results (if authenticated)
               └─> Return: {results: [...]}
           └─> Store in localStorage
           └─> Navigate to /results

3. USER VIEWS & FILTERS RESULTS
   └─> ResultsPage.js
       └─> Load from localStorage
       └─> Display results table
       └─> User changes filters (city/branch)
           └─> POST /filter-results (auto-triggered)
               └─> Backend: Re-query with new filters
               └─> Update displayed results
       └─> User exports to PDF/Excel
```

### Database Query Flow:

```
cutoff_db Database Structure:
├── Tables: {city}_{cap} (e.g., nagpur_cap1, pune_cap2)
│   └── Columns: college_code, college_name, branch_name, 
│                branch_code, seat_type, percentile, year

Query Pattern:
1. Determine table: {city}_{cap}
2. Filter by: branch_name, seat_type, year
3. For each college:
   - Get percentile for previous year
   - Query 4 more years back
   - Calculate weighted average
   - Predict admission chance
```

---

## 🗄️ Database Schema

### Schema 1: `cutoff_db` (Historical Cutoff Data)

**Table Structure**: `{city}_{cap}` (e.g., `nagpur_cap1`, `pune_cap2`)

| Column | Type | Description |
|--------|------|-------------|
| college_code | VARCHAR | Unique college identifier |
| college_name | VARCHAR | Full college name |
| branch_name | VARCHAR | Engineering branch |
| branch_code | VARCHAR | Branch code |
| seat_type | VARCHAR | Caste category (GENERAL, OBC, etc.) |
| percentile | FLOAT | Cutoff percentile |
| year | INT | Year of cutoff data |

**Example Table**: `nagpur_cap1`
```
college_code | college_name    | branch_name | seat_type | percentile | year
VN01        | VNIT Nagpur     | CSE         | GENERAL   | 82.5       | 2024
VN01        | VNIT Nagpur     | CSE         | OBC       | 78.3       | 2024
CP02        | COEP Pune       | CSE         | GENERAL   | 84.2       | 2024
```

### Schema 2: `user_data` (User Information)

#### **users** table
- `id` (PK)
- `clerk_user_id` (UNIQUE) - Clerk authentication ID
- `email`
- `name`
- `created_at`, `last_login`

#### **marksheet_data** table
- `id` (PK)
- `user_id` (FK → users)
- `file_name`
- `extracted_name` - Student name from OCR
- `exam_year`
- `percentile`
- `category`
- `raw_text` - Full OCR text
- `created_at`

#### **user_preferences** table
- `id` (PK)
- `user_id` (FK → users)
- `marksheet_id` (FK → marksheet_data)
- `cap` - CAP1 or CAP2
- `caste_category`
- `branch`
- `city`
- `state`
- `created_at`

#### **prediction_results** table
- `id` (PK)
- `user_id` (FK → users)
- `marksheet_id` (FK → marksheet_data)
- `preferences_id` (FK → user_preferences)
- `exam_year`
- `user_score`
- `college_name`
- `college_code`
- `branch_name`
- `admission_chance`
- `created_at`

---

## 🌐 API Endpoints

### 1. **POST `/upload`**
Upload marksheet and extract data.

**Request**: Multipart form-data
```
file: <file>
clerk_user_id: <string> (optional)
email: <string> (optional)
name: <string> (optional)
```

**Response**:
```json
{
  "extracted_data": {
    "name": "John Doe",
    "exam_year": 2025,
    "percentile": 85.5,
    "category": "GENERAL"
  },
  "raw_text": "...",
  "user_id": 123,
  "marksheet_id": 456
}
```

### 2. **POST `/predict`**
Get admission predictions.

**Request**:
```json
{
  "exam_year": 2025,
  "score": 85.5,
  "cap": "CAP1",
  "city": "Nagpur",
  "branch": "Computer Science and Engineering",
  "caste_category": "GENERAL",
  "user_id": 123,
  "marksheet_id": 456
}
```

**Response**:
```json
{
  "results": [
    {
      "college_name": "VNIT Nagpur",
      "college_code": "VN01",
      "branch_name": "Computer Science and Engineering",
      "branch_code": "CS",
      "seat_type": "GENERAL",
      "previous_cutoffs": {
        "2024": 82.5,
        "2023": 80.2,
        "2022": 78.9,
        "2021": 76.5,
        "2020": 75.0
      },
      "admission_chance": 78.5
    }
  ]
}
```

### 3. **POST `/filter-results`**
Filter results by city and branch.

**Request**:
```json
{
  "exam_year": 2025,
  "score": 85.5,
  "cap": "CAP1",
  "city": "Pune",
  "branch": "Artificial Intelligence",
  "caste_category": "GENERAL"
}
```

**Response**: Same as `/predict`

### 4. **POST `/chat`**
AI chatbot endpoint.

**Request**:
```json
{
  "message": "What are the top colleges for CSE?",
  "session_id": "session_123"
}
```

**Response**:
```json
{
  "response": "Based on our database...",
  "type": "ai",
  "session_id": "session_123"
}
```

### 5. **GET `/dataset-info`**
Get dataset statistics for chatbot context.

**Response**:
```json
{
  "total_records": 5000,
  "unique_colleges": 150,
  "unique_branches": 30,
  "unique_categories": 5,
  "available_cities": ["Nagpur", "Pune", "Mumbai"],
  "available_years": [2020, 2021, 2022, 2023, 2024]
}
```

### 6. **GET `/user-history`**
Get user's prediction history.

**Request**: Query parameter `clerk_user_id`

**Response**:
```json
{
  "history": [
    {
      "marksheet_id": 456,
      "file_name": "marksheet.pdf",
      "exam_year": 2025,
      "percentile": 85.5,
      "cap": "CAP1",
      "branch": "CSE",
      "city": "Nagpur",
      "result_count": 25
    }
  ]
}
```

---

## ✨ Key Features

### 1. **Automatic Marksheet Processing**
- Supports PDF and image formats (PNG, JPG, JPEG)
- Uses OCR (Tesseract) for images
- Uses PyMuPDF for PDFs
- Extracts: Name, Year, Percentile, Category

### 2. **Smart Prediction Algorithm**
- **Weighted Cutoff Calculation**: Uses 5 years of data with time-weighted importance
- **Admission Chance Formula**:
  - If score ≥ threshold: `min(100, 70 + (score - threshold) * 0.5)`
  - If score < threshold: `max(0, 40 + (score - threshold) * 0.3)`
- **XGBoost Model**: Trained but currently not used (can be integrated)

### 3. **Advanced Filtering**
- Filter by city (Nagpur, Pune, Mumbai, etc.)
- Filter by branch (30+ engineering branches)
- Auto-applies filters when dropdowns change
- Real-time API calls for updated results

### 4. **Export Functionality**
- **PDF Export**: Landscape format with formatted table
- **Excel Export**: Structured spreadsheet with all data
- Includes: College name, code, branch, cutoffs, admission chance

### 5. **AI Chatbot**
- Powered by Google Gemini AI
- Context-aware responses
- Maintains conversation history
- Fallback responses when API unavailable
- Available on all pages

### 6. **User Authentication & History**
- Clerk integration for secure authentication
- Saves user data, preferences, and predictions
- View prediction history
- Personalized experience

### 7. **Responsive UI**
- Modern design with Tailwind CSS
- Mobile-friendly
- Smooth navigation with React Router
- Loading states and error handling

---

## 🤖 Machine Learning Integration

### Current State
- **XGBoost model is trained** but **not actively used** in predictions
- Model is trained on synthetic data with features:
  - Average cutoff
  - Cutoff standard deviation
  - Cutoff trend
  - Cutoff volatility
  - Branch encoding
  - Category encoding

### Prediction Logic (Current)
Uses rule-based calculation:
```python
if score >= threshold:
    admission_chance = min(100, 70 + (score - threshold) * 0.5)
else:
    admission_chance = max(0, 40 + (score - threshold) * 0.3)
```

### Potential ML Enhancement
The XGBoost model can be integrated to:
- Learn from historical admission patterns
- Consider multiple factors simultaneously
- Provide more accurate predictions
- Adapt to changing trends

**Integration Steps**:
1. Prepare features from current data
2. Use `model.predict()` instead of rule-based calculation
3. Adjust prediction based on user score vs threshold
4. Retrain periodically with new data

---

## 🚀 User Journey

### Step 1: Upload Marksheet
1. User visits homepage (`/`)
2. Drags & drops or selects marksheet file
3. System validates file (type, size)
4. If authenticated, file is uploaded
5. Backend processes with OCR
6. Extracted data displayed on form page

### Step 2: Set Preferences
1. User reviews extracted data
2. Selects preferences:
   - CAP Round (CAP1/CAP2)
   - Caste Category
   - Branch (from dropdown)
   - City (from dropdown)
   - State
3. Submits form
4. Backend queries database and calculates predictions
5. Results stored in localStorage
6. Navigate to results page

### Step 3: View & Filter Results
1. Results displayed in table format
2. Shows:
   - College name & code
   - Branch information
   - Previous 5 years cutoffs
   - Admission chance percentage
3. User can:
   - Filter by city/branch (auto-applies)
   - Sort by various columns
   - Export to PDF/Excel
   - Clear filters
4. Can navigate back to change preferences

### Step 4: Chatbot Assistance (Anytime)
1. User clicks chatbot icon (bottom-right)
2. Asks questions about:
   - College cutoffs
   - Admission process
   - Study tips
   - General guidance
3. AI responds with helpful information
4. Conversation history maintained

---

## 📊 Data Processing Pipeline

### OCR Pipeline:
```
File Upload
    ↓
[PDF?] → PyMuPDF → Extract Text
[Image?] → OpenCV Preprocessing → Tesseract OCR → Extract Text
    ↓
Regex Parsing
    ↓
Extract: Name, Year, Percentile, Category
    ↓
Return to Frontend
```

### Prediction Pipeline:
```
User Preferences
    ↓
Query Database: {city}_{cap} table
    ↓
Filter: branch_name, seat_type, year
    ↓
For Each College:
    ├─ Collect 5 years cutoffs
    ├─ Calculate weighted cutoff
    ├─ Compare with user score
    └─ Calculate admission chance
    ↓
Return Results Array
```

---

## 🔐 Security & Authentication

- **Clerk Authentication**: Secure user management
- **Session Management**: Flask sessions for chat history
- **CORS**: Configured for frontend-backend communication
- **File Validation**: Type and size checks
- **SQL Injection Prevention**: Parameterized queries
- **Environment Variables**: Sensitive data in `.env`

---

## 📝 Configuration Files

### Backend
- `requirements.txt` - Python dependencies
- `.env` - Environment variables (GEMINI_API_KEY, DB credentials)
- `app.py` - Main application
- `user_data_manager.py` - Database operations

### Frontend
- `package.json` - Node dependencies
- `tailwind.config.js` - Tailwind CSS configuration
- `App.js` - Main React component with routing

---

## 🎯 Future Enhancements

1. **Integrate XGBoost Model**: Use ML model for predictions
2. **Real-time Data Updates**: File watcher for automatic database updates
3. **More Cities/Branches**: Expand database coverage
4. **Comparison Tool**: Compare multiple colleges side-by-side
5. **Trend Analysis**: Visualize cutoff trends over years
6. **Recommendations**: AI-powered college recommendations
7. **Mobile App**: React Native version
8. **Email Notifications**: Alert users about cutoff updates

---

## 🐛 Known Issues & Limitations

1. **XGBoost Not Used**: Model trained but predictions use rule-based logic
2. **Synthetic Training Data**: Model trained on generated data, not real admissions
3. **Limited Cities**: Currently supports Nagpur, Pune, Mumbai, etc.
4. **No Real-time Updates**: Database updates require manual intervention
5. **OCR Accuracy**: Depends on marksheet quality and format

---

## 📚 Additional Resources

- **README.md** - Basic setup instructions
- **CHATBOT_SETUP.md** - Chatbot configuration guide
- **README_USER_DATA.md** - User data schema documentation
- **FILE_WATCHER_README.md** - File watcher setup guide

---

## 🏁 Conclusion

AdmitWise AI is a comprehensive admission prediction system that combines:
- **OCR technology** for automated data extraction
- **Historical data analysis** for accurate predictions
- **Machine learning** (ready for integration)
- **AI chatbot** for student guidance
- **User management** for personalized experience

The system is production-ready with room for ML model integration and feature enhancements.

