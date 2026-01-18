"""Playwright template for automated video uploading to multiple platforms."""
from playwright.sync_api import sync_playwright, Page, Browser
from pathlib import Path
from typing import Dict, Optional
import time
from utils.logging_config import logger


class VideoUploader:
    """Automated video uploader using Playwright."""
    
    def __init__(self, headless: bool = False):
        """
        Initialize video uploader.
        
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
    
    def upload_to_youtube(
        self,
        video_path: Path,
        title: str,
        description: str,
        credentials: Dict[str, str],
        tags: Optional[list[str]] = None
    ) -> bool:
        """
        Upload video to YouTube.
        
        Args:
            video_path: Path to video file
            title: Video title
            description: Video description
            credentials: Dict with 'email' and 'password'
            tags: Optional list of tags
            
        Returns:
            True if successful, False otherwise
        """
        logger.info(f"Uploading to YouTube: {title}")
        
        if not video_path.exists():
            logger.error(f"Video file not found: {video_path}")
            return False
        
        page = self.browser.new_page()
        
        try:
            # Navigate to YouTube Studio
            page.goto("https://studio.youtube.com")
            time.sleep(2)
            
            # Login (simplified - may need to handle 2FA)
            page.fill('input[type="email"]', credentials["email"])
            page.click('button:has-text("Next")')
            time.sleep(2)
            
            page.fill('input[type="password"]', credentials["password"])
            page.click('button:has-text("Next")')
            time.sleep(5)
            
            # Handle 2FA if needed (would integrate with Gmail verification)
            # This is a template - actual implementation would need to handle various cases
            
            # Click create/upload button
            page.click('button:has-text("Create")')
            time.sleep(1)
            page.click('text="Upload video"')
            time.sleep(2)
            
            # Upload file
            page.set_input_files('input[type="file"]', str(video_path))
            logger.info("Video file selected, waiting for upload...")
            
            # Fill in details
            time.sleep(5)  # Wait for upload to start
            page.fill('input[aria-label="Title"]', title)
            page.fill('textarea[aria-label="Tell viewers about your video"]', description)
            
            if tags:
                tags_input = page.locator('input[aria-label="Tags"]')
                tags_input.fill(", ".join(tags))
            
            # Set visibility (default: unlisted for testing)
            page.click('text="Unlisted"')
            
            # Publish
            page.click('button:has-text("Publish")')
            
            logger.info("YouTube upload initiated")
            return True
            
        except Exception as e:
            logger.error(f"YouTube upload failed: {e}")
            return False
        finally:
            page.close()
    
    def upload_to_tiktok(
        self,
        video_path: Path,
        caption: str,
        credentials: Dict[str, str]
    ) -> bool:
        """
        Upload video to TikTok.
        
        Args:
            video_path: Path to video file
            caption: Video caption
            credentials: Dict with login credentials
            credentials: Dict with 'email'/'username' and 'password'
            
        Returns:
            True if successful, False otherwise
        """
        logger.info(f"Uploading to TikTok: {caption[:50]}...")
        
        if not video_path.exists():
            logger.error(f"Video file not found: {video_path}")
            return False
        
        page = self.browser.new_page()
        
        try:
            # Navigate to TikTok upload page
            page.goto("https://www.tiktok.com/upload")
            time.sleep(2)
            
            # Login if needed
            # TikTok login flow varies - this is a template
            
            # Upload video
            page.set_input_files('input[type="file"]', str(video_path))
            time.sleep(5)
            
            # Add caption
            page.fill('div[contenteditable="true"]', caption)
            
            # Publish
            page.click('button:has-text("Post")')
            
            logger.info("TikTok upload initiated")
            return True
            
        except Exception as e:
            logger.error(f"TikTok upload failed: {e}")
            return False
        finally:
            page.close()
    
    def upload_to_instagram(
        self,
        video_path: Path,
        caption: str,
        credentials: Dict[str, str]
    ) -> bool:
        """
        Upload video to Instagram.
        
        Args:
            video_path: Path to video file
            caption: Video caption
            credentials: Dict with 'username' and 'password'
            
        Returns:
            True if successful, False otherwise
        """
        logger.info(f"Uploading to Instagram: {caption[:50]}...")
        
        if not video_path.exists():
            logger.error(f"Video file not found: {video_path}")
            return False
        
        page = self.browser.new_page()
        
        try:
            # Navigate to Instagram
            page.goto("https://www.instagram.com")
            time.sleep(2)
            
            # Login
            page.fill('input[name="username"]', credentials["username"])
            page.fill('input[name="password"]', credentials["password"])
            page.click('button[type="submit"]')
            time.sleep(5)
            
            # Navigate to create post
            page.goto("https://www.instagram.com/create/select/")
            time.sleep(2)
            
            # Upload video
            page.set_input_files('input[type="file"]', str(video_path))
            time.sleep(5)
            
            # Add caption and publish
            page.fill('textarea[aria-label="Write a caption..."]', caption)
            page.click('button:has-text("Share")')
            
            logger.info("Instagram upload initiated")
            return True
            
        except Exception as e:
            logger.error(f"Instagram upload failed: {e}")
            return False
        finally:
            page.close()


def upload_to_multiple_platforms(
    video_path: Path,
    platform_configs: Dict[str, Dict],
    credentials: Dict[str, Dict[str, str]]
) -> Dict[str, bool]:
    """
    Upload video to multiple platforms.
    
    Args:
        video_path: Path to video file
        platform_configs: Dict mapping platform names to their configs
            Example: {
                "youtube": {"title": "...", "description": "...", "tags": [...]},
                "tiktok": {"caption": "..."},
                "instagram": {"caption": "..."}
            }
        credentials: Dict mapping platform names to credentials
        
    Returns:
        Dict mapping platform names to success status
    """
    results = {}
    
    with VideoUploader(headless=False) as uploader:
        for platform, config in platform_configs.items():
            platform_creds = credentials.get(platform, {})
            
            if platform == "youtube":
                results[platform] = uploader.upload_to_youtube(
                    video_path,
                    config.get("title", ""),
                    config.get("description", ""),
                    platform_creds,
                    config.get("tags")
                )
            elif platform == "tiktok":
                results[platform] = uploader.upload_to_tiktok(
                    video_path,
                    config.get("caption", ""),
                    platform_creds
                )
            elif platform == "instagram":
                results[platform] = uploader.upload_to_instagram(
                    video_path,
                    config.get("caption", ""),
                    platform_creds
                )
            
            # Wait between uploads
            time.sleep(10)
    
    return results
