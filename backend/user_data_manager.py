#!/usr/bin/env python3
"""
User Data Manager for AdmitWise AI
Handles user data storage in the user_data schema
"""

import mysql.connector
from datetime import datetime
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Database configuration for user_data schema
USER_DB_CONFIG = {
    "host": "localhost",
    "user": "root",
    "password": "Sudhir@567",  # Update with your password
    "database": "user_data",
    "port": 3306
}

def get_user_db_connection():
    """Get connection to user_data database"""
    return mysql.connector.connect(**USER_DB_CONFIG)

class UserDataManager:
    def __init__(self):
        self.db_config = USER_DB_CONFIG
    
    def create_or_update_user(self, clerk_user_id, email, name):
        """Create or update user record from Clerk data"""
        try:
            conn = get_user_db_connection()
            cursor = conn.cursor()
            
            # Insert or update user
            query = """
                INSERT INTO users (clerk_user_id, email, name, last_login) 
                VALUES (%s, %s, %s, NOW())
                ON DUPLICATE KEY UPDATE 
                email = VALUES(email), 
                name = VALUES(name), 
                last_login = NOW()
            """
            
            cursor.execute(query, (clerk_user_id, email, name))
            
            # Get user ID
            if cursor.lastrowid == 0:
                # User already exists, get their ID
                cursor.execute("SELECT id FROM users WHERE clerk_user_id = %s", (clerk_user_id,))
                user_id = cursor.fetchone()[0]
            else:
                user_id = cursor.lastrowid
            
            conn.commit()
            conn.close()
            
            logger.info(f"✅ User created/updated: {clerk_user_id} (ID: {user_id})")
            return user_id
            
        except Exception as e:
            logger.error(f"❌ Error creating/updating user: {e}")
            return None
    
    def save_marksheet_data(self, user_id, file_name, extracted_data, raw_text):
        """Save extracted marksheet data (what shows on form page)"""
        try:
            conn = get_user_db_connection()
            cursor = conn.cursor()
            
            query = """
                INSERT INTO marksheet_data 
                (user_id, file_name, extracted_name, exam_year, percentile, category, raw_text)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """
            
            values = (
                user_id,
                file_name,
                extracted_data.get('name', 'Unknown'),
                extracted_data.get('year'),
                extracted_data.get('percentile'),
                extracted_data.get('category', 'GENERAL'),
                raw_text
            )
            
            cursor.execute(query, values)
            marksheet_id = cursor.lastrowid
            
            conn.commit()
            conn.close()
            
            logger.info(f"✅ Marksheet data saved for user {user_id} (marksheet_id: {marksheet_id})")
            return marksheet_id
            
        except Exception as e:
            logger.error(f"❌ Error saving marksheet data: {e}")
            return None
    
    def save_user_preferences(self, user_id, marksheet_id, preferences):
        """Save user form preferences"""
        try:
            conn = get_user_db_connection()
            cursor = conn.cursor()
            
            query = """
                INSERT INTO user_preferences 
                (user_id, marksheet_id, cap, caste_category, branch, city, state)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """
            
            values = (
                user_id,
                marksheet_id,
                preferences.get('cap'),
                preferences.get('caste_category'),
                preferences.get('branch'),
                preferences.get('city'),
                preferences.get('state')
            )
            
            cursor.execute(query, values)
            preferences_id = cursor.lastrowid
            
            conn.commit()
            conn.close()
            
            logger.info(f"✅ Preferences saved for user {user_id} (preferences_id: {preferences_id})")
            return preferences_id
            
        except Exception as e:
            logger.error(f"❌ Error saving preferences: {e}")
            return None
    
    def save_prediction_results(self, user_id, marksheet_id, preferences_id, results_data):
        """Save prediction results"""
        try:
            conn = get_user_db_connection()
            cursor = conn.cursor()
            
            # Clear previous results for this user/preferences combination
            cursor.execute("""
                DELETE FROM prediction_results 
                WHERE user_id = %s AND preferences_id = %s
            """, (user_id, preferences_id))
            
            # Insert new results
            query = """
                INSERT INTO prediction_results 
                (user_id, marksheet_id, preferences_id, exam_year, user_score, 
                 college_name, college_code, branch_name, admission_chance)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            """
            
            for result in results_data:
                values = (
                    user_id,
                    marksheet_id,
                    preferences_id,
                    result.get('exam_year'),
                    result.get('user_score'),
                    result.get('college_name'),
                    result.get('college_code'),
                    result.get('branch_name'),
                    result.get('admission_chance')
                )
                cursor.execute(query, values)
            
            conn.commit()
            conn.close()
            
            logger.info(f"✅ Prediction results saved for user {user_id}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error saving prediction results: {e}")
            return False
    
    def get_user_history(self, clerk_user_id):
        """Get user's complete history"""
        try:
            conn = get_user_db_connection()
            cursor = conn.cursor(dictionary=True)
            
            # Get user's marksheets with preferences and results
            query = """
                SELECT 
                    m.id as marksheet_id,
                    m.file_name,
                    m.extracted_name,
                    m.exam_year,
                    m.percentile,
                    m.category,
                    m.created_at as marksheet_date,
                    p.cap,
                    p.caste_category,
                    p.branch,
                    p.city,
                    p.state,
                    p.created_at as preferences_date,
                    COUNT(pr.id) as result_count
                FROM marksheet_data m
                LEFT JOIN user_preferences p ON m.id = p.marksheet_id
                LEFT JOIN prediction_results pr ON p.id = pr.preferences_id
                WHERE m.user_id = (SELECT id FROM users WHERE clerk_user_id = %s)
                GROUP BY m.id, p.id
                ORDER BY m.created_at DESC
            """
            
            cursor.execute(query, (clerk_user_id,))
            history = cursor.fetchall()
            
            conn.close()
            return history
            
        except Exception as e:
            logger.error(f"❌ Error getting user history: {e}")
            return []
    
    def get_user_by_clerk_id(self, clerk_user_id):
        """Get user ID by Clerk user ID"""
        try:
            conn = get_user_db_connection()
            cursor = conn.cursor()
            
            cursor.execute("SELECT id FROM users WHERE clerk_user_id = %s", (clerk_user_id,))
            result = cursor.fetchone()
            
            conn.close()
            return result[0] if result else None
            
        except Exception as e:
            logger.error(f"❌ Error getting user by Clerk ID: {e}")
            return None

# Test the connection
if __name__ == "__main__":
    try:
        conn = get_user_db_connection()
        print("✅ Connected to user_data database successfully!")
        conn.close()
    except Exception as e:
        print(f"❌ Connection failed: {e}")
