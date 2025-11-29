# AdmitWise AI - Frontend

A modern React-based frontend application for the CET Admission Predictor system. This application provides an intuitive user interface for uploading marksheets, configuring preferences, and viewing admission predictions with advanced filtering and export capabilities.

## 🚀 Features

- **File Upload Interface**: Drag-and-drop or click to upload CET marksheets (PDF, PNG, JPG)
- **Form-Based Configuration**: Easy-to-use form for setting preferences (branch, city, category)
- **Results Display**: Comprehensive table showing college-wise admission chances
- **Advanced Filtering**: Filter results by city, branch, and minimum admission chance percentage
- **Export Functionality**: Export results to PDF or Excel format
- **AI Chatbot**: Integrated chatbot for answering admission-related queries
- **Responsive Design**: Modern UI built with Tailwind CSS, fully responsive
- **User Authentication**: Clerk-based authentication for user data persistence

## 🛠️ Tech Stack

### Core Framework
- **React 18.2.0**: Modern React with hooks
- **React Router DOM 6.8.1**: Client-side routing
- **React Scripts 5.0.1**: Build tooling and development server

### UI & Styling
- **Tailwind CSS 3.2.7**: Utility-first CSS framework
- **PostCSS & Autoprefixer**: CSS processing

### HTTP & API
- **Axios 1.3.4**: HTTP client for API communication
- **Proxy Configuration**: Automatic proxy to backend (localhost:5000)

### File Handling
- **React Dropzone 14.2.3**: File upload with drag-and-drop support
- **jsPDF 2.5.1**: PDF generation for exporting results
- **XLSX 0.18.5**: Excel file generation

### Authentication
- **@clerk/clerk-react 5.48.1**: User authentication and management

### Data Display
- **React Table 7.8.0**: Advanced table component for results display

## 📋 Prerequisites

- **Node.js**: Version 16.0 or higher
- **npm**: Comes with Node.js
- **Backend Server**: The backend API should be running on `http://localhost:5000`

## 🔧 Installation

### 1. Navigate to Frontend Directory
```bash
cd frontend
```

### 2. Install Dependencies
```bash
npm install
```

This will install all required packages listed in `package.json`.

## 🚀 Running the Application

### Development Mode
```bash
npm start
```

The application will start on `http://localhost:3000` and automatically open in your browser.

### Build for Production
```bash
npm build
```

This creates an optimized production build in the `build/` folder.

### Run Tests
```bash
npm test
```

## 📁 Project Structure

```
frontend/
├── public/
│   ├── index.html          # Main HTML template
│   └── favicon.svg         # Application favicon
├── src/
│   ├── components/
│   │   ├── UploadPage.js   # File upload interface
│   │   ├── FormPage.js     # Preferences form
│   │   ├── ResultsPage.js  # Results display with filters
│   │   ├── Navbar.js       # Navigation bar
│   │   └── Chatbot.js      # AI chatbot component
│   ├── App.js              # Main app component with routing
│   ├── index.js            # Application entry point
│   └── index.css           # Global styles
├── package.json            # Dependencies and scripts
├── tailwind.config.js      # Tailwind CSS configuration
├── postcss.config.js       # PostCSS configuration
└── README.md               # This file
```

## 🔌 API Integration

The frontend communicates with the backend API through the following endpoints:

### Upload Marksheet
```javascript
POST /upload
Content-Type: multipart/form-data
Body: { file: File, clerk_user_id: string, email: string, name: string }
Response: { extracted_data: {...}, raw_text: string }
```

### Get Predictions
```javascript
POST /predict
Content-Type: application/json
Body: {
  exam_year: number,
  score: number,
  cap: string,
  city: string,
  branch: string,
  category: string,
  user_id: number,
  marksheet_id: number
}
Response: { results: [...], exam_year: number, user_score: number }
```

### Get Colleges Data
```javascript
GET /colleges
Response: { colleges: [...], branches: [...], cities: [...] }
```

### Chat with AI
```javascript
POST /chat
Content-Type: application/json
Body: { message: string, session_id: string }
Response: { response: string, type: string, session_id: string }
```

## 🎨 Component Details

