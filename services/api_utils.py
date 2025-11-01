"""
API Utilities
Helper functions for making external API calls.
"""

import requests
from typing import Dict, Any, Optional
import logging
from time import sleep

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class APIClient:
    """Generic API client with retry logic and error handling."""
    
    def __init__(self, base_url: str = '', timeout: int = 10):
        """
        Initialize API client.
        
        Args:
            base_url: Base URL for API requests
            timeout: Request timeout in seconds
        """
        self.base_url = base_url
        self.timeout = timeout
        self.session = requests.Session()
    
    def get(self, endpoint: str, params: Optional[Dict[str, Any]] = None, 
            headers: Optional[Dict[str, str]] = None, retries: int = 3) -> Dict[str, Any]:
        """
        Make a GET request with retry logic.
        
        Args:
            endpoint: API endpoint path
            params: Query parameters
            headers: Request headers
            retries: Number of retry attempts
            
        Returns:
            JSON response as dictionary
        """
        url = f"{self.base_url}{endpoint}" if self.base_url else endpoint
        
        for attempt in range(retries):
            try:
                response = self.session.get(
                    url,
                    params=params,
                    headers=headers,
                    timeout=self.timeout
                )
                response.raise_for_status()
                return response.json()
                
            except requests.exceptions.HTTPError as e:
                logger.error(f"HTTP error on attempt {attempt + 1}: {e}")
                if response.status_code == 429:  # Rate limit
                    wait_time = 2 ** attempt  # Exponential backoff
                    logger.info(f"Rate limited. Waiting {wait_time}s before retry...")
                    sleep(wait_time)
                elif attempt == retries - 1:
                    return {'error': f'HTTP {response.status_code}: {str(e)}'}
                    
            except requests.exceptions.ConnectionError as e:
                logger.error(f"Connection error on attempt {attempt + 1}: {e}")
                if attempt == retries - 1:
                    return {'error': f'Connection error: {str(e)}'}
                sleep(1)
                
            except requests.exceptions.Timeout as e:
                logger.error(f"Timeout on attempt {attempt + 1}: {e}")
                if attempt == retries - 1:
                    return {'error': f'Request timeout: {str(e)}'}
                sleep(1)
                
            except requests.exceptions.RequestException as e:
                logger.error(f"Request error: {e}")
                return {'error': f'Request failed: {str(e)}'}
        
        return {'error': 'Max retries exceeded'}
    
    def post(self, endpoint: str, data: Optional[Dict[str, Any]] = None,
             json: Optional[Dict[str, Any]] = None, headers: Optional[Dict[str, str]] = None,
             retries: int = 3) -> Dict[str, Any]:
        """
        Make a POST request with retry logic.
        
        Args:
            endpoint: API endpoint path
            data: Form data
            json: JSON data
            headers: Request headers
            retries: Number of retry attempts
            
        Returns:
            JSON response as dictionary
        """
        url = f"{self.base_url}{endpoint}" if self.base_url else endpoint
        
        for attempt in range(retries):
            try:
                response = self.session.post(
                    url,
                    data=data,
                    json=json,
                    headers=headers,
                    timeout=self.timeout
                )
                response.raise_for_status()
                return response.json()
                
            except requests.exceptions.HTTPError as e:
                logger.error(f"HTTP error on attempt {attempt + 1}: {e}")
                if response.status_code == 429:  # Rate limit
                    wait_time = 2 ** attempt
                    logger.info(f"Rate limited. Waiting {wait_time}s before retry...")
                    sleep(wait_time)
                elif attempt == retries - 1:
                    return {'error': f'HTTP {response.status_code}: {str(e)}'}
                    
            except requests.exceptions.RequestException as e:
                logger.error(f"Request error: {e}")
                if attempt == retries - 1:
                    return {'error': f'Request failed: {str(e)}'}
                sleep(1)
        
        return {'error': 'Max retries exceeded'}


def format_api_error(error: Dict[str, Any]) -> str:
    """
    Format API error for user display.
    
    Args:
        error: Error dictionary from API response
        
    Returns:
        Formatted error message
    """
    if 'error' in error:
        return f"API Error: {error['error']}"
    return "An unexpected error occurred"


def is_api_response_valid(response: Dict[str, Any]) -> bool:
    """
    Check if API response is valid (no errors).
    
    Args:
        response: API response dictionary
        
    Returns:
        True if valid, False if contains errors
    """
    return 'error' not in response and response is not None


def parse_timestamp(timestamp_str: str, format: str = '%Y-%m-%dT%H:%M:%SZ') -> Optional[str]:
    """
    Parse and format timestamp string.
    
    Args:
        timestamp_str: Timestamp string to parse
        format: Expected timestamp format
        
    Returns:
        Formatted timestamp or None if parsing fails
    """
    try:
        from datetime import datetime
        dt = datetime.strptime(timestamp_str, format)
        return dt.isoformat()
    except Exception as e:
        logger.error(f"Error parsing timestamp: {e}")
        return None
