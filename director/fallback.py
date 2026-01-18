"""Rule-based fallback for recipe selection."""
from typing import Dict
from utils.logging_config import logger


def select_recipe_fallback(topic: str) -> Dict[str, str]:
    """
    Select recipe using rule-based keyword matching.
    
    Args:
        topic: Input topic string
        
    Returns:
        Dictionary with 'recipe' and 'reasoning' keys
    """
    topic_lower = topic.lower()
    
    # Keyword patterns for each recipe type
    patterns = {
        "ambient": ["ambient", "calm", "peaceful", "serene", "relaxing", "lo-fi", "lofi", "meditation", "zen", "nature", "forest", "ocean", "rain"],
        "loop10h": ["10 hour", "10h", "loop", "looping", "long", "extended", "ambient loop"],
        "news": ["news", "breaking", "report", "update", "announcement", "headline", "story", "journalism"],
        "stories": ["story", "tale", "narrative", "short story", "storytime", "instagram story"],
        "brainrot": ["brainrot", "chaos", "intense", "fast", "energetic", "viral", "meme", "trending"],
    }
    
    # Score each recipe based on keyword matches
    scores = {}
    for recipe, keywords in patterns.items():
        score = sum(1 for keyword in keywords if keyword in topic_lower)
        if score > 0:
            scores[recipe] = score
    
    # Select recipe with highest score
    if scores:
        selected_recipe = max(scores, key=scores.get)
        reasoning = f"Matched {scores[selected_recipe]} keyword(s) for {selected_recipe} recipe"
        logger.info(f"Fallback selected recipe: {selected_recipe} - {reasoning}")
        return {
            "recipe": selected_recipe,
            "reasoning": reasoning
        }
    
    # Default to ambient if no matches
    logger.info("No keyword matches found, defaulting to ambient recipe")
    return {
        "recipe": "ambient",
        "reasoning": "No specific keywords matched, defaulting to ambient style"
    }
