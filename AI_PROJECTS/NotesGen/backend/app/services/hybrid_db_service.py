"""
Hybrid Database Service

Automatically uses DynamoDB when AWS permissions are available,
falls back to SQLite for local development and testing.
"""

import os
import sqlite3
import json
import time
import uuid
from datetime import datetime, timezone
from typing import Dict, List, Optional, Any


class HybridDatabaseService:
    """Database service that automatically chooses DynamoDB or SQLite."""
    
    def __init__(self):
        """Initialize with automatic database detection."""
        self.use_dynamodb = self._test_dynamodb_access()
        
        if self.use_dynamodb:
            print("💫 Using AWS DynamoDB (serverless)")
            from app.services.dynamodb_service import dynamodb_service
            self.db = dynamodb_service
        else:
            print("💽 Using SQLite (local development)")
            self.db = SQLiteDatabase()
    
    def _test_dynamodb_access(self) -> bool:
        """Test if DynamoDB access is available."""
        try:
            import boto3
            from botocore.exceptions import ClientError, NoCredentialsError
            
            # Quick test to see if we can access DynamoDB
            dynamodb = boto3.client('dynamodb', region_name='us-east-1')
            dynamodb.list_tables()
            return True
            
        except (ClientError, NoCredentialsError, ImportError):
            return False
    
    # Delegate all operations to the underlying database
    def __getattr__(self, name):
        """Delegate all method calls to the underlying database service."""
        return getattr(self.db, name)


