# File Watcher for AdmitWise AI

This module automatically monitors the `cutoffdata` folder for new Excel files and inserts the data into MySQL database.

## Features

- **Automatic File Detection**: Monitors the `cutoffdata` folder for new/modified Excel files
- **Database Integration**: Automatically creates tables and inserts data into MySQL
- **Weighted Threshold Support**: Integrates with the weighted threshold system
- **Error Handling**: Robust error handling and logging
- **Duplicate Prevention**: Prevents duplicate data insertion

## Setup

### 1. Install Dependencies

```powershell
pip install mysql-connector-python watchdog
```

### 2. Database Configuration

Update the database configuration in `file_watcher.py`:

```python
db_config = {
    "host": "localhost",
    "user": "root",
    "password": "Sudhir@567",  
    "database": "cutoff_db",
    "port": 3307   
}
```

### 3. Create Database

Create the MySQL database:

```sql
CREATE DATABASE cutoff_db;
```

## Usage

### Automatic Integration

The file watcher starts automatically when you run the main application:

```powershell
python app.py
```

### Manual Control

You can control the file watcher via API endpoints:

- **Start Watcher**: `POST /file-watcher/start`
- **Stop Watcher**: `POST /file-watcher/stop`
- **Check Status**: `GET /file-watcher/status`

### Testing

Run the test script:

```powershell
# Test the file watcher
python test_file_watcher.py

# Create a sample Excel file for testing
python test_file_watcher.py --create-sample
```

## File Format

Excel files should be named in the format: `City_CAPX.xlsx`

Example: `Nagpur_CAP1.xlsx`, `Mumbai_CAP2.xlsx`

### Excel Structure

Each sheet in the Excel file represents a year (e.g., "2024", "2023", "2022").

Required columns:
- `CollegeCode`: College code
- `CollegeName`: College name
- `BranchCode`: Branch code
- `BranchName`: Branch name
- `Stage`: CAP stage (e.g., "CAP1", "CAP2")
- `SeatType`: Seat type (e.g., "General", "OBC", "SC", "ST", "EWS")
- `Rank`: Student rank
- `Percentile`: Student percentile

## Database Schema

For each city, a table is created with the naming convention: `{city}_cutoff`

Example table structure:
```sql
CREATE TABLE nagpur_cutoff (
    id INT AUTO_INCREMENT PRIMARY KEY,
    college_code VARCHAR(50),
    college_name VARCHAR(255),
    branch_code VARCHAR(50),
    branch_name VARCHAR(255),
    stage VARCHAR(20),
    seat_type VARCHAR(50),
    `rank` INT,
    percentile DECIMAL(10,6),
    cap VARCHAR(50),
    year YEAR,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);
```

## Weighted Threshold Integration

The file watcher integrates with the weighted threshold system:

- **2021**: Uses 2020 data (100%)
- **2022**: Uses 2021 (65%) + 2020 (35%)
- **2023**: Uses 2022 (60%) + 2021 (25%) + 2020 (15%)
- **2024**: Uses 2023 (60%) + 2022 (25%) + 2021 (10%) + 2020 (5%)
- **2025**: Uses 2024 (60%) + 2023 (25%) + 2022 (10%) + 2021 (5%) + 2020 (5%)

## Logging

The file watcher provides detailed logging:

- File detection events
- Database operations
- Error messages
- Processing status

## Error Handling

- **Database Connection**: Graceful handling of connection failures
- **File Processing**: Continues processing other files if one fails
- **Duplicate Data**: Prevents duplicate entries for the same year/CAP
- **Invalid Files**: Skips files with incorrect format or naming

## Monitoring

The file watcher runs in the background and can be monitored through:

1. **Console Logs**: Real-time status updates
2. **API Endpoints**: Programmatic status checking
3. **Database**: Direct database queries to verify data insertion

## Troubleshooting

### Common Issues

1. **Database Connection Failed**
   - Check MySQL server is running
   - Verify database credentials
   - Ensure database exists

2. **File Not Processed**
   - Check file naming convention
   - Verify Excel file format
   - Check file permissions

3. **Data Not Inserted**
   - Check database table exists
   - Verify column names match expected format
   - Check for data validation errors

### Debug Mode

Enable debug logging by modifying the logging level in `file_watcher.py`:

```python
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
```
