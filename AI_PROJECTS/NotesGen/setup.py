from setuptools import setup, find_packages

setup(
    name="notesgen",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "fastapi==0.104.1",
        "uvicorn==0.24.0",
        "sqlalchemy==2.0.23",
        "pydantic==2.5.1",
        "python-multipart==0.0.6",
        "python-dotenv==1.0.0",
        "alembic==1.12.1",
        "boto3==1.29.1",
        "python-pptx==0.6.21",
        "python-jose[cryptography]==3.3.0",
        "passlib[bcrypt]==1.7.4",
        "python-magic==0.4.27",
        "psycopg2-binary==2.9.9",
        "aiofiles==23.2.1",
        "httpx==0.25.1",
        "asyncio==3.4.3",
        "websockets==12.0",
        "pydantic-settings==2.1.0",
    ],
) 