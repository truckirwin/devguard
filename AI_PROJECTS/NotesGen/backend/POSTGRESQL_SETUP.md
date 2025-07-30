# PostgreSQL Setup Instructions

## ⚠️ CRITICAL MIGRATION NOTICE

This application has been **permanently migrated from SQLite to PostgreSQL** to resolve:
- "Server unavailable" errors during PPT uploads
- Infinite polling loops for slide images  
- Database locking during heavy image processing
- Column mapping errors (format vs image_format)

**SQLite is NO LONGER SUPPORTED** and will cause system failures.

## Prerequisites

You must have PostgreSQL installed and running before using this application.

### macOS Installation

```bash
# Install PostgreSQL using Homebrew
brew install postgresql@15
brew services start postgresql@15

# Create database and user
psql postgres
```

### Ubuntu/Debian Installation

```bash
# Install PostgreSQL
sudo apt update
sudo apt install postgresql postgresql-contrib

# Start PostgreSQL service
sudo systemctl start postgresql
sudo systemctl enable postgresql

# Access PostgreSQL
sudo -u postgres psql
```

### Windows Installation

1. Download PostgreSQL from: https://www.postgresql.org/download/windows/
2. Run the installer and follow the setup wizard
3. Remember the password you set for the `postgres` user
4. Start PostgreSQL service from Services panel

## Database Setup

Once PostgreSQL is installed, create the database and user:

```sql
-- Connect to PostgreSQL as superuser
psql -U postgres

-- Create database
CREATE DATABASE notesgen_db;

-- Create user
CREATE USER notesgen WITH PASSWORD 'notesgen_password';

-- Grant privileges
GRANT ALL PRIVILEGES ON DATABASE notesgen_db TO notesgen;

-- For PostgreSQL 15+ (additional permissions needed)
\c notesgen_db
GRANT ALL ON SCHEMA public TO notesgen;
GRANT ALL ON ALL TABLES IN SCHEMA public TO notesgen;
GRANT ALL ON ALL SEQUENCES IN SCHEMA public TO notesgen;

-- Exit
\q
```

## Environment Configuration

1. Copy the environment template:
   ```bash
   cp env_template.txt .env
   ```

2. Edit `.env` with your PostgreSQL settings:
   ```bash
   # Required: PostgreSQL connection
   DATABASE_URL=postgresql://notesgen:notesgen_password@localhost:5432/notesgen_db
   
   # Change this in production!
   SECRET_KEY=your-secret-key-here-change-in-production
   ```

## Migration from SQLite (If Applicable)

If you have existing SQLite data to migrate:

```bash
# 1. Ensure PostgreSQL is running and configured
# 2. Run the migration script
cd backend
python migrate_to_postgresql.py
```

This script will:
- ✅ Backup your SQLite database
- ✅ Create PostgreSQL schema
- ✅ Migrate all your data
- ✅ Verify the migration
- ✅ Fix column mapping issues

## Starting the Application

After PostgreSQL setup:

```bash
# Install dependencies
pip install -r requirements.txt

# Start the application
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

You should see:
```
✅ Connected to PostgreSQL: PostgreSQL 15.x on ...
INFO:     Application startup complete.
```

## Troubleshooting

### "Failed to connect to PostgreSQL"

1. **Check PostgreSQL is running:**
   ```bash
   # macOS
   brew services list | grep postgresql
   
   # Ubuntu
   sudo systemctl status postgresql
   
   # Windows
   # Check Services panel for "postgresql" service
   ```

2. **Check connection settings:**
   ```bash
   psql -U notesgen -d notesgen_db -h localhost
   ```

3. **Check firewall settings:**
   - PostgreSQL runs on port 5432
   - Ensure localhost connections are allowed

### "Database does not exist"

```sql
-- Connect as postgres user and create database
psql -U postgres
CREATE DATABASE notesgen_db;
```

### "Permission denied"

```sql
-- Grant all privileges to notesgen user
psql -U postgres -d notesgen_db
GRANT ALL PRIVILEGES ON DATABASE notesgen_db TO notesgen;
GRANT ALL ON SCHEMA public TO notesgen;
```

### "Column mapping verification failed"

This indicates a model validation error. Try:

1. **Clear Python cache:**
   ```bash
   find . -name "*.pyc" -delete
   find . -name "__pycache__" -delete
   ```

2. **Restart the application:**
   ```bash
   uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
   ```

## Verifying the Setup

Test that everything works:

```bash
# Test database connection
python -c "from app.db.database import engine; print('PostgreSQL connection successful!')"

# Test application startup
curl http://localhost:8000/health
```

Expected response: `{"status": "healthy"}`

## Performance Benefits

After migrating to PostgreSQL, you should experience:

- ✅ **No more "Server unavailable" errors**
- ✅ **Faster concurrent PPT uploads**
- ✅ **Better handling of large files (40+ slides)**
- ✅ **Eliminated infinite polling loops**
- ✅ **Resolved column mapping errors**
- ✅ **Production-grade performance**

## Security Notes

For production deployment:

1. **Change default passwords:**
   ```sql
   ALTER USER notesgen WITH PASSWORD 'your-secure-password';
   ```

2. **Update environment variables:**
   ```bash
   DATABASE_URL=postgresql://notesgen:your-secure-password@localhost:5432/notesgen_db
   SECRET_KEY=your-production-secret-key
   ```

3. **Configure PostgreSQL security:**
   - Edit `postgresql.conf` and `pg_hba.conf`
   - Restrict network access
   - Enable SSL connections

## Support

If you encounter issues:

1. **Check the logs:** Application logs will show detailed PostgreSQL connection information
2. **Verify PostgreSQL version:** This application is tested with PostgreSQL 12+
3. **Check system resources:** PostgreSQL requires adequate RAM and disk space

## DO NOT REVERT TO SQLITE

⚠️ **WARNING:** Do not attempt to use SQLite with this application. The code contains specific validations to prevent SQLite usage because it causes system failures. PostgreSQL is now required for proper operation. 