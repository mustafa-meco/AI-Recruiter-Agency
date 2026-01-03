from db.database import JobDatabase
import json

db = JobDatabase()
candidates = db.get_all_candidates()

print(f"Total candidates: {len(candidates)}\n")

for c in candidates:
    print(f"=== {c['name']} ===")
    print(f"Score: {c['score']}")
    print(f"Recommendation: {c['recommendation'][:150]}...")
    
    if isinstance(c['full_report'], dict):
        final_rec = c['full_report'].get('final_recommendation', {})
        print(f"Has final_recommendation key: {bool(final_rec)}")
        print(f"Recommendation text: {final_rec.get('recommendation', 'N/A')[:100]}...")
    else:
        print("Full report is not a dict")
    print()
