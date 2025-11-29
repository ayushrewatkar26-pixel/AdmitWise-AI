# CET Admission Predictor

A full-stack web application that predicts admission chances into engineering colleges based on CET scores using machine learning and historical cutoff data.

## Features

- **Automatic Marksheet Processing**: Upload CET marksheet (PDF/Image) and automatically extract student details using OCR
- **Smart Prediction**: Uses XGBoost ML model with 5 years of historical cutoff data
- **Comprehensive Results**: View college-wise admission chances with detailed cutoff information
- **Advanced Filtering**: Filter results by city, branch, and minimum admission chance
- **Export Options**: Export results to PDF or Excel format
- **Modern UI**: Built with React and Tailwind CSS for a beautiful user experience

## Tech Stack

### Backend
- **Python Flask**: Web framework
- **XGBoost**: Machine learning model for admission prediction
- **OpenCV & Tesseract**: OCR for marksheet processing
- **Pandas & NumPy**: Data processing
- **PyMuPDF**: PDF text extraction

### Frontend
- **React**: Frontend framework
- **Tailwind CSS**: Styling
- **React Router**: Navigation
- **Axios**: API communication
- **React Dropzone**: File upload
- **jsPDF & XLSX**: Export functionality

## Installation

### Prerequisites
- Python 3.8+
- Node.js 16+
- Tesseract OCR

### Quick Start (Recommended)

1. **Install all dependencies:**
```bash
npm run setup
```

2. **Start both backend and frontend:**
```bash
npm start
```

The application will be available at:
- **Frontend**: `http://localhost:3000`
- **Backend**: `http://localhost:5000`

### Individual Setup

#### Backend Only
```bash
npm run backend
```

#### Frontend Only
```bash
npm run frontend
```

#### Install Dependencies Only
```bash
# Install all dependencies
npm run install-all

# Install backend dependencies only
npm run install-backend

# Install frontend dependencies only
npm run install-frontend
```

### Manual Setup (Alternative)

#### Backend Setup
1. Navigate to backend directory:
```bash
cd backend
```

2. Create virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Install Tesseract OCR:
   - **Windows**: Download from [GitHub](https://github.com/UB-Mannheim/tesseract/wiki)
   - **macOS**: `brew install tesseract`
   - **Ubuntu**: `sudo apt-get install tesseract-ocr`

#### Frontend Setup
1. Navigate to frontend directory:
```bash
cd frontend
```

2. Install dependencies:
```bash
npm install
```

## Usage

1. **Upload Marksheet**: Go to the upload page and upload your CET marksheet (PDF, PNG, or JPG)
2. **Review Details**: The system will automatically extract your name, score, and category
3. **Set Preferences**: Choose your preferred state, branch, and city
4. **View Results**: Get a comprehensive list of colleges with admission chances
5. **Filter & Export**: Use filters to narrow down results and export to PDF/Excel

## API Endpoints

### POST /upload
Upload CET marksheet and extract student details.

**Request**: Multipart form data with file
**Response**: 
```json
{
  "name": "Student Name",
  "exam_year": 2025,
  "score": 85,
  "caste_category": "OBC"
}
```

### POST /predict
Get admission predictions based on student data and preferences.

**Request**:
```json
{
  "exam_year": 2025,
  "score": 85,
  "caste_category": "OBC",
  "branch": "CSE",
  "city": "Nagpur",
  "state": "Maharashtra"
}
```

**Response**:
```json
{
  "exam_year": 2025,
  "user_score": 85,
  "results": [
    {
      "college_name": "VNIT Nagpur",
      "college_code": "VN01",
      "branch": "CSE",
      "caste_category": "OBC",
      "previous_year_cutoffs": "82, 80, 78, 76, 75",
      "user_score": 85,
      "admission_chance": 78.5
    }
  ]
}
```

### GET /colleges
Get available colleges, branches, and locations.

## Dataset Format

The system uses a comprehensive dataset with the following structure:

| College Name | Code | State | City | Branch | Caste Category | 2024 Cutoff | 2023 Cutoff | 2022 Cutoff | 2021 Cutoff | 2020 Cutoff |
|--------------|------|-------|------|--------|----------------|-------------|-------------|-------------|-------------|-------------|
| VNIT Nagpur  | VN01 | MH    | Nagpur | CSE   | OBC           | 82          | 80          | 78          | 76          | 75          |

## Machine Learning Model

The XGBoost model uses the following features:
- Average cutoff over 5 years
- Cutoff standard deviation
- Cutoff trend (recent vs historical)
- State, city, branch, and category encodings

The model is trained on simulated admission data and provides weighted predictions considering recent year trends.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

This project is licensed under the MIT License.

## Support

For support or questions, please open an issue in the repository.
