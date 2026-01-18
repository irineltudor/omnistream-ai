"""Recipe manager for registering and instantiating recipes."""
from typing import Dict, Type, Optional
from recipes.base_recipe import RecipeBase
from recipes.brainrot_recipe import BrainrotRecipe
from recipes.news_recipe import NewsRecipe
from recipes.stories_recipe import StoriesRecipe
from recipes.ambient_recipe import AmbientRecipe
from recipes.loop10h_recipe import Loop10hRecipe
from utils.logging_config import logger


class RecipeManager:
    """Manages recipe registration and instantiation."""
    
    def __init__(self):
        """Initialize recipe manager with all available recipes."""
        self._recipes: Dict[str, Type[RecipeBase]] = {}
        self._register_default_recipes()
    
    def _register_default_recipes(self):
        """Register all default recipe types."""
        recipes = [
            BrainrotRecipe,
            NewsRecipe,
            StoriesRecipe,
            AmbientRecipe,
            Loop10hRecipe,
        ]
        
        for recipe_class in recipes:
            instance = recipe_class()
            name = instance.get_name()
            self._recipes[name] = recipe_class
            logger.info(f"Registered recipe: {name}")
    
    def register_recipe(self, name: str, recipe_class: Type[RecipeBase]):
        """
        Register a custom recipe.
        
        Args:
            name: Recipe name identifier
            recipe_class: Recipe class to register
        """
        self._recipes[name] = recipe_class
        logger.info(f"Registered custom recipe: {name}")
    
    def get_recipe(
        self,
        recipe_type: str,
        duration: Optional[float] = None,
        resolution: Optional[str] = None,
        fps: Optional[int] = None
    ) -> RecipeBase:
        """
        Get a recipe instance.
        
        Args:
            recipe_type: Recipe type name (e.g., "brainrot", "news")
            duration: Optional duration override
            resolution: Optional resolution override
            fps: Optional FPS override
            
        Returns:
            Recipe instance
            
        Raises:
            ValueError: If recipe type not found
        """
        if recipe_type not in self._recipes:
            available = ", ".join(self._recipes.keys())
            raise ValueError(
                f"Recipe type '{recipe_type}' not found. Available: {available}"
            )
        
        recipe_class = self._recipes[recipe_type]
        return recipe_class(duration=duration, resolution=resolution, fps=fps)
    
    def list_recipes(self) -> list[str]:
        """List all available recipe types."""
        return list(self._recipes.keys())
    
    def recipe_exists(self, recipe_type: str) -> bool:
        """Check if a recipe type exists."""
        return recipe_type in self._recipes


# Global recipe manager instance
recipe_manager = RecipeManager()
