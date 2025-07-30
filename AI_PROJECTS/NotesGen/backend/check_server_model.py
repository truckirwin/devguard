
import sys
sys.path.insert(0, "/Users/robirwi/Desktop/NotesGen/backend")

from app.models.models import SlideImage
from sqlalchemy.dialects import sqlite

# Show the actual column mapping used by the server
print("Current SlideImage model columns in server memory:")
for column in SlideImage.__table__.columns:
    print(f"  {column.name}: {column.type}")

# Test the problematic query
from app.db.database import SessionLocal
db = SessionLocal()

query = db.query(SlideImage).filter(
    SlideImage.ppt_file_id == 1,
    SlideImage.slide_number == 1
)

# Show the exact SQL being generated
compiled_query = query.statement.compile(dialect=sqlite.dialect(), compile_kwargs={"literal_binds": True})
print(f"\nGenerated SQL: {compiled_query}")

db.close()
