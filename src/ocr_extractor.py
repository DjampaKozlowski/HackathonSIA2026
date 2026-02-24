import re
from typing import Optional, Dict, List
import pytesseract
from PIL import Image
import io

class TraitExtractor:
    """Extract trait information from OCR text using pattern matching."""
    
    # Patterns pour détecter les traits et leurs informations
    PATTERNS = {
        "VIGOUR": {
            "keywords": ["vigour", "vigor", "plant vigor", "visual vigor"],
            "method_patterns": [
                r"visual\s+(?:scoring|assessment|evaluation)",
                r"scored\s+visually",
                r"visual\s+scale"
            ],
            "unit_patterns": [
                r"scale\s+(?:of\s+)?(\d+)\s*[-–to]+\s*(\d+)",
                r"(\d+)\s*[-–]\s*(\d+)\s+scale",
                r"1\s*[-–to]+\s*9"
            ]
        },
        "Shoot_Lenght": {
            "keywords": ["shoot length", "shoot height", "stem length"],
            "method_patterns": [
                r"measured\s+(?:with|using)\s+(?:a\s+)?ruler",
                r"manual\s+measurement"
            ],
            "unit_patterns": [r"\b(cm|centimeter|millimeter|mm)\b"]
        },
        "Leaf_Area": {
            "keywords": ["leaf area", "foliar area", "leaf surface"],
            "method_patterns": [
                r"(?:measured\s+)?(?:with|using)\s+(?:a\s+)?(?:leaf\s+area\s+)?meter",
                r"LI[-\s]?COR",
                r"planimeter"
            ],
            "unit_patterns": [r"\b(cm[²2]|m[²2]|mm[²2])\b"]
        },
        "SPAD": {
            "keywords": ["spad", "chlorophyll", "spad value", "spad meter"],
            "method_patterns": [
                r"SPAD[-\s]?(?:meter|502)?",
                r"chlorophyll\s+meter"
            ],
            "unit_patterns": [r"SPAD\s+(?:units?|values?)"]
        },
        "Fresh_Aerial_Weight": {
            "keywords": ["fresh aerial weight", "fresh weight", "above-ground weight", "shoot fresh weight"],
            "method_patterns": [
                r"weighed?\s+(?:fresh|immediately)",
                r"fresh\s+(?:weight|mass)\s+(?:determination|measurement)"
            ],
            "unit_patterns": [r"\b(g|kg|mg|grams?|kilograms?)\b(?:/(?:ha|plot|plant))?"]
        },
        "Fresh_Root_Weight": {
            "keywords": ["fresh root weight", "root fresh weight", "root weight"],
            "method_patterns": [
                r"roots?\s+(?:were\s+)?weighed?\s+fresh",
                r"fresh\s+root\s+(?:weight|mass)"
            ],
            "unit_patterns": [r"\b(g|kg|mg|grams?|kilograms?)\b(?:/plant)?"]
        },
        "Bud_Break": {
            "keywords": ["bud break", "budburst", "bud burst", "budding"],
            "method_patterns": [
                r"(?:counted|scored|recorded)\s+(?:when|at)\s+bud",
                r"visual\s+(?:observation|assessment)\s+of\s+bud",
                r"BBCH\s+stage"
            ],
            "unit_patterns": [
                r"(?:days?|date)\s+(?:after|from)\s+(?:planting|sowing)",
                r"julian\s+day",
                r"BBCH\s+(?:scale|stage)"
            ]
        }
    }
    
    def __init__(self):
        pass
    
    def extract_text_from_image(self, image_bytes: bytes) -> str:
        """Extract text from image using Tesseract OCR."""
        image = Image.open(io.BytesIO(image_bytes))
        text = pytesseract.image_to_string(image, lang='eng')
        return text
    
    def find_trait_info(self, text: str, trait_id: str) -> Dict[str, Optional[str]]:
        """Extract trait information from text using pattern matching."""
        text_lower = text.lower()
        
        if trait_id not in self.PATTERNS:
            return {"trait": None, "method": None, "unit": None}
        
        patterns = self.PATTERNS[trait_id]
        
        # Check if trait is mentioned
        trait_found = any(kw in text_lower for kw in patterns["keywords"])
        
        if not trait_found:
            return {"trait": None, "method": None, "unit": None}
        
        # Extract trait description (context around keywords)
        trait_desc = self._extract_context(text, patterns["keywords"])
        
        # Extract method
        method = self._extract_pattern(text_lower, patterns.get("method_patterns", []))
        
        # Extract unit
        unit = self._extract_pattern(text_lower, patterns.get("unit_patterns", []))
        
        # Only return if we found at least something meaningful
        if trait_desc or method or unit:
            return {
                "trait": trait_desc,
                "method": method,
                "unit": unit
            }
        
        return {"trait": None, "method": None, "unit": None}
    
    def _extract_context(self, text: str, keywords: List[str], window: int = 100) -> Optional[str]:
        """Extract surrounding context when a keyword is found."""
        text_lower = text.lower()
        
        for keyword in keywords:
            pos = text_lower.find(keyword)
            if pos != -1:
                start = max(0, pos - window)
                end = min(len(text), pos + len(keyword) + window)
                context = text[start:end].strip()
                # Clean up
                context = re.sub(r'\s+', ' ', context)
                return context
        
        return None
    
    def _extract_pattern(self, text: str, patterns: List[str]) -> Optional[str]:
        """Extract first matching pattern from text."""
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return match.group(0).strip()
        return None
    
    def extract_all_traits(self, image_bytes: bytes, trait_ids: List[Dict]) -> List[Dict]:
        """Extract all traits from an image."""
        text = self.extract_text_from_image(image_bytes)
        
        results = []
        for trait_info in trait_ids:
            trait_id = trait_info["trait_id"]
            info = self.find_trait_info(text, trait_id)
            
            # Only include if we found something
            if any(v is not None for v in info.values()):
                results.append({
                    "trait_id": trait_id,
                    "description": trait_info["description"],
                    **info
                })
        
        return results