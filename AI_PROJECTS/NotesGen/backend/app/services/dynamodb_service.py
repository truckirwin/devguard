"""
DynamoDB Service for NotesGen
AWS serverless database service
"""

import boto3
import json
import time
import uuid
from datetime import datetime, timezone
from typing import Dict, List, Optional, Any
from boto3.dynamodb.conditions import Key, Attr
from botocore.exceptions import ClientError
from app.utils.tracking_utils import format_tracking_log


class DynamoDBService:
    """Comprehensive DynamoDB service for all app data needs."""
    
    def __init__(self):
        """Initialize DynamoDB service with optimized settings."""
        # Use default region from environment or fallback to us-east-1
        self.dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
        self.table_prefix = 'NotesGen'  # Prefix for all tables
        
        # Table definitions optimized for free tier
        self.tables = {
            'ppt_files': f'{self.table_prefix}_PPTFiles',
            'slide_versions': f'{self.table_prefix}_SlideVersions', 
            'bulk_jobs': f'{self.table_prefix}_BulkJobs',
            'aws_docs': f'{self.table_prefix}_AWSDocs',
            'slide_images': f'{self.table_prefix}_SlideImages'
        }
        
        # Initialize table references
        self._table_refs = {}
    
    def get_table(self, table_name: str):
        """Get table reference with caching."""
        if table_name not in self._table_refs:
            self._table_refs[table_name] = self.dynamodb.Table(self.tables[table_name])
        return self._table_refs[table_name]
    
    def create_all_tables(self):
        """Create all required DynamoDB tables if they don't exist."""
        print("🚀 Creating DynamoDB tables for NotesGen...")
        
        tables_to_create = [
            self._create_ppt_files_table,
            self._create_slide_versions_table,
            self._create_bulk_jobs_table,
            self._create_aws_docs_table,
            self._create_slide_images_table
        ]
        
        for create_func in tables_to_create:
            try:
                create_func()
            except Exception as e:
                print(f"❌ Error creating table: {e}")
        
        print("✅ All DynamoDB tables ready!")
    
    def _create_ppt_files_table(self):
        """Create PPT files table."""
        table_name = self.tables['ppt_files']
        
        try:
            table = self.dynamodb.create_table(
                TableName=table_name,
                KeySchema=[
                    {'AttributeName': 'id', 'KeyType': 'HASH'}  # Partition key
                ],
                AttributeDefinitions=[
                    {'AttributeName': 'id', 'AttributeType': 'N'},
                    {'AttributeName': 'tracking_id', 'AttributeType': 'S'}
                ],
                GlobalSecondaryIndexes=[
                    {
                        'IndexName': 'TrackingIdIndex',
                        'KeySchema': [
                            {'AttributeName': 'tracking_id', 'KeyType': 'HASH'}
                        ],
                        'Projection': {'ProjectionType': 'ALL'}
                    }
                ],
                BillingMode='PAY_PER_REQUEST'  # Free tier friendly
            )
            
            # Wait for table to be created
            table.meta.client.get_waiter('table_exists').wait(TableName=table_name)
            print(f"✅ Created table: {table_name}")
            
        except ClientError as e:
            if e.response['Error']['Code'] == 'ResourceInUseException':
                print(f"✅ Table {table_name} already exists")
            else:
                raise
    
    def _create_slide_versions_table(self):
        """Create slide versions table."""
        table_name = self.tables['slide_versions']
        
        try:
            table = self.dynamodb.create_table(
                TableName=table_name,
                KeySchema=[
                    {'AttributeName': 'slide_id', 'KeyType': 'HASH'},  # Partition key
                    {'AttributeName': 'version_id', 'KeyType': 'RANGE'}  # Sort key
                ],
                AttributeDefinitions=[
                    {'AttributeName': 'slide_id', 'AttributeType': 'N'},
                    {'AttributeName': 'version_id', 'AttributeType': 'S'},
                    {'AttributeName': 'job_id', 'AttributeType': 'S'}
                ],
                GlobalSecondaryIndexes=[
                    {
                        'IndexName': 'JobIdIndex',
                        'KeySchema': [
                            {'AttributeName': 'job_id', 'KeyType': 'HASH'}
                        ],
                        'Projection': {'ProjectionType': 'ALL'}
                    }
                ],
                BillingMode='PAY_PER_REQUEST'
            )
            
            table.meta.client.get_waiter('table_exists').wait(TableName=table_name)
            print(f"✅ Created table: {table_name}")
            
        except ClientError as e:
            if e.response['Error']['Code'] == 'ResourceInUseException':
                print(f"✅ Table {table_name} already exists")
            else:
                raise
    
    def _create_bulk_jobs_table(self):
        """Create bulk generation jobs table."""
        table_name = self.tables['bulk_jobs']
        
        try:
            table = self.dynamodb.create_table(
                TableName=table_name,
                KeySchema=[
                    {'AttributeName': 'job_id', 'KeyType': 'HASH'}  # Partition key
                ],
                AttributeDefinitions=[
                    {'AttributeName': 'job_id', 'AttributeType': 'S'},
                    {'AttributeName': 'ppt_file_id', 'AttributeType': 'N'},
                    {'AttributeName': 'created_at', 'AttributeType': 'S'}
                ],
                GlobalSecondaryIndexes=[
                    {
                        'IndexName': 'PPTFileIdIndex',
                        'KeySchema': [
                            {'AttributeName': 'ppt_file_id', 'KeyType': 'HASH'},
                            {'AttributeName': 'created_at', 'KeyType': 'RANGE'}
                        ],
                        'Projection': {'ProjectionType': 'ALL'}
                    }
                ],
                BillingMode='PAY_PER_REQUEST'
            )
            
            table.meta.client.get_waiter('table_exists').wait(TableName=table_name)
            print(f"✅ Created table: {table_name}")
            
        except ClientError as e:
            if e.response['Error']['Code'] == 'ResourceInUseException':
                print(f"✅ Table {table_name} already exists")
            else:
                raise
    
    def _create_aws_docs_table(self):
        """Create AWS documentation table."""
        table_name = self.tables['aws_docs']
        
        try:
            table = self.dynamodb.create_table(
                TableName=table_name,
                KeySchema=[
                    {'AttributeName': 'url', 'KeyType': 'HASH'}  # Partition key
                ],
                AttributeDefinitions=[
                    {'AttributeName': 'url', 'AttributeType': 'S'},
                    {'AttributeName': 'service', 'AttributeType': 'S'},
                    {'AttributeName': 'last_updated', 'AttributeType': 'S'}
                ],
                GlobalSecondaryIndexes=[
                    {
                        'IndexName': 'ServiceIndex',
                        'KeySchema': [
                            {'AttributeName': 'service', 'KeyType': 'HASH'},
                            {'AttributeName': 'last_updated', 'KeyType': 'RANGE'}
                        ],
                        'Projection': {'ProjectionType': 'ALL'}
                    }
                ],
                BillingMode='PAY_PER_REQUEST'
            )
            
            table.meta.client.get_waiter('table_exists').wait(TableName=table_name)
            print(f"✅ Created table: {table_name}")
            
        except ClientError as e:
            if e.response['Error']['Code'] == 'ResourceInUseException':
                print(f"✅ Table {table_name} already exists")
            else:
                raise
    
    def _create_slide_images_table(self):
        """Create slide images table."""
        table_name = self.tables['slide_images']
        
        try:
            table = self.dynamodb.create_table(
                TableName=table_name,
                KeySchema=[
                    {'AttributeName': 'ppt_file_id', 'KeyType': 'HASH'},  # Partition key
                    {'AttributeName': 'slide_number', 'KeyType': 'RANGE'}  # Sort key
                ],
                AttributeDefinitions=[
                    {'AttributeName': 'ppt_file_id', 'AttributeType': 'N'},
                    {'AttributeName': 'slide_number', 'AttributeType': 'N'}
                ],
                BillingMode='PAY_PER_REQUEST'
            )
            
            table.meta.client.get_waiter('table_exists').wait(TableName=table_name)
            print(f"✅ Created table: {table_name}")
            
        except ClientError as e:
            if e.response['Error']['Code'] == 'ResourceInUseException':
                print(f"✅ Table {table_name} already exists")
            else:
                raise

    # PPT Files Operations
    def create_ppt_file(self, filename: str, file_path: str, tracking_id: str) -> int:
        """Create a new PPT file record."""
        table = self.get_table('ppt_files')
        
        # Generate new ID (simple counter approach)
        ppt_id = int(time.time() * 1000)  # Use timestamp as ID
        
        item = {
            'id': ppt_id,
            'filename': filename,
            'file_path': file_path,
            'tracking_id': tracking_id,
            'created_at': datetime.now(timezone.utc).isoformat(),
            'updated_at': datetime.now(timezone.utc).isoformat()
        }
        
        table.put_item(Item=item)
        return ppt_id
    
    def get_ppt_file(self, ppt_id: int) -> Optional[Dict]:
        """Get PPT file by ID."""
        table = self.get_table('ppt_files')
        
        try:
            response = table.get_item(Key={'id': ppt_id})
            return response.get('Item')
        except ClientError:
            return None
    
    def get_ppt_file_by_tracking_id(self, tracking_id: str) -> Optional[Dict]:
        """Get PPT file by tracking ID."""
        table = self.get_table('ppt_files')
        
        try:
            response = table.query(
                IndexName='TrackingIdIndex',
                KeyConditionExpression=Key('tracking_id').eq(tracking_id)
            )
            items = response.get('Items', [])
            return items[0] if items else None
        except ClientError:
            return None
    
    def list_ppt_files(self, limit: int = 50) -> List[Dict]:
        """List all PPT files."""
        table = self.get_table('ppt_files')
        
        try:
            response = table.scan(Limit=limit)
            return response.get('Items', [])
        except ClientError:
            return []

    # Slide Versions Operations
    def store_slide_version(self, slide_id: int, version_type: str, content: Dict, 
                          job_id: Optional[str] = None) -> str:
        """Store a slide version."""
        table = self.get_table('slide_versions')
        
        version_id = f"{version_type}_{int(time.time() * 1000)}"
        
        item = {
            'slide_id': slide_id,
            'version_id': version_id,
            'version_type': version_type,
            'content': json.dumps(content),
            'job_id': job_id or 'manual',
            'is_active': True,
            'created_at': datetime.now(timezone.utc).isoformat()
        }
        
        table.put_item(Item=item)
        return version_id
    
    def get_slide_versions(self, slide_id: int) -> List[Dict]:
        """Get all versions for a slide."""
        table = self.get_table('slide_versions')
        
        try:
            response = table.query(
                KeyConditionExpression=Key('slide_id').eq(slide_id)
            )
            return response.get('Items', [])
        except ClientError:
            return []

    # Bulk Jobs Operations  
    def create_bulk_job(self, ppt_file_id: int, total_slides: int, 
                       slide_numbers: List[int]) -> str:
        """Create a new bulk generation job."""
        table = self.get_table('bulk_jobs')
        
        job_id = str(uuid.uuid4())
        
        item = {
            'job_id': job_id,
            'ppt_file_id': ppt_file_id,
            'total_slides': total_slides,
            'slide_numbers': slide_numbers,
            'completed_slides': 0,
            'failed_slides': 0,
            'status': 'pending',
            'created_at': datetime.now(timezone.utc).isoformat(),
            'updated_at': datetime.now(timezone.utc).isoformat()
        }
        
        table.put_item(Item=item)
        return job_id
    
    def update_bulk_job(self, job_id: str, updates: Dict):
        """Update bulk job status."""
        table = self.get_table('bulk_jobs')
        
        # Build update expression
        update_expr = "SET "
        expr_values = {}
        
        for key, value in updates.items():
            update_expr += f"{key} = :{key}, "
            expr_values[f":{key}"] = value
        
        update_expr += "updated_at = :updated_at"
        expr_values[":updated_at"] = datetime.now(timezone.utc).isoformat()
        
        table.update_item(
            Key={'job_id': job_id},
            UpdateExpression=update_expr,
            ExpressionAttributeValues=expr_values
        )
    
    def get_bulk_job(self, job_id: str) -> Optional[Dict]:
        """Get bulk job by ID."""
        table = self.get_table('bulk_jobs')
        
        try:
            response = table.get_item(Key={'job_id': job_id})
            return response.get('Item')
        except ClientError:
            return None

    # AWS Documentation Operations
    def store_aws_doc(self, url: str, title: str, service: str, topic: str, 
                     keywords: List[str], content_snippet: str):
        """Store AWS documentation entry."""
        table = self.get_table('aws_docs')
        
        item = {
            'url': url,
            'title': title,
            'service': service,
            'topic': topic,
            'keywords': keywords,  # DynamoDB supports lists
            'content_snippet': content_snippet,
            'last_updated': datetime.now(timezone.utc).isoformat(),
            'crawled_at': datetime.now(timezone.utc).isoformat()
        }
        
        table.put_item(Item=item)
    
    def search_aws_docs(self, query: str, limit: int = 10) -> List[Dict]:
        """Search AWS documentation by keywords."""
        table = self.get_table('aws_docs')
        
        try:
            # Search in title and topic using filter expressions
            response = table.scan(
                FilterExpression=Attr('title').contains(query) | 
                               Attr('topic').contains(query) |
                               Attr('keywords').contains(query),
                Limit=limit
            )
            return response.get('Items', [])
        except ClientError:
            return []
    
    def get_docs_by_service(self, service: str, limit: int = 20) -> List[Dict]:
        """Get documentation for a specific AWS service."""
        table = self.get_table('aws_docs')
        
        try:
            response = table.query(
                IndexName='ServiceIndex',
                KeyConditionExpression=Key('service').eq(service),
                Limit=limit,
                ScanIndexForward=False  # Most recent first
            )
            return response.get('Items', [])
        except ClientError:
            return []

    # Slide Images Operations
    def store_slide_image(self, ppt_file_id: int, slide_number: int, 
                         image_data: str, format: str = 'PNG'):
        """Store slide image."""
        table = self.get_table('slide_images')
        
        item = {
            'ppt_file_id': ppt_file_id,
            'slide_number': slide_number,
            'image_data': image_data,  # Base64 encoded
            'format': format,
            'created_at': datetime.now(timezone.utc).isoformat()
        }
        
        table.put_item(Item=item)
    
    def get_slide_image(self, ppt_file_id: int, slide_number: int) -> Optional[Dict]:
        """Get slide image."""
        table = self.get_table('slide_images')
        
        try:
            response = table.get_item(
                Key={
                    'ppt_file_id': ppt_file_id,
                    'slide_number': slide_number
                }
            )
            return response.get('Item')
        except ClientError:
            return None

    # Utility Operations
    def get_database_stats(self) -> Dict:
        """Get statistics about all tables."""
        stats = {}
        
        for table_key, table_name in self.tables.items():
            try:
                table = self.get_table(table_key)
                
                # Get table description for item count
                desc = table.meta.client.describe_table(TableName=table_name)
                item_count = desc['Table'].get('ItemCount', 0)
                
                stats[table_key] = {
                    'name': table_name,
                    'item_count': item_count,
                    'status': desc['Table']['TableStatus']
                }
            except Exception as e:
                stats[table_key] = {'error': str(e)}
        
        return stats
    
    def migrate_from_sqlite(self, sqlite_db_path: str):
        """Migrate data from existing SQLite database to DynamoDB."""
        print("🔄 Starting SQLite to DynamoDB migration...")
        
        try:
            import sqlite3
            conn = sqlite3.connect(sqlite_db_path)
            conn.row_factory = sqlite3.Row  # Enable column access by name
            cursor = conn.cursor()
            
            # Migrate PPT files
            cursor.execute("SELECT * FROM ppt_files")
            ppt_files = cursor.fetchall()
            
            for row in ppt_files:
                # Create tracking ID if not exists
                tracking_id = getattr(row, 'tracking_id', f"migrated_{row['id']}_{int(time.time())}")
                
                self.create_ppt_file(
                    filename=row['filename'],
                    file_path=row['file_path'],
                    tracking_id=tracking_id
                )
            
            print(f"✅ Migrated {len(ppt_files)} PPT files")
            
            # Migrate slide images if they exist
            try:
                cursor.execute("SELECT * FROM slide_images")
                images = cursor.fetchall()
                
                for row in images:
                    self.store_slide_image(
                        ppt_file_id=row['ppt_file_id'],
                        slide_number=row['slide_number'],
                        image_data=row['image_data'],
                        format=getattr(row, 'format', 'PNG')
                    )
                
                print(f"✅ Migrated {len(images)} slide images")
            except sqlite3.OperationalError:
                print("ℹ️ No slide images table found in SQLite - skipping")
            
            conn.close()
            print("🎉 Migration completed successfully!")
            
        except Exception as e:
            print(f"❌ Migration failed: {e}")


# Global instance
dynamodb_service = DynamoDBService()


def main():
    """Initialize DynamoDB tables."""
    print("🚀 Setting up NotesGen DynamoDB tables...")
    
    try:
        # Create all tables
        dynamodb_service.create_all_tables()
        
        # Show statistics
        stats = dynamodb_service.get_database_stats()
        print("\n📊 Database Statistics:")
        for table_key, info in stats.items():
            print(f"  {table_key}: {info}")
        
        print("\n✅ DynamoDB setup complete!")
        print("💰 All tables configured for free tier (pay-per-request)")
        
    except Exception as e:
        print(f"❌ Setup failed: {e}")


if __name__ == "__main__":
    main() 