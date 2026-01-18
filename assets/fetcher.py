"""Asset fetcher for Pexels API and local assets."""
import requests
import json
from pathlib import Path
from typing import List, Dict, Optional, Tuple
from urllib.parse import quote
import hashlib
from utils.config import Config
from utils.logging_config import logger


class AssetFetcher:
    """Fetches video and image assets from Pexels API or local storage."""
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize asset fetcher.
        
        Args:
            api_key: Pexels API key (uses Config if None)
        """
        self.api_key = api_key or Config.PEXELS_API_KEY
        self.base_url = "https://api.pexels.com/v1"
        self.video_url = f"{self.base_url}/videos/search"
        self.photo_url = f"{self.base_url}/search"
        self.cache_dir = Config.TEMP_PATH / "asset_cache"
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.cache_file = self.cache_dir / "cache.json"
        self._load_cache()
    
    def _load_cache(self):
        """Load asset cache from disk."""
        if self.cache_file.exists():
            try:
                with open(self.cache_file, 'r') as f:
                    self.cache = json.load(f)
            except Exception as e:
                logger.warning(f"Failed to load cache: {e}")
                self.cache = {}
        else:
            self.cache = {}
    
    def _save_cache(self):
        """Save asset cache to disk."""
        try:
            with open(self.cache_file, 'w') as f:
                json.dump(self.cache, f, indent=2)
        except Exception as e:
            logger.warning(f"Failed to save cache: {e}")
    
    def _get_cache_key(self, query: str, asset_type: str) -> str:
        """Generate cache key for query."""
        key = f"{asset_type}:{query.lower()}"
        return hashlib.md5(key.encode()).hexdigest()
    
    def _pexels_request(
        self,
        url: str,
        params: Dict,
        headers: Optional[Dict] = None
    ) -> Optional[Dict]:
        """
        Make request to Pexels API.
        
        Args:
            url: API endpoint URL
            params: Query parameters
            headers: Request headers
            
        Returns:
            JSON response or None if error
        """
        if not self.api_key:
            logger.warning("Pexels API key not configured")
            return None
        
        default_headers = {
            "Authorization": self.api_key,
            "User-Agent": "UniversalVideoFactory/1.0"
        }
        if headers:
            default_headers.update(headers)
        
        try:
            response = requests.get(url, params=params, headers=default_headers, timeout=10)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"Pexels API request failed: {e}")
            return None
    
    def search_videos(
        self,
        query: str,
        per_page: int = 10,
        page: int = 1,
        orientation: str = "landscape",
        size: str = "large"
    ) -> List[Dict]:
        """
        Search for videos on Pexels.
        
        Args:
            query: Search query
            per_page: Results per page (max 80)
            page: Page number
            orientation: "landscape", "portrait", or "square"
            size: "large", "medium", or "small"
            
        Returns:
            List of video dictionaries
        """
        cache_key = self._get_cache_key(query, "video")
        if cache_key in self.cache:
            logger.info(f"Using cached video results for: {query}")
            return self.cache[cache_key]
        
        params = {
            "query": query,
            "per_page": min(per_page, 80),
            "page": page,
            "orientation": orientation,
            "size": size
        }
        
        data = self._pexels_request(self.video_url, params)
        if data and "videos" in data:
            videos = data["videos"]
            self.cache[cache_key] = videos
            self._save_cache()
            logger.info(f"Found {len(videos)} videos for query: {query}")
            return videos
        
        logger.warning(f"No videos found for query: {query}")
        return []
    
    def search_photos(
        self,
        query: str,
        per_page: int = 10,
        page: int = 1,
        orientation: str = "landscape"
    ) -> List[Dict]:
        """
        Search for photos on Pexels.
        
        Args:
            query: Search query
            per_page: Results per page (max 80)
            page: Page number
            orientation: "landscape", "portrait", or "square"
            
        Returns:
            List of photo dictionaries
        """
        cache_key = self._get_cache_key(query, "photo")
        if cache_key in self.cache:
            logger.info(f"Using cached photo results for: {query}")
            return self.cache[cache_key]
        
        params = {
            "query": query,
            "per_page": min(per_page, 80),
            "page": page,
            "orientation": orientation
        }
        
        data = self._pexels_request(self.photo_url, params)
        if data and "photos" in data:
            photos = data["photos"]
            self.cache[cache_key] = photos
            self._save_cache()
            logger.info(f"Found {len(photos)} photos for query: {query}")
            return photos
        
        logger.warning(f"No photos found for query: {query}")
        return []
    
    def download_video(self, video_url: str, output_path: Path) -> bool:
        """
        Download video from URL.
        
        Args:
            video_url: Video URL
            output_path: Output file path
            
        Returns:
            True if successful, False otherwise
        """
        try:
            response = requests.get(video_url, stream=True, timeout=30)
            response.raise_for_status()
            
            output_path.parent.mkdir(parents=True, exist_ok=True)
            with open(output_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            
            logger.info(f"Downloaded video: {output_path}")
            return True
        except Exception as e:
            logger.error(f"Failed to download video: {e}")
            return False
    
    def get_best_video_url(self, video_data: Dict) -> Optional[str]:
        """
        Get best quality video URL from video data.
        
        Args:
            video_data: Video dictionary from Pexels API
            
        Returns:
            Best video URL or None
        """
        if "video_files" not in video_data:
            return None
        
        video_files = video_data["video_files"]
        # Prefer high quality, then medium, then low
        for quality in ["hd", "sd", "sd"]:
            for vf in video_files:
                if vf.get("quality") == quality:
                    return vf.get("link")
        
        # Fallback to first available
        if video_files:
            return video_files[0].get("link")
        
        return None
    
    def fetch_videos(
        self,
        keywords: List[str],
        count: int = 5,
        use_local_fallback: bool = True
    ) -> List[Path]:
        """
        Fetch videos for given keywords.
        
        Args:
            keywords: List of search keywords
            count: Number of videos to fetch
            use_local_fallback: Whether to use local assets if API fails
            
        Returns:
            List of video file paths
        """
        videos = []
        query = " ".join(keywords[:3])  # Use first 3 keywords
        
        # Try Pexels API first
        if self.api_key:
            pexels_videos = self.search_videos(query, per_page=count)
            for video_data in pexels_videos[:count]:
                video_url = self.get_best_video_url(video_data)
                if video_url:
                    video_id = video_data.get("id", hash(video_url))
                    output_path = Config.TEMP_PATH / "assets" / f"video_{video_id}.mp4"
                    if self.download_video(video_url, output_path):
                        videos.append(output_path)
                        if len(videos) >= count:
                            break
        
        # Fallback to local assets
        if len(videos) < count and use_local_fallback:
            local_videos = self._get_local_videos(keywords)
            videos.extend(local_videos[:count - len(videos)])
        
        logger.info(f"Fetched {len(videos)} videos for keywords: {keywords}")
        return videos
    
    def fetch_images(
        self,
        keywords: List[str],
        count: int = 5,
        use_local_fallback: bool = True
    ) -> List[Path]:
        """
        Fetch images for given keywords.
        
        Args:
            keywords: List of search keywords
            count: Number of images to fetch
            use_local_fallback: Whether to use local assets if API fails
            
        Returns:
            List of image file paths
        """
        images = []
        query = " ".join(keywords[:3])
        
        # Try Pexels API first
        if self.api_key:
            pexels_photos = self.search_photos(query, per_page=count)
            for photo_data in pexels_photos[:count]:
                photo_url = photo_data.get("src", {}).get("large") or photo_data.get("src", {}).get("original")
                if photo_url:
                    photo_id = photo_data.get("id", hash(photo_url))
                    output_path = Config.TEMP_PATH / "assets" / f"image_{photo_id}.jpg"
                    if self._download_image(photo_url, output_path):
                        images.append(output_path)
                        if len(images) >= count:
                            break
        
        # Fallback to local assets
        if len(images) < count and use_local_fallback:
            local_images = self._get_local_images(keywords)
            images.extend(local_images[:count - len(images)])
        
        logger.info(f"Fetched {len(images)} images for keywords: {keywords}")
        return images
    
    def _download_image(self, image_url: str, output_path: Path) -> bool:
        """Download image from URL."""
        try:
            response = requests.get(image_url, stream=True, timeout=10)
            response.raise_for_status()
            
            output_path.parent.mkdir(parents=True, exist_ok=True)
            with open(output_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            
            return True
        except Exception as e:
            logger.error(f"Failed to download image: {e}")
            return False
    
    def _get_local_videos(self, keywords: List[str]) -> List[Path]:
        """Get local video files matching keywords."""
        local_path = Config.ASSETS_LOCAL_PATH
        if not local_path.exists():
            return []
        
        videos = []
        for ext in [".mp4", ".mov", ".avi", ".mkv"]:
            videos.extend(local_path.glob(f"*{ext}"))
        
        # Simple keyword matching (could be improved)
        if keywords:
            filtered = []
            for video in videos:
                video_name = video.stem.lower()
                if any(kw.lower() in video_name for kw in keywords):
                    filtered.append(video)
            return filtered[:10]  # Return up to 10 matches
        
        return videos[:10]
    
    def _get_local_images(self, keywords: List[str]) -> List[Path]:
        """Get local image files matching keywords."""
        local_path = Config.BASE_DIR / "assets" / "local_images"
        if not local_path.exists():
            return []
        
        images = []
        for ext in [".jpg", ".jpeg", ".png", ".webp"]:
            images.extend(local_path.glob(f"*{ext}"))
        
        # Simple keyword matching
        if keywords:
            filtered = []
            for image in images:
                image_name = image.stem.lower()
                if any(kw.lower() in image_name for kw in keywords):
                    filtered.append(image)
            return filtered[:10]
        
        return images[:10]
    
    def _get_local_audio_files(self) -> List[Path]:
        """Get local audio files."""
        local_path = Config.BASE_DIR / "assets" / "local_audio"
        if not local_path.exists():
            return []
        
        audio_files = []
        for ext in [".mp3", ".wav", ".ogg", ".m4a"]:
            audio_files.extend(local_path.glob(f"*{ext}"))
        
        return audio_files[:10]


# Global asset fetcher instance
_asset_fetcher: Optional[AssetFetcher] = None


def get_asset_fetcher(api_key: Optional[str] = None) -> AssetFetcher:
    """Get or create global asset fetcher instance."""
    global _asset_fetcher
    if _asset_fetcher is None:
        _asset_fetcher = AssetFetcher(api_key)
    return _asset_fetcher
