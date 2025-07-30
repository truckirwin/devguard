"""
Web Search Service - Updated for Database Lookups

Finds AWS documentation using the local/AWS database instead of
unreliable real-time web searches.
"""

from typing import List, Dict
from app.utils.tracking_utils import format_tracking_log
from app.services.hybrid_db_service import db_service


class WebSearchService:
    """Service for finding AWS documentation using database lookups."""
    
    def __init__(self):
        """Initialize the web search service."""
        self.timeout = 5
    
    def search_aws_documentation(self, search_topics: List[str], tracking_id: str) -> str:
        """
        Search AWS documentation using database lookups.
        
        Args:
            search_topics: List of topic search queries
            tracking_id: Tracking ID for logging
            
        Returns:
            HTML formatted references with clickable links
        """
        print(format_tracking_log(tracking_id, f"🔍 Database search for AWS docs: {search_topics}", "INFO"))
        
        all_results = []
        
        # Search for each topic in the database
        for topic in search_topics:
            print(format_tracking_log(tracking_id, f"📚 Searching database for: {topic}", "INFO"))
            
            # Clean the topic for better database search
            clean_topic = self._clean_search_topic(topic)
            
            # Search in the AWS documentation database
            results = db_service.search_aws_docs(clean_topic, limit=3)
            
            if results:
                print(format_tracking_log(tracking_id, f"✅ Found {len(results)} results for: {clean_topic}", "INFO"))
                all_results.extend(results)
            else:
                print(format_tracking_log(tracking_id, f"❌ No results found for: {clean_topic}", "INFO"))
        
        # Remove duplicates by URL
        unique_results = {}
        for result in all_results:
            unique_results[result['url']] = result
        
        final_results = list(unique_results.values())[:5]  # Limit to 5 results
        
        if final_results:
            print(format_tracking_log(tracking_id, f"📖 Generated {len(final_results)} references from database", "INFO"))
            return self._format_references_html(final_results, tracking_id)
        else:
            print(format_tracking_log(tracking_id, "❌ No AWS documentation found in database", "INFO"))
            return self._get_fallback_references(search_topics, tracking_id)
    
    def _clean_search_topic(self, topic: str) -> str:
        """Clean topic for better database search."""
        # Remove site: prefixes and common search operators
        clean_topic = topic.replace("site:docs.aws.amazon.com", "").strip()
        clean_topic = clean_topic.replace('"', '').strip()
        
        # Extract key terms
        if " aws " in clean_topic.lower():
            # Remove "aws" as it's redundant in AWS docs
            clean_topic = clean_topic.lower().replace(" aws ", " ").strip()
        
        return clean_topic
    
    def _format_references_html(self, results: List[Dict], tracking_id: str) -> str:
        """Format database results as HTML references."""
        print(format_tracking_log(tracking_id, f"🎨 Formatting {len(results)} references as HTML", "INFO"))
        
        html_parts = []
        
        for i, result in enumerate(results, 1):
            title = result.get('title', 'AWS Documentation')
            url = result.get('url', '')
            service = result.get('service', 'AWS')
            
            # Clean up title
            if title == 'Untitled' or not title:
                title = f"{service.title()} Documentation"
            
            # Format as: Page title: \n URL (clickable)
            formatted_reference = f'{title}:<br><a href="{url}" target="_blank" rel="noopener">{url}</a>'
            html_parts.append(formatted_reference)
        
        # Join with double line breaks for spacing
        references_html = '<br><br>'.join(html_parts)
        
        print(format_tracking_log(tracking_id, f"✅ References formatted: {len(html_parts)} links", "INFO"))
        return references_html
    
    def _get_fallback_references(self, search_topics: List[str], tracking_id: str) -> str:
        """Generate fallback references when no database results found."""
        print(format_tracking_log(tracking_id, "🔄 Generating fallback references", "INFO"))
        
        # Extract service names from search topics
        services = set()
        for topic in search_topics:
            topic_lower = topic.lower()
            
            # Look for common AWS service names
            aws_services = [
                'sagemaker', 'lambda', 'ec2', 's3', 'rds', 'dynamodb',
                'glue', 'kinesis', 'athena', 'redshift', 'emr', 'bedrock'
            ]
            
            for service in aws_services:
                if service in topic_lower:
                    services.add(service)
        
        if not services:
            # Generic AWS documentation
            fallback_html = (
                'AWS Documentation:<br><a href="https://docs.aws.amazon.com/" target="_blank" rel="noopener">https://docs.aws.amazon.com/</a><br><br>'
                'AWS Getting Started:<br><a href="https://aws.amazon.com/getting-started/" target="_blank" rel="noopener">https://aws.amazon.com/getting-started/</a>'
            )
        else:
            # Service-specific documentation
            html_parts = []
            for service in list(services)[:3]:  # Limit to 3 services
                service_url = f"https://docs.aws.amazon.com/{service}/"
                service_title = f"AWS {service.title()} Documentation"
                formatted_reference = f'{service_title}:<br><a href="{service_url}" target="_blank" rel="noopener">{service_url}</a>'
                html_parts.append(formatted_reference)
            
            fallback_html = '<br><br>'.join(html_parts)
        
        print(format_tracking_log(tracking_id, f"✅ Fallback references generated", "INFO"))
        return fallback_html 