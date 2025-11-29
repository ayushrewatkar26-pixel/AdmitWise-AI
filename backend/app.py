from flask import Flask, request, jsonify, session
from flask_cors import CORS
import pandas as pd
import numpy as np
import xgboost as xgb
from sklearn.preprocessing import LabelEncoder
import mysql.connector
import cv2
import pytesseract
import fitz  # PyMuPDF
import os
import warnings
import re
import google.generativeai as genai
from user_data_manager import UserDataManager
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

warnings.filterwarnings("ignore")

# ======================================================
# Flask App Setup
# ======================================================
app = Flask(__name__)
CORS(app)
app.secret_key = os.getenv('FLASK_SECRET_KEY', 'admitwise_secret_key_2024_dev_only')  # For session management

# Initialize User Data Manager
user_manager = UserDataManager()

# ======================================================
# Gemini AI Configuration
# ======================================================
# Configure Gemini AI - Get API key from environment variable
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')

if GEMINI_API_KEY:
    try:
        genai.configure(api_key=GEMINI_API_KEY)
        
        # List available models to see what's supported
        print("🔍 Checking available Gemini models...")
        try:
            models = genai.list_models()
            available_models = [model.name for model in models if 'generateContent' in model.supported_generation_methods]
            print(f"Available models: {available_models[:5]}...")  # Show first 5 models
            
            # Try different model names based on what's available
            # Updated to use the newer model names that are actually available
            model_priority = ['gemini-2.5-flash', 'gemini-2.5-flash-preview-05-20', 'gemini-1.5-flash', 'gemini-1.5-pro', 'gemini-pro']
            
            gemini_model = None
            for model_name in model_priority:
                try:
                    # Check if model is in available models
                    if any(model_name in model for model in available_models):
                        gemini_model = genai.GenerativeModel(model_name)
                        print(f" Gemini AI configured successfully with {model_name}")
                        break
                except Exception as model_error:
                    print(f" Failed to use {model_name}: {model_error}")
                    continue
            
            if not gemini_model:
                # Try the first available model as fallback
                try:
                    first_model = available_models[0].replace('models/', '')
                    gemini_model = genai.GenerativeModel(first_model)
                    print(f" Gemini AI configured with {first_model} (fallback to first available)")
                except Exception as fallback_error:
                    print(f" All model attempts failed: {fallback_error}")
                    gemini_model = None
                
        except Exception as list_error:
            print(f" Could not list models: {list_error}")
            # Try newer models as direct fallback
            fallback_models = ['gemini-2.5-flash', 'gemini-1.5-flash', 'gemini-pro']
            gemini_model = None
            
            for fallback_model in fallback_models:
                try:
                    gemini_model = genai.GenerativeModel(fallback_model)
                    print(f" Gemini AI configured with {fallback_model} (direct fallback)")
                    break
                except Exception as fallback_error:
                    print(f" Failed fallback with {fallback_model}: {fallback_error}")
                    continue
            
            if not gemini_model:
                print(" All fallback attempts failed")
            
    except Exception as e:
        print(f" Error configuring Gemini AI: {e}")
        gemini_model = None

# Define test function first
def test_gemini_connection():
    """
    Test if Gemini API is working properly.
    """
    if not gemini_model:
        return False
    
    try:
        # Simple test query
        test_response = gemini_model.generate_content("Hello, this is a test. Please respond with 'API working'.")
        print(f" Gemini API test successful: {test_response.text[:50]}...")
        return True
    except Exception as e:
        print(f" Gemini API test failed: {e}")
        return False

# Test Gemini connection if model is configured
if gemini_model:
    test_gemini_connection()
else:
    print(" GEMINI_API_KEY not found in environment variables. Fallback responses will be used.")

UPLOAD_FOLDER = "uploads"
ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "pdf"}
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# ======================================================
# Database Connection
# ======================================================
def get_db_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="Sudhir@567",
        database="cutoff_db",
        port=3306
    )

