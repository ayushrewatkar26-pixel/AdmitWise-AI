# AdmitWise AI - Backend

A Flask-based REST API backend for the CET Admission Predictor system. This backend handles marksheet processing using OCR, machine learning-based admission predictions, user data management, and AI-powered chatbot functionality.

## 🚀 Features

- **OCR Processing**: Extract student data from CET marksheets (PDF/Images) using Tesseract OCR
- **ML Predictions**: XGBoost-based admission chance predictions using historical cutoff data
- **Database Integration**: MySQL database for storing cutoff data and user information
- **User Data Management**: Persistent storage of user uploads, preferences, and prediction history
- **AI Chatbot**: Gemini AI-powered chatbot for answering admission queries
- **File Watching**: Automatic processing of new cutoff data files
- **RESTful API**: Clean API endpoints for frontend integration
- **CORS Support**: Cross-origin resource sharing enabled for frontend communication

## 🛠️ Tech Stack

### Web Framework
- **Flask 2.3.0+**: Lightweight Python web framework
- **Flask-CORS 4.0.0+**: Cross-origin resource sharing support
- **Werkzeug 2.3.0+**: WSGI utilities

### Machine Learning
- **XGBoost 1.7.0+**: Gradient boosting framework for predictions
- **scikit-learn 1.3.0+**: Machine learning utilities and preprocessing
- **NumPy 1.24.0+**: Numerical computing
- **Pandas 2.0.0+**: Data manipulation and analysis

### Computer Vision & OCR
- **OpenCV 4.8.0+**: Image processing
- **pytesseract 0.3.10+**: Python wrapper for Tesseract OCR
- **Pillow 10.0.0+**: Image manipulation

### Document Processing
- **PyMuPDF 1.23.0+**: PDF text extraction

### Database
- **mysql-connector-python 8.1.0+**: MySQL database connector

### AI & Chatbot
- **google-generativeai 0.3.0+**: Google Gemini AI integration

### Utilities
- **python-dotenv 1.0.0+**: Environment variable management
- **watchdog 3.0.0+**: File system monitoring
- **openpyxl 3.1.0+**: Excel file processing

## 📋 Prerequisites

