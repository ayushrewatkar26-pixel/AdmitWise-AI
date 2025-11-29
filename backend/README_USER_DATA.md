# User Data Storage Implementation

This implementation adds user data storage to AdmitWise AI using a new MySQL schema called `user_data`.

## What's Stored

### 1. User Information (from Clerk)
- Clerk User ID
- Email
- Name
- Created/Last login timestamps

### 2. Extracted Marksheet Data (from Form Page)
- File name
- **Extracted Name** (from marksheet)
- **Exam Year** (from marksheet)
- **Percentile** (from marksheet)
- **Category** (from marksheet)
- Raw OCR text

### 3. User Preferences (from Form)
- CAP selection
- Caste category
- Branch preference
- City preference
- State preference

### 4. Prediction Results
- College predictions with admission chances
- Linked to user and preferences

## Database Schema

### New Schema: `user_data`

```sql
-- Users table (linked to Clerk)
users (id, clerk_user_id, email, name, created_at, last_login)

-- Marksheet data (extracted form data)
marksheet_data (id, user_id, file_name, extracted_name, exam_year, percentile, category, raw_text, created_at)

-- User preferences (form selections)
user_preferences (id, user_id, marksheet_id, cap, caste_category, branch, city, state, created_at)

-- Prediction results
prediction_results (id, user_id, marksheet_id, preferences_id, exam_year, user_score, college_name, college_code, branch_name, admission_chance, created_at)
```

## Setup Instructions

### 1. Create Database Schema
```bash
cd backend
python setup_user_database.py
```

### 2. Update Database Password
Edit `user_data_manager.py` and `setup_user_database.py`:
```python
"password": "YOUR_MYSQL_PASSWORD"
```

### 3. Test Connection
```bash
python user_data_manager.py
```

## How It Works

### 1. File Upload
- Frontend sends user data (Clerk ID, email, name) with file
- Backend creates/updates user record
- Saves extracted marksheet data
- Returns marksheet_id and user_id

### 2. Form Submission
- Frontend sends preferences with user_id and marksheet_id
- Backend saves preferences
- Generates predictions
- Saves all prediction results

### 3. Data Flow
```
Upload File → Extract Data → Save to marksheet_data
     ↓
Form Preferences → Save to user_preferences
     ↓
Generate Predictions → Save to prediction_results
```

## API Endpoints

### New Endpoints
- `GET /user-history?clerk_user_id=xxx` - Get user's complete history

### Updated Endpoints
- `POST /upload` - Now saves user and marksheet data
- `POST /predict` - Now saves preferences and results

## Benefits

1. **Persistent Data**: User data survives browser sessions
2. **User History**: Track all uploads and predictions
3. **Analytics**: Analyze user behavior and preferences
4. **Security**: Data stored securely in database
5. **Scalability**: Supports multiple users

## Data Privacy

- Only stores data shown on the form page
- Raw OCR text stored for reference
- User can access their complete history
- Data linked to Clerk authentication

## Testing

### Test User Data Storage
1. Sign in with Clerk
2. Upload a marksheet
3. Fill form preferences
4. Get predictions
5. Check database for saved data

### View User History
```bash
curl "http://localhost:5000/user-history?clerk_user_id=YOUR_CLERK_ID"
```

## Troubleshooting

### Database Connection Issues
- Check MySQL is running
- Verify password in config files
- Ensure user has CREATE privileges

### Missing Data
- Check if user is signed in
- Verify Clerk user data is being sent
- Check backend logs for errors

### Schema Issues
- Run `setup_user_database.py` again
- Check MySQL error logs
- Verify table creation
