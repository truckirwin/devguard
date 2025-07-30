#!/usr/bin/env python3
from app.db.database import engine
from sqlalchemy import text

with engine.connect() as conn:
    try:
        conn.execute(text('ALTER TABLE ppt_files ADD COLUMN last_modified DATETIME'))
        conn.commit()
        print('✅ Added last_modified column')
    except Exception as e:
        print(f'ℹ️ Column may already exist: {e}') 