# ======================================================
# Dataset Loading (from MySQL)
# ======================================================
def load_sample_dataset():
    data = {
        'college_name': ['VNIT Nagpur', 'COEP Pune', 'IIT Bombay'],
        'college_code': ['VN01', 'CP02', 'IB03'],
        'branch_name': ['CSE', 'CSE', 'CSE'],
        'seat_type': ['General', 'General', 'General'],
        'year': [2024, 2024, 2024],
        'percentile': [82, 84, 95],
        'state': ['Maharashtra', 'Maharashtra', 'Maharashtra'],
        'city': ['Nagpur', 'Pune', 'Mumbai'],
    }
    return pd.DataFrame(data)

def load_dataset_from_db():
    """
    Load all cutoff tables created by file_watcher.py into one DataFrame.
    Each table is city_capX (e.g., nagpur_cap1, pune_cap2).
    Adds a column 'source_table' so we know where each row came from.
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SHOW TABLES")
        all_tables = [t[0] for t in cursor.fetchall()]

        # pick only tables created by file_watcher (city_capX)
        cutoff_tables = [t for t in all_tables if "_cap" in t]

        if not cutoff_tables:
            print(" No cutoff tables found in MySQL. Using sample dataset.")
            return load_sample_dataset()

        frames = []
        for table in cutoff_tables:
            try:
                df_part = pd.read_sql(f"SELECT * FROM `{table}`", conn)
                df_part["source_table"] = table
                frames.append(df_part)
                print(f" Loaded {len(df_part)} rows from {table}")
            except Exception as e:
                print(f" Skipped {table}: {e}")

        conn.close()

        if frames:
            df_all = pd.concat(frames, ignore_index=True)
            print(f" Total {len(df_all)} rows loaded from {len(frames)} tables")
            return df_all
        else:
            print(" All tables empty. Using sample dataset.")
            return load_sample_dataset()

    except Exception as e:
        print(f" MySQL load error: {e}")
        return load_sample_dataset()

df = load_dataset_from_db()

# ======================================================
# Helper Functions
# ======================================================
def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS
def calculate_weighted_cutoff(previous_cutoffs, exam_year):
    """
    Calculate weighted cutoff with proper year distribution:
    - 1st year (exam_year - 1): 60% + any missing years' share
    - 2nd year (exam_year - 2): 15%
    - 3rd year (exam_year - 3): 15%
    - 4th year (exam_year - 4): 5%
    - 5th year (exam_year - 5): 5%
    
    If any year's cutoff is missing, its share is added to the 1st year.
    """
    prev_year = exam_year - 1
    
    # Define year weights as specified
    year_weights = {
        prev_year: 0.60,        # 1st year: 60%
        prev_year - 1: 0.15,    # 2nd year: 15%
        prev_year - 2: 0.15,    # 3rd year: 15%
        prev_year - 3: 0.05,    # 4th year: 5%
        prev_year - 4: 0.05     # 5th year: 5%
    }
    
    # Step 1: Calculate missing weight and available weighted sum
    missing_weight = 0
    weighted_sum = 0
    available_weight = 0
    
    for year, weight in year_weights.items():
        cutoff = previous_cutoffs.get(year)
        if cutoff is None:
            # Add missing year's weight to missing_weight
            missing_weight += weight
        else:
            # Use available cutoff with its original weight
            weighted_sum += cutoff * weight
            available_weight += weight
    
    # Step 2: Add missing weight to the 1st year (prev_year)
    if previous_cutoffs.get(prev_year) is not None:
        # Add all missing weight to the 1st year
        weighted_sum += previous_cutoffs[prev_year] * missing_weight
        available_weight += missing_weight
    
    # Step 3: Return weighted average
    return weighted_sum / available_weight if available_weight > 0 else None

# ======================================================
# OCR Setup
# ======================================================
# Configure pytesseract with full exe path (important!)
pytesseract.pytesseract.tesseract_cmd = r"C:\Users\HP\AppData\Local\Programs\Tesseract-OCR\tesseract.exe"

def extract_text_from_image(image_path):
    try:
        image = cv2.imread(image_path)
        if image is None:
            print(f"⚠️ Unable to read image: {image_path}")
            return ""

        # Convert to grayscale
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

        # Improve contrast & sharpness
        gray = cv2.resize(gray, None, fx=1.5, fy=1.5, interpolation=cv2.INTER_CUBIC)
        _, thresh = cv2.threshold(gray, 150, 255, cv2.THRESH_BINARY)

        # OCR
        text = pytesseract.image_to_string(thresh, lang="eng")
        return text.strip()
    except Exception as e:
        print(f"OCR error on image: {e}")
        return ""

def extract_text_from_pdf(pdf_path):
    """
    If PDF has digital text -> extract using PyMuPDF
    If PDF is scanned -> OCR each page using pytesseract
    """
    try:
        doc = fitz.open(pdf_path)
        text = ""

        for page_num, page in enumerate(doc):
            page_text = page.get_text()
            if page_text.strip():
                text += page_text
            else:
                # Render page as image and OCR
                pix = page.get_pixmap(dpi=300)
                img_path = f"temp_page_{page_num}.png"
                pix.save(img_path)
                text += extract_text_from_image(img_path)
                os.remove(img_path)

        doc.close()
        return text.strip()
    except Exception as e:
        print(f"PDF extraction error: {e}")
        return ""

def parse_marksheet(text):
    """
    Extract candidate details from MHT CET PDF text.
    Returns a dictionary with name, year, percentile, category.
    """
    result = {}

    # --- Year ---
    year_match = re.search(r"(20\d{2})", text)
    result['year'] = int(year_match.group(1)) if year_match else None

    # Split text into lines for easier parsing
    lines = [line.strip() for line in text.splitlines() if line.strip()]

    # --- Category ---
    categories = ['GENERAL', 'OBC', 'SC', 'ST', 'EWS']
    category = None
    for line in lines:
        if line.upper() in categories:
            category = line.upper()
            break
    result['category'] = category if category else "GENERAL"

    # --- Percentile ---
    # Look for the first numeric value between 0 and 100 with decimal
    percentile = None
    for line in lines:
        try:
            val = float(line)
            if 0 <= val <= 100:
                percentile = val
                break
        except:
            continue
    result['percentile'] = percentile if percentile else 0.0

    # --- Name ---
    # Candidate name usually comes after category
    name = None
    if category:
        try:
            cat_index = lines.index(category)
            # Look for next line(s) with all uppercase letters and multiple words
            for l in lines[cat_index + 1:]:
                if l.isupper() and len(l.split()) >= 2:
                    name = l
                    break
        except ValueError:
            pass
    result['name'] = name if name else "Unknown"

    return result

def weighted_avg_percentile(marksheet_year, df):
    """
    Compute weighted average percentile for last 5 years with updated distribution:
    Year -5: 5%, Year -4: 5%, Year -3: 15%, Year -2: 15%, Year -1: 60%
    Missing years' weights are added to Year -1 (most recent)
    """
    # Define year weights as specified
    year_weights = {
        marksheet_year - 1: 0.60,    # 1st year: 60%
        marksheet_year - 2: 0.15,    # 2nd year: 15%
        marksheet_year - 3: 0.15,    # 3rd year: 15%
        marksheet_year - 4: 0.05,    # 4th year: 5%
        marksheet_year - 5: 0.05     # 5th year: 5%
    }
    
    df_years = df[df['year'].isin(year_weights.keys())].copy()

    # Step 1: Calculate missing weight and available weighted sum
    missing_weight = 0
    weighted_sum = 0
    available_weight = 0
    
    for year, weight in year_weights.items():
        if year in df_years['year'].values:
            percentile = df_years.loc[df_years['year'] == year, 'percentile'].mean()
            weighted_sum += percentile * weight
            available_weight += weight
        else:
            # Add missing year's weight to missing_weight
            missing_weight += weight
    
    # Step 2: Add missing weight to the 1st year (most recent)
    first_year = marksheet_year - 1
    if first_year in df_years['year'].values:
        # Add all missing weight to the 1st year
        first_year_percentile = df_years.loc[df_years['year'] == first_year, 'percentile'].mean()
        weighted_sum += first_year_percentile * missing_weight
        available_weight += missing_weight
    
    return weighted_sum / available_weight if available_weight > 0 else 50

def prepare_features(df):
    features_df = df.copy()
    le_branch = LabelEncoder()
    le_category = LabelEncoder()

    features_df["branch_encoded"] = le_branch.fit_transform(features_df["branch_name"])
    features_df["category_encoded"] = le_category.fit_transform(features_df["seat_type"])
    features_df["avg_cutoff"] = features_df.get("percentile", 50)
    features_df["cutoff_std"] = 5
    features_df["cutoff_trend"] = 0
    features_df["cutoff_volatility"] = 0.1

    return features_df, le_branch, le_category

features_df, le_branch, le_category = prepare_features(df)

def train_model():
    np.random.seed(42)

    # Drop rows with missing branch/category before training
    clean_df = features_df.dropna(subset=["branch_name", "seat_type"]).copy()

    if clean_df.empty:
        print(" No valid data for training, using sample dataset.")
        clean_df = load_sample_dataset()
        clean_df, _, _ = prepare_features(clean_df)

    # Add synthetic target column
    clean_df["admission_chance"] = np.clip(
        100 - clean_df["avg_cutoff"].fillna(50) * 0.4 + np.random.normal(0, 5, len(clean_df)),
        0, 100
    )

    feature_columns = ["avg_cutoff", "cutoff_std", "cutoff_trend",
                       "cutoff_volatility", "branch_encoded", "category_encoded"]

    X = clean_df[feature_columns].fillna(0)
    y = clean_df["admission_chance"].fillna(50)   # default label = 50 if missing

    model = xgb.XGBRegressor(
        n_estimators=100,
        max_depth=5,
        learning_rate=0.1,
        random_state=42
    )
    model.fit(X, y)

    return model, feature_columns


model, feature_columns = train_model()

# ======================================================
# Chatbot Helper Functions
# ======================================================


def call_gemini_api(query, context=""):
    """
    Call Gemini API for general admission-related queries.
    """
    if not gemini_model:
        return get_fallback_response(query)
    
    try:
        prompt = f"""
        You are a helpful assistant for AdmitWise AI, a college admission prediction platform in India.
        You help students with college admission queries, cutoff information, and general admission guidance.
        
        Context: {context}
        
        User Query: {query}
        
        Please provide a helpful, accurate, and encouraging response related to college admissions in India.
        Keep your response concise but informative. If the query is not related to admissions, politely redirect to admission-related topics.
        """
        
        response = gemini_model.generate_content(prompt)
        return response.text
        
    except Exception as e:
        print(f"Gemini API error: {e}")
        return get_fallback_response(query)

def get_fallback_response(query):
    """
    Provide helpful fallback responses when Gemini API is not available.
    """
    query_lower = query.lower()
    
    # College-specific queries
    if any(word in query_lower for word in ['cutoff', 'percentile', 'score', 'admission']):
        return """I can help you with college cutoff information! Our database contains cutoff data for many colleges. 

