import pandas as pd
import mysql.connector
import logging
import os

# ==============================
# Logging Setup
# ==============================
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

# ==============================
# Database Connection Config
# ==============================
db_config = {
    "host": "localhost",
    "user": "root",
    "password": "Sudhir@567",
    "database": "cutoff_db",
    "port": 3306
}

# ==============================
# Folder Containing Excel Files
# ==============================
FOLDER_PATH = r"E:\project\temp\final"   # 👉 Put all 15 Excel files here


def import_excel_to_mysql(file_path, table_name):
    """Import one Excel file into a new MySQL table (custom table name)."""
    logger.info(f"🔁 Importing: {file_path} -> {table_name}")

    if not os.path.exists(file_path):
        logger.error(f"❌ File not found: {file_path}")
        return False

    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()

        # Drop and recreate table
        cursor.execute(f"DROP TABLE IF EXISTS `{table_name}`")
        cursor.execute(f"""
            CREATE TABLE `{table_name}` (
                college_code VARCHAR(50),
                college_name VARCHAR(255),
                branch_code VARCHAR(50),
                branch_name VARCHAR(255),
                seat_type VARCHAR(50),
                `rank` INT,
                percentile FLOAT,
                `year` INT,
                cap VARCHAR(50)
            )
        """)
        conn.commit()

        # Load Excel
        xls = pd.ExcelFile(file_path)
        total_inserted = 0

        for sheet_name in xls.sheet_names:
            df = pd.read_excel(xls, sheet_name=sheet_name)

            if df.empty:
                continue

            # Normalize column names
            df.columns = df.columns.astype(str).str.strip().str.lower()

            insert_sql = f"""
                INSERT INTO `{table_name}` (
                    college_code, college_name, branch_code, branch_name,
                    seat_type, `rank`, percentile, `year`, cap
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            """

            for _, row in df.iterrows():
                try:
                    values = (
                        str(row.get("college_code")) if pd.notnull(row.get("college_code")) else None,
                        str(row.get("college_name")) if pd.notnull(row.get("college_name")) else None,
                        str(row.get("branch_code")) if pd.notnull(row.get("branch_code")) else None,
                        str(row.get("branch_name")) if pd.notnull(row.get("branch_name")) else None,
                        str(row.get("seat_type")) if pd.notnull(row.get("seat_type")) else None,
                        int(row.get("rank")) if pd.notnull(row.get("rank")) else None,
                        float(row.get("percentile")) if pd.notnull(row.get("percentile")) else None,
                        int(row.get("year")) if pd.notnull(row.get("year")) else None,
                        str(row.get("cap")) if pd.notnull(row.get("cap")) else None
                    )
                    cursor.execute(insert_sql, values)
                    total_inserted += 1
                except Exception as e:
                    logger.warning(f"⚠️ Skipped row: {e}")

            conn.commit()
            logger.info(f"✅ Inserted {len(df)} rows from sheet '{sheet_name}'")

        cursor.close()
        conn.close()
        logger.info(f"🎉 Import finished for {table_name}. Total rows: {total_inserted}")
        return True

    except Exception as e:
        logger.error(f"❌ Import failed for {table_name}: {e}")
        return False


if __name__ == "__main__":
    # Process all Excel files in folder
    for file in os.listdir(FOLDER_PATH):
        if file.endswith(".xlsx") or file.endswith(".xls"):
            file_path = os.path.join(FOLDER_PATH, file)

            # Generate table name from filename (remove extension, spaces -> underscores)
            base_name = os.path.splitext(file)[0]
            table_name = base_name.strip().replace(" ", "_").lower()

            import_excel_to_mysql(file_path, table_name)