- **Python**: Version 3.8 or higher
- **MySQL**: Version 5.7 or higher (for database)
- **Tesseract OCR**: Must be installed on the system
  - **Windows**: Download from [GitHub](https://github.com/UB-Mannheim/tesseract/wiki)
  - **macOS**: `brew install tesseract`
  - **Ubuntu/Debian**: `sudo apt-get install tesseract-ocr`
  - **Fedora**: `sudo dnf install tesseract`

## 🔧 Installation

### 1. Navigate to Backend Directory
```bash
cd backend
```

### 2. Create Virtual Environment (Recommended)
```bash
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Set Up Environment Variables
Create a `.env` file in the backend directory:
```env
FLASK_SECRET_KEY=your_secret_key_here
GEMINI_API_KEY=your_gemini_api_key_here

# Database Configuration (optional, defaults shown)
DB_HOST=localhost
DB_USER=root
DB_PASSWORD=your_password
DB_NAME=cutoff_db
DB_PORT=3306
```

### 5. Set Up Database
```bash
# Create database schema
python setup_user_database.py

# Or manually run SQL script
mysql -u root -p < create_user_schema.sql
```

### 6. Configure Tesseract Path (if needed)
If Tesseract is not in your system PATH, set it in `app.py`:
```python
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'  # Windows
# or
pytesseract.pytesseract.tesseract_cmd = '/usr/bin/tesseract'  # Linux/Mac
```

## 🚀 Running the Application

### Development Mode
```bash
python app.py
```

The server will start on `http://localhost:5000`

### Production Mode
```bash
# Using Gunicorn (install: pip install gunicorn)
gunicorn -w 4 -b 0.0.0.0:5000 app:app

# Using Waitress (Windows-friendly, install: pip install waitress)
waitress-serve --host=0.0.0.0 --port=5000 app:app
```

## 📁 Project Structure

```
backend/
├── app.py                      # Main Flask application
├── user_data_manager.py        # User data management utilities
├── file_watcher.py            # File watching service
├── setup_user_database.py     # Database setup script
├── create_user_schema.sql     # SQL schema for user data
├── requirements.txt           # Python dependencies
├── cutoffdata/                # Excel files with cutoff data
│   └── Nagpur_CAP1.xlsx
├── uploads/                   # Temporary upload storage (gitignored)
├── test_*.py                  # Test files
├── check_database.py          # Database verification script
├── view_data.py               # Data viewing utilities
├── README.md                  # This file
├── README_USER_DATA.md        # User data system documentation
└── FILE_WATCHER_README.md     # File watcher documentation
```

## 🔌 API Endpoints

### File Upload & OCR

#### POST /upload
Upload CET marksheet and extract student details using OCR.

**Request:**
- Method: `POST`
- Content-Type: `multipart/form-data`
- Body:
  - `file`: PDF, PNG, or JPG file
  - `clerk_user_id`: (optional) Clerk user ID
  - `email`: (optional) User email
  - `name`: (optional) User name

**Response:**
```json
{
  "extracted_data": {
    "name": "Student Name",
    "exam_year": 2025,
    "score": 85.5,
    "caste_category": "OBC",
    "marksheet_id": 123,
    "user_id": 456
  },
  "raw_text": "Full OCR extracted text..."
}
```

### Predictions

#### POST /predict
Get admission predictions based on student data and preferences.

**Request:**
```json
{
  "exam_year": 2025,
  "score": 85.5,
  "cap": "CAP1",
  "city": "Nagpur",
  "branch": "CSE",
  "category": "OBC",
  "user_id": 456,
  "marksheet_id": 123
}
```

**Response:**
```json
{
  "exam_year": 2025,
  "user_score": 85.5,
  "results": [
    {
      "college_name": "VNIT Nagpur",
      "college_code": "VN01",
      "branch": "CSE",
      "caste_category": "OBC",
      "previous_year_cutoffs": "82, 80, 78, 76, 75",
      "user_score": 85.5,
      "admission_chance": 78.5
    }
  ],
  "available": {
    "branches": ["CSE", "ECE", "ME"],
    "categories": ["GENERAL", "OBC", "SC", "ST"]
  }
}
```

### College Data

#### GET /colleges
Get available colleges, branches, cities, and categories.

**Response:**
```json
{
  "colleges": ["VNIT Nagpur", "COEP Pune", ...],
  "branches": ["CSE", "ECE", "ME", ...],
  "cities": ["Nagpur", "Pune", "Mumbai", ...],
  "categories": ["GENERAL", "OBC", "SC", "ST"]
}
```

### AI Chatbot

#### POST /chat
Chat with AI-powered chatbot about admissions.

**Request:**
```json
{
  "message": "What is the cutoff for CSE in Nagpur?",
  "session_id": "user_session_123"
}
```

**Response:**
```json
{
  "response": "Based on the available data...",
  "type": "ai",
  "session_id": "user_session_123"
}
```

### User History

#### GET /user-history
Get complete user history (uploads, preferences, predictions).

**Query Parameters:**
- `clerk_user_id`: Clerk user ID

**Response:**
```json
{
  "user_id": 456,
  "email": "user@example.com",
  "name": "User Name",
  "marksheets": [...],
  "preferences": [...],
  "predictions": [...]
}
```

### Dataset Information

#### GET /dataset-info
Get metadata about the cutoff dataset.

**Response:**
```json
{
  "total_colleges": 150,
  "total_branches": 20,
  "cities": ["Nagpur", "Pune", ...],
  "years_covered": [2020, 2021, 2022, 2023, 2024]
}
```

## 🗄️ Database Schema

### Cutoff Data Tables
Tables are dynamically created based on city and CAP (e.g., `nagpur_cap1`, `pune_cap2`).

**Structure:**
- `college_code`: College identifier
- `college_name`: Full college name
- `branch_name`: Branch name (CSE, ECE, etc.)
- `branch_code`: Branch identifier
- `seat_type`: Category (GENERAL, OBC, SC, ST)
- `percentile`: Cutoff percentile
- `year`: Academic year

### User Data Tables
See `README_USER_DATA.md` for detailed schema information.

## 🤖 Machine Learning Model

### XGBoost Prediction Model
The system uses XGBoost for admission chance predictions based on:
- Average cutoff over 5 years
- Cutoff standard deviation
- Cutoff trend (recent vs historical)
- State, city, branch, and category encodings

### Features Used
1. **Historical Data**: 5 years of cutoff data
2. **Statistical Features**: Mean, std deviation, trends
3. **Categorical Encodings**: Label encoding for categories
4. **User Score**: Current student's score

## 📊 Data Processing

### OCR Workflow
1. File uploaded (PDF or Image)
2. PDF → Text extraction (PyMuPDF)
3. Image → OCR processing (Tesseract)
4. Text parsing using regex patterns
5. Data extraction (name, score, category, year)

### Prediction Workflow
1. Load cutoff data from MySQL
2. Filter by city, branch, category
3. Calculate statistical features
4. Apply XGBoost model
5. Return predictions with admission chances

## 🔐 Security Considerations

### Environment Variables
- Never commit `.env` files
- Use strong `FLASK_SECRET_KEY` in production
- Keep `GEMINI_API_KEY` secure
- Use environment-specific configurations

### Database Security
- Use strong database passwords
- Limit database user privileges
- Enable SSL for production connections
- Regular database backups

### File Upload Security
- Validate file types and sizes
- Sanitize filenames
- Delete temporary files after processing
- Scan uploaded files for malware (in production)

## 🧪 Testing

### Run Tests
```bash
# Test prediction API
python test_prediction.py

# Test database connection
python test_db.py

# Test file watcher
python test_file_watcher.py

# Test enhanced calculations
python test_enhanced_calculation.py
```

### Manual Testing
```bash
# Check database setup
python check_database.py

# View stored data
python view_data.py
```

## 📝 Configuration

### Flask Configuration
- `SECRET_KEY`: Session encryption key
- `UPLOAD_FOLDER`: Directory for temporary uploads
- `MAX_CONTENT_LENGTH`: Maximum file size (default: 16MB)

### CORS Configuration
CORS is enabled for all origins in development. For production:
```python
CORS(app, resources={
    r"/api/*": {
        "origins": ["https://yourdomain.com"],
        "methods": ["GET", "POST"],
        "allow_headers": ["Content-Type"]
    }
})
```

## 🐛 Troubleshooting

### Tesseract Not Found
```bash
# Check if Tesseract is installed
tesseract --version

# Set path in app.py if needed
pytesseract.pytesseract.tesseract_cmd = '/path/to/tesseract'
```

### Database Connection Issues
- Verify MySQL is running: `mysql -u root -p`
- Check database credentials in `.env`
- Ensure database exists: `CREATE DATABASE cutoff_db;`
- Verify user has proper permissions

### OCR Extraction Issues
- Ensure image quality is good
- Check if Tesseract language packs are installed
- Verify file format is supported
- Check logs for OCR errors

### API Errors
- Check Flask logs for detailed error messages
- Verify all dependencies are installed
- Ensure environment variables are set
- Check CORS configuration if frontend can't connect

## 📦 Dependencies

See `requirements.txt` for complete list. Key dependencies:

- **Flask**: Web framework
- **XGBoost**: ML predictions
- **pytesseract**: OCR processing
- **mysql-connector-python**: Database
- **google-generativeai**: AI chatbot
- **pandas/numpy**: Data processing

## 🔄 Updates & Maintenance

### Updating Dependencies
```bash
pip install --upgrade -r requirements.txt
```

### Database Migrations
- Backup database before schema changes
- Test migrations on development first
- Document all schema changes

### Monitoring
- Set up logging for production
- Monitor API response times
- Track error rates
- Monitor database performance

## 📄 Additional Documentation

- **README_USER_DATA.md**: User data management system
- **FILE_WATCHER_README.md**: File watching service documentation
- **Main README.md**: Overall project documentation

## 📞 Support

For issues or questions:
- Check the main project README
- Review API endpoint documentation
- Check database connection and setup
- Open an issue in the repository

## 🔒 Production Deployment Checklist

- [ ] Set strong `FLASK_SECRET_KEY`
- [ ] Configure production database
- [ ] Set up proper CORS origins
- [ ] Enable HTTPS
- [ ] Set up logging
- [ ] Configure file upload limits
- [ ] Set up monitoring
- [ ] Enable rate limiting
- [ ] Set up backups
- [ ] Configure environment variables securely

---

**Note**: This backend requires MySQL database and Tesseract OCR to be installed. Ensure all prerequisites are met before running the application.

