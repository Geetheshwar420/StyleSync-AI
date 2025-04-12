import openai
import os
from typing import Dict, List

class FashionChatbot:
    def __init__(self):
        # Initialize OpenAI API from .env file
        from dotenv import load_dotenv
        load_dotenv()
        self.api_key = os.getenv('OPENAI_API_KEY')
        if not self.api_key:
            raise ValueError("OPENAI_API_KEY not found in .env file")
        openai.api_key = self.api_key

        self.system_prompt = """
        You are a professional fashion stylist providing advice to clients. 
        Your responses should be:
        - Concise (1-2 sentences)
        - Professional yet friendly
        - Focused on practical fashion advice
        - Include specific recommendations when possible
        - Consider body types, skin tones, and current trends
        """
        
        # Initialize with some example conversations
        self.example_conversations = [
            {"role": "user", "content": "What should I wear to a summer wedding?"},
            {"role": "assistant", "content": "For a summer wedding, consider a light chiffon dress in pastel colors. Pair with strappy sandals and minimal jewelry."},
            {"role": "user", "content": "I have a pear-shaped body, what styles flatter me?"},
            {"role": "assistant", "content": "A-line skirts and dresses balance your proportions. Pair with structured tops to draw attention upward."}
        ]

    def get_fashion_advice(self, message: str, context: Dict = None) -> str:
        """Get fashion advice from the chatbot"""
        messages = [
            {"role": "system", "content": self.system_prompt},
            *self.example_conversations,
            {"role": "user", "content": message}
        ]

        if context:
            # Add context about user's body type/skin tone if available
            context_message = f"Additional context - Body type: {context.get('body_type', 'unknown')}, Skin tone: {context.get('skin_tone', 'unknown')}"
            messages.insert(1, {"role": "system", "content": context_message})

        try:
            response = openai.ChatCompletion.create(
                model="gpt-4o",
                messages=messages,
                temperature=0.7,
                max_tokens=150
            )
            return response.choices[0].message.content
        except Exception as e:
            return f"Sorry, I couldn't process your request. Error: {str(e)}"

    def generate_outfit_recommendation(self, body_type: str, skin_tone: str, occasion: str = None) -> List[str]:
        """Generate specific outfit recommendations"""
        prompt = f"Generate 3 outfit recommendations for someone with {body_type} body type and {skin_tone} skin tone"
        if occasion:
            prompt += f" for a {occasion} event"
        
        messages = [
            {"role": "system", "content": self.system_prompt},
            {"role": "user", "content": prompt}
        ]

        try:
            response = openai.ChatCompletion.create(
                model="gpt-4o", 
                messages=messages,
                temperature=0.7,
                max_tokens=300
            )
            return self._parse_outfit_response(response.choices[0].message.content)
        except Exception as e:
            return [f"Couldn't generate recommendations. Error: {str(e)}"]

    def _parse_outfit_response(self, text: str) -> List[str]:
        """Parse the chatbot response into individual outfit recommendations"""
        # Simple parsing - split by numbered items or newlines
        outfits = []
        for line in text.split('\n'):
            line = line.strip()
            if line and not line.startswith(('1.', '2.', '3.', '-')):
                outfits.append(line)
        return outfits[:3] if outfits else [text]