class SQLiteDatabase:
    """SQLite implementation that mimics DynamoDB structure for development."""
    
    def __init__(self, db_path: str = "notesgen_local.db"):
        """Initialize SQLite database."""
        self.db_path = db_path
        self.create_all_tables()
    
    def create_all_tables(self):
        """Create all required tables in SQLite."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # PPT Files table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS ppt_files (
                id INTEGER PRIMARY KEY,
                filename TEXT NOT NULL,
                file_path TEXT NOT NULL,
                tracking_id TEXT UNIQUE NOT NULL,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            )
        """)
        
        # Slide Versions table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS slide_versions (
                slide_id INTEGER NOT NULL,
                version_id TEXT NOT NULL,
                version_type TEXT NOT NULL,
                content TEXT NOT NULL,
                job_id TEXT,
                is_active BOOLEAN DEFAULT 1,
                created_at TEXT NOT NULL,
                PRIMARY KEY (slide_id, version_id)
            )
        """)
        
        # Bulk Jobs table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS bulk_jobs (
                job_id TEXT PRIMARY KEY,
                ppt_file_id INTEGER NOT NULL,
                total_slides INTEGER NOT NULL,
                slide_numbers TEXT NOT NULL,  -- JSON array
                completed_slides INTEGER DEFAULT 0,
                failed_slides INTEGER DEFAULT 0,
                status TEXT DEFAULT 'pending',
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            )
        """)
        
        # AWS Documentation table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS aws_docs (
                url TEXT PRIMARY KEY,
                title TEXT NOT NULL,
                service TEXT NOT NULL,
                topic TEXT NOT NULL,
                keywords TEXT NOT NULL,  -- JSON array
                content_snippet TEXT,
                last_updated TEXT NOT NULL,
                crawled_at TEXT NOT NULL
            )
        """)
        
        # Slide Images table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS slide_images (
                ppt_file_id INTEGER NOT NULL,
                slide_number INTEGER NOT NULL,
                image_data TEXT NOT NULL,  -- Base64
                format TEXT DEFAULT 'PNG',
                created_at TEXT NOT NULL,
                PRIMARY KEY (ppt_file_id, slide_number)
            )
        """)
        
        # Create indexes for better performance
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_ppt_tracking 
            ON ppt_files(tracking_id)
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_versions_job 
            ON slide_versions(job_id)
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_jobs_ppt 
            ON bulk_jobs(ppt_file_id)
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_docs_service 
            ON aws_docs(service)
        """)
        
        conn.commit()
        conn.close()
        print("✅ SQLite tables created successfully")

    # PPT Files Operations
    def create_ppt_file(self, filename: str, file_path: str, tracking_id: str) -> int:
        """Create a new PPT file record."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO ppt_files (filename, file_path, tracking_id, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?)
        """, (
            filename, file_path, tracking_id,
            datetime.now(timezone.utc).isoformat(),
            datetime.now(timezone.utc).isoformat()
        ))
        
        ppt_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return ppt_id
    
    def get_ppt_file(self, ppt_id: int) -> Optional[Dict]:
        """Get PPT file by ID."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM ppt_files WHERE id = ?", (ppt_id,))
        row = cursor.fetchone()
        
        conn.close()
        return dict(row) if row else None
    
    def get_ppt_file_by_tracking_id(self, tracking_id: str) -> Optional[Dict]:
        """Get PPT file by tracking ID."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM ppt_files WHERE tracking_id = ?", (tracking_id,))
        row = cursor.fetchone()
        
        conn.close()
        return dict(row) if row else None
    
    def list_ppt_files(self, limit: int = 50) -> List[Dict]:
        """List all PPT files."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM ppt_files ORDER BY created_at DESC LIMIT ?", (limit,))
        rows = cursor.fetchall()
        
        conn.close()
        return [dict(row) for row in rows]

    # Slide Versions Operations
    def store_slide_version(self, slide_id: int, version_type: str, content: Dict, 
                          job_id: Optional[str] = None) -> str:
        """Store a slide version."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        version_id = f"{version_type}_{int(time.time() * 1000)}"
        
        cursor.execute("""
            INSERT INTO slide_versions 
            (slide_id, version_id, version_type, content, job_id, is_active, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            slide_id, version_id, version_type, json.dumps(content),
            job_id or 'manual', True, datetime.now(timezone.utc).isoformat()
        ))
        
        conn.commit()
        conn.close()
        return version_id
    
    def get_slide_versions(self, slide_id: int) -> List[Dict]:
        """Get all versions for a slide."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT * FROM slide_versions 
            WHERE slide_id = ? 
            ORDER BY created_at DESC
        """, (slide_id,))
        rows = cursor.fetchall()
        
        conn.close()
        return [dict(row) for row in rows]

    # Bulk Jobs Operations
    def create_bulk_job(self, ppt_file_id: int, total_slides: int, 
                       slide_numbers: List[int]) -> str:
        """Create a new bulk generation job."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        job_id = str(uuid.uuid4())
        
        cursor.execute("""
            INSERT INTO bulk_jobs 
            (job_id, ppt_file_id, total_slides, slide_numbers, completed_slides, 
             failed_slides, status, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            job_id, ppt_file_id, total_slides, json.dumps(slide_numbers),
            0, 0, 'pending',
            datetime.now(timezone.utc).isoformat(),
            datetime.now(timezone.utc).isoformat()
        ))
        
        conn.commit()
        conn.close()
        return job_id
    
    def update_bulk_job(self, job_id: str, updates: Dict):
        """Update bulk job status."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Build dynamic update query
        set_clauses = []
        values = []
        
        for key, value in updates.items():
            set_clauses.append(f"{key} = ?")
            values.append(value)
        
        set_clauses.append("updated_at = ?")
        values.append(datetime.now(timezone.utc).isoformat())
        values.append(job_id)
        
        query = f"UPDATE bulk_jobs SET {', '.join(set_clauses)} WHERE job_id = ?"
        cursor.execute(query, values)
        
        conn.commit()
        conn.close()
    
    def get_bulk_job(self, job_id: str) -> Optional[Dict]:
        """Get bulk job by ID."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM bulk_jobs WHERE job_id = ?", (job_id,))
        row = cursor.fetchone()
        
        conn.close()
        if row:
            result = dict(row)
            # Parse JSON fields
            result['slide_numbers'] = json.loads(result['slide_numbers'])
            return result
        return None

    # AWS Documentation Operations
    def store_aws_doc(self, url: str, title: str, service: str, topic: str, 
                     keywords: List[str], content_snippet: str):
        """Store AWS documentation entry."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT OR REPLACE INTO aws_docs 
            (url, title, service, topic, keywords, content_snippet, last_updated, crawled_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            url, title, service, topic, json.dumps(keywords), content_snippet,
            datetime.now(timezone.utc).isoformat(),
            datetime.now(timezone.utc).isoformat()
        ))
        
        conn.commit()
        conn.close()
    
    def search_aws_docs(self, query: str, limit: int = 10) -> List[Dict]:
        """Search AWS documentation by keywords."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        # Simple text search across title, topic, and keywords
        cursor.execute("""
            SELECT * FROM aws_docs 
            WHERE title LIKE ? OR topic LIKE ? OR keywords LIKE ?
            ORDER BY last_updated DESC
            LIMIT ?
        """, (f"%{query}%", f"%{query}%", f"%{query}%", limit))
        
        rows = cursor.fetchall()
        conn.close()
        
        results = []
        for row in rows:
            result = dict(row)
            result['keywords'] = json.loads(result['keywords'])
            results.append(result)
        
        return results
    
    def get_docs_by_service(self, service: str, limit: int = 20) -> List[Dict]:
        """Get documentation for a specific AWS service."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT * FROM aws_docs 
            WHERE service = ?
            ORDER BY last_updated DESC
            LIMIT ?
        """, (service, limit))
        
        rows = cursor.fetchall()
        conn.close()
        
        results = []
        for row in rows:
            result = dict(row)
            result['keywords'] = json.loads(result['keywords'])
            results.append(result)
        
        return results

    # Slide Images Operations
    def store_slide_image(self, ppt_file_id: int, slide_number: int, 
                         image_data: str, format: str = 'PNG'):
        """Store slide image."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT OR REPLACE INTO slide_images 
            (ppt_file_id, slide_number, image_data, format, created_at)
            VALUES (?, ?, ?, ?, ?)
        """, (
            ppt_file_id, slide_number, image_data, format,
            datetime.now(timezone.utc).isoformat()
        ))
        
        conn.commit()
        conn.close()
    
    def get_slide_image(self, ppt_file_id: int, slide_number: int) -> Optional[Dict]:
        """Get slide image."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT * FROM slide_images 
            WHERE ppt_file_id = ? AND slide_number = ?
        """, (ppt_file_id, slide_number))
        
        row = cursor.fetchone()
        conn.close()
        return dict(row) if row else None

    # Utility Operations
    def get_database_stats(self) -> Dict:
        """Get statistics about all tables."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        stats = {}
        tables = ['ppt_files', 'slide_versions', 'bulk_jobs', 'aws_docs', 'slide_images']
        
        for table in tables:
            cursor.execute(f"SELECT COUNT(*) FROM {table}")
            count = cursor.fetchone()[0]
            stats[table] = {
                'name': table,
                'item_count': count,
                'status': 'ACTIVE'
            }
        
        conn.close()
        return stats


# Global instance - automatically chooses the best database
db_service = HybridDatabaseService()


def main():
    """Test the hybrid database service."""
    print("🧪 Testing Hybrid Database Service...")
    
    # Show which database is being used
    db_type = "DynamoDB" if db_service.use_dynamodb else "SQLite"
    print(f"📊 Using: {db_type}")
    
    # Show statistics
    stats = db_service.get_database_stats()
    print("📈 Database stats:")
    for table, info in stats.items():
        print(f"  {table}: {info['item_count']} items")
    
    print("✅ Hybrid database service ready!")


if __name__ == "__main__":
    main() 