Try asking about specific colleges like:
• "Show me VNIT Nagpur CSE cutoff"
• "What are the top engineering colleges in Pune?"
• "CSE cutoff for general category"

I can search our database for the most accurate cutoff information available."""

    # General admission queries
    elif any(word in query_lower for word in ['prepare', 'study', 'exam', 'cet', 'jee', 'admission process']):
        return """For admission preparation and guidance:

 **Study Tips:**
• Focus on your target percentile
• Practice previous year papers
• Strengthen weak subjects

 **Admission Process:**
• Check college websites for updates
• Keep documents ready
• Apply before deadlines

 **Our Platform:**
• Upload your marksheet for predictions
• Get admission chances for colleges
• Compare cutoff trends

Feel free to ask about specific colleges or branches!"""

    # Default response
    else:
        return """I'm here to help with college admission queries! 

I can assist you with:
• College cutoff information
• Admission predictions
• Study guidance
• General admission advice

Try asking about specific colleges or use our prediction feature by uploading your marksheet!"""


def get_chat_history(session_id):
    """
    Get chat history for a session.
    """
    return session.get(f'chat_history_{session_id}', [])

def save_to_chat_history(session_id, user_message, bot_response):
    """
    Save conversation to session history.
    """
    if f'chat_history_{session_id}' not in session:
        session[f'chat_history_{session_id}'] = []
    
    session[f'chat_history_{session_id}'].append({
        'user': user_message,
        'bot': bot_response,
        'timestamp': pd.Timestamp.now().isoformat()
    })
    
    # Keep only last 10 conversations
    if len(session[f'chat_history_{session_id}']) > 10:
        session[f'chat_history_{session_id}'] = session[f'chat_history_{session_id}'][-10:]

# ======================================================
# Routes
# ======================================================
@app.route("/upload", methods=["POST"])
def upload_file():
    if "file" not in request.files:
        return jsonify({"error": "No file uploaded"}), 400

    file = request.files["file"]
    if file.filename == "":
        return jsonify({"error": "No file selected"}), 400

    # Get user data from request
    clerk_user_id = request.form.get("clerk_user_id")
    email = request.form.get("email")
    name = request.form.get("name")

    if file and allowed_file(file.filename):
        filepath = os.path.join(app.config["UPLOAD_FOLDER"], file.filename)
        file.save(filepath)

        try:
            if file.filename.lower().endswith(".pdf"):
                text = extract_text_from_pdf(filepath)
            else:
                text = extract_text_from_image(filepath)

            parsed_data = parse_marksheet(text)
            
            # Save to database if user is authenticated
            if clerk_user_id and email and name:
                user_id = user_manager.create_or_update_user(clerk_user_id, email, name)
                if user_id:
                    marksheet_id = user_manager.save_marksheet_data(
                        user_id, file.filename, parsed_data, text
                    )
                    parsed_data["marksheet_id"] = marksheet_id
                    parsed_data["user_id"] = user_id
            
            return jsonify({"extracted_data": parsed_data, "raw_text": text})

        finally:
            if os.path.exists(filepath):
                os.remove(filepath)

    return jsonify({"error": "Invalid file type"}), 400

@app.route("/predict", methods=["POST"])
def predict():
    try:
        data = request.get_json()

        exam_year = int(data.get("exam_year", 2025))
        score = float(data.get("score", 0))
        cap = data.get("cap", "CAP1")
        city = data.get("city", "Nagpur")
        branch = data.get("branch", "CSE")
        category = data.get("category") or data.get("caste_category", "GENERAL")
        
        # Get user data for saving
        user_id = data.get("user_id")
        marksheet_id = data.get("marksheet_id")

        # --- Determine table ---
        table_name = f"{city.strip().lower()}_{cap.strip().lower()}"  # e.g. nagpur_cap1

        conn = get_db_connection()
        query = f"SELECT college_code, college_name, branch_name,branch_code, seat_type, percentile, year FROM `{table_name}`"
        df_city = pd.read_sql(query, conn)
        conn.close()

        # If the table exists but has no rows, return 200 with empty results
        if df_city.empty:
            return jsonify({
                "results": [],
                "message": f"No cutoff records available in {table_name} yet.",
                "available": {
                    "branches": [],
                    "categories": []
                }
            })

        # --- Filter by branch & caste category for previous year first ---
        prev_year = exam_year - 1

        # Perform robust, case-insensitive matching for branch and category
        branch_norm = str(branch).strip().lower()
        category_norm = str(category).strip().lower()
        branch_series = df_city['branch_name'].astype(str).str.strip()
        seat_series = df_city['seat_type'].astype(str).str.strip()
        year_series = df_city['year']

        # First try strict exact match (case-insensitive)
        mask_branch = branch_series.str.lower() == branch_norm
        mask_category = seat_series.str.lower() == category_norm
        mask_year = year_series == prev_year
        df_prev_year = df_city[mask_branch & mask_category & mask_year]

        # If exact match fails but the branch exists with minor naming differences,
        # fall back to contains-based match while keeping category and year strict
        if df_prev_year.empty:
            contains_mask = branch_series.str.lower().str.contains(branch_norm, na=False)
            df_prev_year = df_city[contains_mask & mask_category & mask_year]

        # If nothing matches for that combination, return empty results with helpful metadata
        if df_prev_year.empty:
            available_in_year = df_city[df_city['year'] == prev_year]
            available_branches = sorted(available_in_year['branch_name'].dropna().astype(str).str.strip().unique().tolist()) if not available_in_year.empty else []
            available_categories = sorted(available_in_year['seat_type'].dropna().astype(str).str.strip().unique().tolist()) if not available_in_year.empty else []
            return jsonify({
                "results": [],
                "message": f"No records for branch '{branch}' and category '{category}' in {city} {cap} for year {prev_year}.",
                "available": {
                    "branches": available_branches,
                    "categories": available_categories
                }
            })

        results = []
        for _, row in df_prev_year.iterrows():
            college_code = row['college_code']

            # --- Collect previous 4 years percentiles ---
            previous_cutoffs = {prev_year: row['percentile']}
            for y in range(prev_year - 1, prev_year - 5, -1):
                prev_data = df_city[
                    (df_city['college_code'] == college_code) &
                    (df_city['branch_name'] == branch) &
                    (df_city['seat_type'] == category) &
                    (df_city['year'] == y)
                ]
                previous_cutoffs[y] = float(prev_data['percentile'].mean()) if not prev_data.empty else None
            
            # --- Weighted cutoff ---
            threshold = calculate_weighted_cutoff(previous_cutoffs, exam_year)

            # --- Admission chance calculation (numeric %) ---
            if threshold is not None:
                if score >= threshold:
                    admission_chance = min(100, 70 + (score - threshold) * 0.5)
                else:
                    admission_chance = max(0, 40 + (score - threshold) * 0.3)
            else:
                admission_chance = 50  # default

            results.append({
                "college_name": row["college_name"],
                "college_code": college_code,
                "branch_name": branch,
                "branch_code": row.get("branch_code", ""),
                "seat_type": category,
                "previous_cutoffs": previous_cutoffs,
                "admission_chance": round(float(admission_chance), 2)
            })

        # Save user preferences and results to database
        if user_id and marksheet_id:
            preferences = {
                "cap": cap,
                "caste_category": category,
                "branch": branch,
                "city": city,
                "state": "Maharashtra"  # Default state
            }
            
            preferences_id = user_manager.save_user_preferences(user_id, marksheet_id, preferences)
            
            if preferences_id:
                # Prepare results data for saving
                results_for_db = []
                for result in results:
                    results_for_db.append({
                        "exam_year": exam_year,
                        "user_score": score,
                        "college_name": result["college_name"],
                        "college_code": result["college_code"],
                        "branch_name": result["branch_name"],
                        "admission_chance": result["admission_chance"]
                    })
                
                user_manager.save_prediction_results(user_id, marksheet_id, preferences_id, results_for_db)

        return jsonify({"results": results})

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/filter-results", methods=["POST"])
def filter_results():
    try:
        data = request.get_json()

        exam_year = int(data.get("exam_year", 2025))
        user_score = float(data.get("score", 0))
        cap = data.get("cap", "CAP1")
        city = data.get("city", "Nagpur")
        branch_filter = data.get("branch", "")  # empty = all branches
        caste_category = data.get("caste_category", "GENERAL")

        if not city or not cap:
            return jsonify({"error": "City and CAP are required"}), 400

        table_name = f"{city.strip().lower()}_{cap.strip().lower()}"
        prev_year = exam_year - 1

        conn = get_db_connection()
        # Read the table for the previous year only, then normalize seat_type in pandas
        query = f"""
            SELECT college_code, college_name, branch_name, branch_code, seat_type, percentile, year
            FROM `{table_name}`
            WHERE year = %s
        """
        df_year = pd.read_sql(query, conn, params=(prev_year,))

        if df_year.empty:
            conn.close()
            return jsonify({"results": []})

        # Normalize seat type and branch names (trim + lowercase)
        seat_norm = df_year['seat_type'].astype(str).str.strip().str.lower()
        branch_series = df_year['branch_name'].astype(str).str.strip()
        df_prev_year = df_year[seat_norm == str(caste_category).strip().lower()].copy()

        if df_prev_year.empty:
            conn.close()
            return jsonify({"results": []})

        # Apply branch filter if specified (exact match)
        if branch_filter:
            desired_branch = str(branch_filter).strip().lower()
            exact_mask = df_prev_year['branch_name'].astype(str).str.strip().str.lower() == desired_branch
            filtered = df_prev_year[exact_mask]
            if filtered.empty:
                contains_mask = df_prev_year['branch_name'].astype(str).str.strip().str.lower().str.contains(desired_branch, na=False)
                filtered = df_prev_year[contains_mask]
            df_prev_year = filtered

        all_results = []

        for _, row in df_prev_year.iterrows():
            college_code = row['college_code']
            branch_name = row['branch_name']
            branch_code = row['branch_code']

            # Collect previous 4 years percentiles
            previous_cutoffs = {prev_year: row['percentile']}
            for y in range(prev_year - 1, prev_year - 5, -1):
                query_prev = f"""
                    SELECT percentile
                    FROM `{table_name}`
                    WHERE college_code = %s AND branch_name = %s AND seat_type = %s AND year = %s
                """
                cursor = conn.cursor(dictionary=True)
                cursor.execute(query_prev, (college_code, branch_name, caste_category, y))
                result = cursor.fetchone()
                previous_cutoffs[y] = float(result['percentile']) if result else None

            # Weighted cutoff and admission chance
            threshold = calculate_weighted_cutoff(previous_cutoffs, exam_year)
            if threshold is not None:
                if user_score >= threshold:
                    admission_chance = min(100, 70 + (user_score - threshold) * 0.5)
                else:
                    admission_chance = max(0, 40 + (user_score - threshold) * 0.3)
            else:
                admission_chance = 50

            all_results.append({
                "college_name": row["college_name"],
                "college_code": college_code,
                "branch_name": branch_name,
                "branch_code": branch_code,
                "seat_type": caste_category,
                "previous_cutoffs": previous_cutoffs,
                "admission_chance": round(float(admission_chance), 2)
            })

        conn.close()
        return jsonify({"results": all_results})

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/colleges", methods=["GET"])
def get_colleges():
    try:
        conn = get_db_connection()
        df_col = pd.read_sql("SELECT DISTINCT college_name, college_code, branch_name, seat_type FROM college_data", conn)
        conn.close()
        return jsonify({"colleges": df_col.to_dict(orient="records")})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/chat", methods=["POST"])
def chat():
    """
    AI chatbot endpoint - uses only Gemini AI for all responses
    """
    try:
        data = request.get_json()
        user_message = data.get('message', '').strip()
        session_id = data.get('session_id', 'default')
        
        if not user_message:
            return jsonify({"error": "Message is required"}), 400
        
        # Get chat history for context
        chat_history = get_chat_history(session_id)
        
        print(f" Chat request: '{user_message}'")
        
        # Build context from chat history
        context = ""
        if chat_history:
            # Include recent conversation context
            recent_context = "\n".join([
                f"User: {msg['user']}\nBot: {msg['bot']}" 
                for msg in chat_history[-3:]  # Last 3 conversations
            ])
            context = f"Recent conversation context:\n{recent_context}\n\n"
        
        # Use Gemini API for all responses
        bot_response = call_gemini_api(user_message, context)
        
        # Save to chat history
        save_to_chat_history(session_id, user_message, bot_response)
        
        return jsonify({
            "response": bot_response,
            "type": "ai",
            "session_id": session_id
        })
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/dataset-info", methods=["GET"])
def get_dataset_info():
    """
    Enhanced dataset info endpoint for chatbot metadata.
    """
    try:
        # Get comprehensive dataset information
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        # Get all cutoff tables
        cursor.execute("SHOW TABLES")
        tables = [t['Tables_in_cutoff_db'] for t in cursor.fetchall() if '_cap' in t['Tables_in_cutoff_db']]
        
        # Aggregate information from all tables
        total_records = 0
        unique_colleges = set()
        unique_branches = set()
        unique_categories = set()
        available_cities = set()
        available_years = set()
        
        for table in tables:
            try:
                # Get basic counts
                cursor.execute(f"SELECT COUNT(*) as count FROM `{table}`")
                count_result = cursor.fetchone()
                if count_result:
                    total_records += count_result['count']
                
                # Get unique values
                cursor.execute(f"""
                    SELECT DISTINCT college_name, branch_name, seat_type, city, year
                    FROM `{table}`
                """)
                table_data = cursor.fetchall()
                
                for row in table_data:
                    if row['college_name']:
                        unique_colleges.add(row['college_name'])
                    if row['branch_name']:
                        unique_branches.add(row['branch_name'])
                    if row['seat_type']:
                        unique_categories.add(row['seat_type'])
                    if row.get('city'):
                        available_cities.add(row['city'])
                    if row['year']:
                        available_years.add(row['year'])
                        
            except Exception as e:
                print(f"Error processing table {table}: {e}")
                continue
        
        conn.close()
        
        return jsonify({
            "total_records": total_records,
            "unique_colleges": len(unique_colleges),
            "unique_branches": len(unique_branches),
            "unique_categories": len(unique_categories),
            "available_cities": sorted(list(available_cities)),
            "available_years": sorted(list(available_years)),
            "available_tables": tables,
            "sample_colleges": sorted(list(unique_colleges))[:10],
            "sample_branches": sorted(list(unique_branches))[:10]
        })
        
    except Exception as e:
        # Fallback to basic info from loaded dataframe
        return jsonify({
            "total_records": len(df),
            "unique_colleges": df["college_name"].nunique() if "college_name" in df else 0,
            "unique_branches": df["branch_name"].nunique() if "branch_name" in df else 0,
            "unique_categories": df["seat_type"].nunique() if "seat_type" in df else 0,
            "error": str(e)
        })

@app.route("/user-history", methods=["GET"])
def get_user_history():
    """Get user's complete history from database"""
    try:
        clerk_user_id = request.args.get("clerk_user_id")
        if not clerk_user_id:
            return jsonify({"error": "clerk_user_id is required"}), 400
        
        history = user_manager.get_user_history(clerk_user_id)
        return jsonify({"history": history})
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# ======================================================
# Run App
# ======================================================
if __name__ == "__main__":
    print(" Starting AdmitWise AI Backend (MySQL mode)...")
    app.run(debug=True, port=5000)