### UploadPage
- Handles file upload via drag-and-drop or file picker
- Validates file type (PDF, PNG, JPG) and size (max 16MB)
- Extracts student data using OCR via backend
- Navigates to FormPage with extracted data

### FormPage
- Displays extracted student information
- Allows editing of exam details (year, score, category)
- Provides dropdowns for branch, city, and CAP selection
- Submits preferences to backend for prediction

### ResultsPage
- Displays prediction results in a sortable table
- Provides filters for city, branch, and minimum admission chance
- Supports exporting results to PDF or Excel
- Shows detailed cutoff information for each college

### Chatbot
- Floating chatbot component available on all pages
- Integrates with Gemini AI via backend
- Maintains conversation history
- Provides context-aware responses about admissions

### Navbar
- Navigation between pages
- User authentication status
- Responsive mobile menu

## 🔐 Environment Variables

Create a `.env` file in the frontend directory (if needed):

```env
REACT_APP_API_URL=http://localhost:5000
REACT_APP_CLERK_PUBLISHABLE_KEY=your_clerk_key_here
```

Note: The application uses a proxy configuration in `package.json` for development, so API calls are automatically forwarded to the backend.

## 🎯 Key Features Implementation

### File Upload
- Uses `react-dropzone` for drag-and-drop functionality
- Validates file types and sizes before upload
- Shows upload progress and error messages
- Handles both PDF and image files

### Data Export
- **PDF Export**: Uses `jsPDF` to generate formatted PDF documents
- **Excel Export**: Uses `XLSX` to create Excel spreadsheets
- Includes all filtered results with proper formatting

### Filtering
- Real-time filtering without page reload
- Multiple filter criteria (city, branch, admission chance)
- Maintains filter state during navigation

### Responsive Design
- Mobile-first approach with Tailwind CSS
- Breakpoints for tablet and desktop views
- Touch-friendly interface elements

## 🐛 Troubleshooting

### Port Already in Use
If port 3000 is already in use:
```bash
# Windows
set PORT=3001 && npm start

# Linux/Mac
PORT=3001 npm start
```

### API Connection Issues
- Ensure backend is running on `http://localhost:5000`
- Check CORS configuration in backend
- Verify proxy settings in `package.json`

### Build Errors
- Clear `node_modules` and reinstall: `rm -rf node_modules && npm install`
- Clear npm cache: `npm cache clean --force`
- Delete `package-lock.json` and reinstall

### Authentication Issues
- Verify Clerk keys are correctly configured
- Check browser console for authentication errors
- Ensure backend accepts Clerk user IDs

## 📝 Development Guidelines

### Code Style
- Use functional components with hooks
- Follow React best practices
- Use meaningful component and variable names
- Add comments for complex logic

### State Management
- Use React hooks (`useState`, `useEffect`) for local state
- Pass data via props or React Router state
- Consider context API for global state if needed

### Performance
- Use React.memo for expensive components
- Implement lazy loading for large components
- Optimize images and assets
- Minimize re-renders with proper dependency arrays

## 🧪 Testing

The project includes testing setup with:
- **@testing-library/react**: Component testing utilities
- **@testing-library/jest-dom**: DOM matchers
- **@testing-library/user-event**: User interaction simulation

Run tests with:
```bash
npm test
```

## 📦 Dependencies

See `package.json` for the complete list of dependencies. Key dependencies include:

- `react` & `react-dom`: Core React library
- `react-router-dom`: Routing
- `axios`: HTTP client
- `tailwindcss`: Styling
- `react-dropzone`: File uploads
- `jspdf` & `xlsx`: Export functionality
- `@clerk/clerk-react`: Authentication

## 🔄 Updates & Maintenance

### Updating Dependencies
```bash
npm update
```

### Checking for Outdated Packages
```bash
npm outdated
```

### Security Audits
```bash
npm audit
npm audit fix
```

## 📄 License

This project is part of the AdmitWise AI system. See the main repository README for license information.

## 🤝 Contributing

1. Follow the existing code style
2. Test your changes thoroughly
3. Update documentation if needed
4. Submit pull requests with clear descriptions

## 📞 Support

For issues or questions:
- Check the main project README
- Review backend API documentation
- Open an issue in the repository

---

**Note**: This frontend requires the backend API to be running. See the backend README for backend setup instructions.

