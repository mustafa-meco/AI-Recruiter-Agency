import sqlite3
import json

db_path = "e:/ollama workspace/Ollama_Course/AI Recruiter Agency/db/jobs.sqlite"

try:
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM candidates ORDER BY id DESC LIMIT 1")
    row = cursor.fetchone()
    
    if row:
        print(f"Name: {row['name']}")
        print(f"Score: {row['score']}")
        full_report = json.loads(row['full_report'])
        rec = full_report.get('final_recommendation', {})
        print("Final Recommendation Object:")
        print(json.dumps(rec, indent=2))
    else:
        print("No candidates found.")
    conn.close()
except Exception as e:
    print(f"Error: {e}")
