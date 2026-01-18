"""Gmail verification code reader using Playwright."""
from playwright.sync_api import sync_playwright, Page, Browser
from typing import Optional
import time
import re
from utils.logging_config import logger


class GmailVerifier:
    """Reads verification codes from Gmail."""
    
    def __init__(self, headless: bool = False):
        """
        Initialize Gmail verifier.
        
        Args:
            headless: Whether to run browser in headless mode
        """
        self.headless = headless
        self.playwright = None
        self.browser: Optional[Browser] = None
    
    def __enter__(self):
        """Context manager entry."""
        self.playwright = sync_playwright().start()
        self.browser = self.playwright.chromium.launch(headless=self.headless)
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        if self.browser:
            self.browser.close()
        if self.playwright:
            self.playwright.stop()
    
    def read_verification_code(
        self,
        email: str,
        password: str,
        sender: Optional[str] = None,
        subject_keywords: Optional[list[str]] = None,
        timeout: int = 60
    ) -> Optional[str]:
        """
        Read verification code from Gmail.
        
        Args:
            email: Gmail address
            password: Gmail password
            sender: Optional sender email to filter by
            subject_keywords: Optional keywords to search in subject
            timeout: Maximum time to wait for email (seconds)
            
        Returns:
            Verification code string or None if not found
        """
        logger.info(f"Reading verification code from Gmail: {email}")
        
        page = self.browser.new_page()
        
        try:
            # Navigate to Gmail
            page.goto("https://mail.google.com")
            time.sleep(2)
            
            # Login
            page.fill('input[type="email"]', email)
            page.click('button:has-text("Next")')
            time.sleep(2)
            
            page.fill('input[type="password"]', password)
            page.click('button:has-text("Next")')
            time.sleep(5)
            
            # Wait for inbox to load
            page.wait_for_selector('div[role="main"]', timeout=10000)
            
            # Search for verification email
            search_query = "verification code"
            if sender:
                search_query = f"from:{sender} {search_query}"
            if subject_keywords:
                search_query += " " + " ".join(subject_keywords)
            
            page.fill('input[aria-label="Search"]', search_query)
            page.press('input[aria-label="Search"]', 'Enter')
            time.sleep(3)
            
            # Wait for email to arrive (polling)
            start_time = time.time()
            code = None
            
            while time.time() - start_time < timeout:
                try:
                    # Click on first email
                    page.click('div[role="main"] tr:first-child', timeout=5000)
                    time.sleep(2)
                    
                    # Extract code from email body
                    email_body = page.locator('div[role="main"]').inner_text()
                    
                    # Look for common code patterns
                    patterns = [
                        r'\b\d{6}\b',  # 6-digit code
                        r'\b\d{4}\b',  # 4-digit code
                        r'code[:\s]+(\d+)',  # "code: 123456"
                        r'verification[:\s]+(\d+)',  # "verification: 123456"
                    ]
                    
                    for pattern in patterns:
                        match = re.search(pattern, email_body, re.IGNORECASE)
                        if match:
                            code = match.group(1) if match.groups() else match.group(0)
                            logger.info(f"Found verification code: {code}")
                            return code
                    
                    # If no code found, wait and retry
                    time.sleep(5)
                    page.go_back()
                    time.sleep(2)
                    
                except Exception as e:
                    logger.debug(f"Waiting for email: {e}")
                    time.sleep(5)
            
            logger.warning("Verification code not found within timeout")
            return None
            
        except Exception as e:
            logger.error(f"Failed to read verification code: {e}")
            return None
        finally:
            page.close()
    
    def wait_for_verification_email(
        self,
        email: str,
        password: str,
        sender: Optional[str] = None,
        timeout: int = 60
    ) -> bool:
        """
        Wait for verification email to arrive (without reading code).
        
        Args:
            email: Gmail address
            password: Gmail password
            sender: Optional sender email
            timeout: Maximum wait time
            
        Returns:
            True if email found, False otherwise
        """
        code = self.read_verification_code(email, password, sender, timeout=timeout)
        return code is not None


def get_verification_code(
    email: str,
    password: str,
    sender: Optional[str] = None,
    timeout: int = 60
) -> Optional[str]:
    """
    Convenience function to get verification code.
    
    Args:
        email: Gmail address
        password: Gmail password
        sender: Optional sender email
        timeout: Maximum wait time
        
    Returns:
        Verification code or None
    """
    with GmailVerifier(headless=True) as verifier:
        return verifier.read_verification_code(email, password, sender, timeout=timeout)
