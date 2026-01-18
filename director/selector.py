"""Director agent for selecting recipes using Gemini API."""
import json
from typing import Dict, Optional
import google.generativeai as genai
from utils.config import Config
from utils.logging_config import logger
from director.fallback import select_recipe_fallback


class DirectorSelector:
    """Selects appropriate recipe for a given topic using AI or fallback."""
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize director selector.
        
        Args:
            api_key: Gemini API key (uses Config if None)
        """
        self.api_key = api_key or Config.GEMINI_API_KEY
        self.model_name = "gemini-2.0-flash-exp"  # Using latest flash model
        self.model = None
        
        if self.api_key:
            try:
                genai.configure(api_key=self.api_key)
                self.model = genai.GenerativeModel(self.model_name)
                logger.info(f"Initialized Gemini model: {self.model_name}")
            except Exception as e:
                logger.warning(f"Failed to initialize Gemini API: {e}")
                self.model = None
        else:
            logger.warning("Gemini API key not configured, will use fallback")
    
    def select_recipe(self, topic: str, user_preference: Optional[str] = None) -> Dict[str, str]:
        """
        Select recipe for given topic.
        
        Args:
            topic: Input topic string
            user_preference: Optional user-specified recipe preference
            
        Returns:
            Dictionary with 'recipe' and 'reasoning' keys
        """
        # If user specified a preference, use it (if valid)
        if user_preference and user_preference != "auto":
            from recipes.recipe_manager import recipe_manager
            if recipe_manager.recipe_exists(user_preference):
                return {
                    "recipe": user_preference,
                    "reasoning": f"User specified recipe: {user_preference}"
                }
        
        # Try Gemini API first
        if self.model:
            try:
                result = self._select_with_gemini(topic)
                if result:
                    return result
            except Exception as e:
                logger.warning(f"Gemini API failed: {e}, using fallback")
        
        # Fallback to rule-based selection
        return select_recipe_fallback(topic)
    
    def _select_with_gemini(self, topic: str) -> Optional[Dict[str, str]]:
        """
        Select recipe using Gemini API.
        
        Args:
            topic: Input topic string
            
        Returns:
            Dictionary with 'recipe' and 'reasoning' or None if failed
        """
        prompt = f"""Given the topic: "{topic}"

Select the most appropriate video recipe type from these options:
- brainrot: Fast-paced, chaotic videos with intense visuals and energetic audio
- news: Structured news-style videos with clear narration and professional layout
- stories: Short vertical videos (9:16) with friendly narration, perfect for social media stories
- ambient: Slow, calming videos with peaceful visuals and ambient music
- loop10h: Long 10-hour looping ambient videos for background/streaming

Respond with ONLY a valid JSON object in this exact format:
{{
    "recipe": "recipe_name",
    "reasoning": "brief explanation of why this recipe fits the topic"
}}

Do not include any other text, only the JSON object."""

        try:
            response = self.model.generate_content(prompt)
            response_text = response.text.strip()
            
            # Extract JSON from response (handle markdown code blocks)
            if "```json" in response_text:
                response_text = response_text.split("```json")[1].split("```")[0].strip()
            elif "```" in response_text:
                response_text = response_text.split("```")[1].split("```")[0].strip()
            
            result = json.loads(response_text)
            
            # Validate recipe name
            from recipes.recipe_manager import recipe_manager
            recipe_name = result.get("recipe", "").lower()
            if recipe_manager.recipe_exists(recipe_name):
                logger.info(f"Gemini selected recipe: {recipe_name} - {result.get('reasoning', '')}")
                return {
                    "recipe": recipe_name,
                    "reasoning": result.get("reasoning", "Selected by AI")
                }
            else:
                logger.warning(f"Gemini returned invalid recipe: {recipe_name}")
                return None
                
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse Gemini response as JSON: {e}")
            logger.debug(f"Response text: {response_text}")
            return None
        except Exception as e:
            logger.error(f"Gemini API error: {e}")
            return None
    
    def generate_story(self, topic: str, recipe_name: str) -> str:
        """
        Generate story/script for video using Gemini.
        
        Args:
            topic: Input topic
            recipe_name: Selected recipe name
            
        Returns:
            Generated story/script text
        """
        if not self.model:
            logger.warning("Gemini API not available, returning basic story")
            return f"This is a {recipe_name} style video about: {topic}"
        
        from recipes.recipe_manager import recipe_manager
        recipe = recipe_manager.get_recipe(recipe_name)
        story_prompt = recipe.get_story_prompt(topic)
        
        try:
            response = self.model.generate_content(story_prompt)
            story = response.text.strip()
            logger.info(f"Generated story for {recipe_name} recipe")
            return story
        except Exception as e:
            logger.error(f"Failed to generate story with Gemini: {e}")
            return story_prompt  # Return the prompt as fallback


# Global director selector instance
_director_selector: Optional[DirectorSelector] = None


def get_director_selector(api_key: Optional[str] = None) -> DirectorSelector:
    """Get or create global director selector instance."""
    global _director_selector
    if _director_selector is None:
        _director_selector = DirectorSelector(api_key)
    return _director_selector
