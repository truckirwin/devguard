"""
AWS Documentation Crawler - Updated for Hybrid Database

Systematically crawls docs.aws.amazon.com to build a comprehensive database
of AWS documentation URLs with their topics and keywords.

Uses hybrid database service (DynamoDB when available, SQLite locally).
"""

import requests
import re
import time
from typing import List, Dict, Set, Optional
from urllib.parse import urljoin, urlparse
from bs4 import BeautifulSoup
from dataclasses import dataclass
from app.services.hybrid_db_service import db_service


@dataclass
class DocumentationPage:
    url: str
    title: str
    service: str
    topic: str
    keywords: List[str]
    content_snippet: str
    last_updated: str


class AWSDocsCrawler:
    """Crawls AWS documentation and builds a searchable database."""
    
    def __init__(self):
        self.base_url = "https://docs.aws.amazon.com"
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (compatible; AWS-NotesGen-Crawler/1.0)'
        })
        self.visited_urls: Set[str] = set()
        self.crawl_delay = 1  # Respectful crawling delay
    
    def get_aws_services(self) -> List[str]:
        """Get list of all AWS services from the main documentation page."""
        print("🔍 Discovering AWS services...")
        
        try:
            response = self.session.get(f"{self.base_url}")
            response.raise_for_status()
            soup = BeautifulSoup(response.content, 'html.parser')
            
            services = []
            
            # Look for service links in the main docs page
            for link in soup.find_all('a', href=True):
                href = link.get('href')
                if href and href.startswith('/') and not href.startswith('//'):
                    # Extract service name from URL pattern
                    match = re.match(r'^/([a-zA-Z0-9-]+)/?', href)
                    if match:
                        service = match.group(1)
                        if service not in ['index', 'general', 'whitepapers']:
                            services.append(service)
            
            # Add known major services that might be missed
            known_services = [
                'sagemaker', 'lambda', 'ec2', 's3', 'rds', 'dynamodb',
                'iam', 'vpc', 'cloudformation', 'cloudwatch', 'glue',
                'kinesis', 'redshift', 'athena', 'emr', 'bedrock',
                'stepfunctions', 'apigateway', 'elasticache', 'efs',
                'fsx', 'organizations', 'config', 'cloudtrail'
            ]
            
            for service in known_services:
                if service not in services:
                    services.append(service)
            
            services = list(set(services))  # Remove duplicates
            print(f"✅ Found {len(services)} AWS services to crawl")
            return services
            
        except Exception as e:
            print(f"❌ Error discovering services: {e}")
            return []
    
    def crawl_service_documentation(self, service: str, max_pages: int = 100):
        """Crawl all documentation for a specific AWS service."""
        print(f"🔍 Crawling {service} documentation...")
        
        # Common documentation paths for each service
        doc_paths = [
            f"/{service}/latest/dg/",  # Developer Guide
            f"/{service}/latest/userguide/",  # User Guide
            f"/{service}/latest/api/",  # API Reference
            f"/{service}/latest/cli/",  # CLI Reference
        ]
        
        pages_crawled = 0
        for doc_path in doc_paths:
            if pages_crawled >= max_pages:
                break
                
            crawled = self.crawl_documentation_section(service, doc_path, max_pages - pages_crawled)
            pages_crawled += crawled
            
            # Rate limiting
            time.sleep(self.crawl_delay)
    
    def crawl_documentation_section(self, service: str, doc_path: str, max_pages: int) -> int:
        """Crawl a specific documentation section for a service."""
        base_url = f"{self.base_url}{doc_path}"
        
        # Try to find the index page
        index_urls = [
            f"{base_url}index.html",
            f"{base_url}what-is-{service}.html",
            f"{base_url}getting-started.html",
            f"{base_url}",
        ]
        
        pages_crawled = 0
        for index_url in index_urls:
            if pages_crawled >= max_pages:
                break
                
            try:
                print(f"  📖 Trying: {index_url}")
                response = self.session.get(index_url, timeout=10)
                
                if response.status_code == 200:
                    print(f"  ✅ Found: {index_url}")
                    crawled = self.crawl_page_and_links(service, index_url, max_pages - pages_crawled)
                    pages_crawled += crawled
                    break
                    
            except Exception as e:
                print(f"  ❌ Failed to access {index_url}: {e}")
                continue
        
        return pages_crawled
    
    def crawl_page_and_links(self, service: str, url: str, max_pages: int) -> int:
        """Crawl a page and its linked pages."""
        if url in self.visited_urls or max_pages <= 0:
            return 0
        
        try:
            print(f"    🔍 Crawling: {url}")
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            
            self.visited_urls.add(url)
            
            # Parse the page
            soup = BeautifulSoup(response.content, 'html.parser')
            page = self.extract_page_content(service, url, soup)
            
            if page:
                self.store_page(page)
                print(f"    ✅ Stored: {page.title}")
            
            pages_crawled = 1
            
            # Find and crawl linked pages in the same service
            if pages_crawled < max_pages:
                for link in soup.find_all('a', href=True):
                    if pages_crawled >= max_pages:
                        break
                        
                    href = link.get('href')
                    if href:
                        # Resolve relative URLs
                        full_url = urljoin(url, href)
                        
                        # Only crawl pages within the same service documentation
                        if (full_url.startswith(f"{self.base_url}/{service}/") and 
                            full_url not in self.visited_urls and
                            full_url.endswith('.html')):
                            
                            time.sleep(self.crawl_delay)  # Rate limiting
                            crawled = self.crawl_page_and_links(service, full_url, max_pages - pages_crawled)
                            pages_crawled += crawled
            
            return pages_crawled
            
        except Exception as e:
            print(f"    ❌ Error crawling {url}: {e}")
            return 0
    
    def extract_page_content(self, service: str, url: str, soup: BeautifulSoup) -> Optional[DocumentationPage]:
        """Extract content from a documentation page."""
        try:
            # Extract title
            title_tag = soup.find('title')
            title = title_tag.get_text().strip() if title_tag else "Untitled"
            
            # Clean up title
            title = re.sub(r' - Amazon .+$', '', title)
            title = re.sub(r' - AWS .+$', '', title)
            
            # Extract main content
            main_content = soup.find('main') or soup.find('div', class_='main-content') or soup.body
            if not main_content:
                return None
            
            # Extract text content
            content_text = main_content.get_text()
            content_snippet = ' '.join(content_text.split())[:500]  # First 500 chars
            
            # Extract topic from URL and content
            topic = self.extract_topic(url, title, content_text)
            
            # Extract keywords
            keywords = self.extract_keywords(title, content_text)
            
            return DocumentationPage(
                url=url,
                title=title,
                service=service,
                topic=topic,
                keywords=keywords,
                content_snippet=content_snippet,
                last_updated=time.strftime('%Y-%m-%d')
            )
            
        except Exception as e:
            print(f"    ❌ Error extracting content from {url}: {e}")
            return None
    
    def extract_topic(self, url: str, title: str, content: str) -> str:
        """Extract the main topic from URL, title, and content."""
        # Extract from URL path
        url_parts = urlparse(url).path.split('/')
        
        # Look for meaningful parts in the URL
        topic_candidates = []
        for part in url_parts:
            if part and part != 'latest' and not part.endswith('.html'):
                # Convert kebab-case to title case
                topic_candidates.append(part.replace('-', ' ').title())
        
        # Use title as primary topic
        if title and title != "Untitled":
            return title
        
        # Fallback to URL-based topic
        if topic_candidates:
            return ' > '.join(topic_candidates[-2:])  # Last 2 meaningful parts
        
        return "General"
    
    def extract_keywords(self, title: str, content: str) -> List[str]:
        """Extract relevant keywords from title and content."""
        # Combine title and content
        text = f"{title} {content}".lower()
        
        # AWS-specific keywords to look for
        aws_keywords = [
            'sagemaker', 'lambda', 'ec2', 's3', 'rds', 'dynamodb',
            'iam', 'vpc', 'cloudformation', 'cloudwatch', 'glue',
            'kinesis', 'redshift', 'athena', 'emr', 'bedrock',
            'api gateway', 'step functions', 'elasticache',
            'machine learning', 'ml', 'ai', 'artificial intelligence',
            'data pipeline', 'etl', 'analytics', 'database',
            'serverless', 'containers', 'kubernetes', 'docker',
            'security', 'authentication', 'authorization',
            'monitoring', 'logging', 'metrics', 'alerting',
            'storage', 'backup', 'disaster recovery',
            'networking', 'cdn', 'load balancer',
            'autopilot', 'automl', 'algorithms', 'training',
            'inference', 'model', 'endpoint', 'batch transform'
        ]
        
        found_keywords = []
        for keyword in aws_keywords:
            if keyword in text:
                found_keywords.append(keyword)
        
        # Add title words as keywords
        title_words = re.findall(r'\b\w{4,}\b', title.lower())
        found_keywords.extend(title_words)
        
        return list(set(found_keywords))  # Remove duplicates
    
    def store_page(self, page: DocumentationPage):
        """Store a documentation page in the database."""
        try:
            db_service.store_aws_doc(
                url=page.url,
                title=page.title,
                service=page.service,
                topic=page.topic,
                keywords=page.keywords,
                content_snippet=page.content_snippet
            )
        except Exception as e:
            print(f"❌ Error storing page {page.url}: {e}")
    
    def search_documentation(self, query: str, limit: int = 10) -> List[Dict]:
        """Search the documentation database for relevant pages."""
        return db_service.search_aws_docs(query, limit)
    
    def get_database_stats(self) -> Dict:
        """Get statistics about the crawled documentation."""
        stats = db_service.get_database_stats()
        return {
            'total_pages': stats.get('aws_docs', {}).get('item_count', 0),
            'database_type': 'DynamoDB' if db_service.use_dynamodb else 'SQLite'
        }
    
    def crawl_all_services(self, max_pages_per_service: int = 50):
        """Crawl documentation for all AWS services."""
        services = self.get_aws_services()
        
        print(f"🚀 Starting comprehensive crawl of {len(services)} AWS services")
        print(f"📊 Max pages per service: {max_pages_per_service}")
        print(f"💾 Using database: {'DynamoDB' if db_service.use_dynamodb else 'SQLite'}")
        
        for i, service in enumerate(services, 1):
            print(f"\n🔍 [{i}/{len(services)}] Crawling {service}...")
            
            try:
                self.crawl_service_documentation(service, max_pages_per_service)
                
                # Show progress
                stats = self.get_database_stats()
                print(f"📊 Progress: {stats['total_pages']} pages crawled")
                
                # Respectful delay between services
                time.sleep(2)
                
            except Exception as e:
                print(f"❌ Error crawling {service}: {e}")
                continue
        
        # Final statistics
        final_stats = self.get_database_stats()
        print(f"\n🎉 Crawling complete!")
        print(f"📊 Final stats: {final_stats['total_pages']} pages")
        print(f"💾 Database: {final_stats['database_type']}")


def main():
    """Run the AWS documentation crawler."""
    crawler = AWSDocsCrawler()
    
    # Start with smaller crawl for testing
    print("🚀 Starting AWS Documentation Crawler")
    crawler.crawl_all_services(max_pages_per_service=20)


if __name__ == "__main__":
    main() 