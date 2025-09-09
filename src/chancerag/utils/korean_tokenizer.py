"""Korean text tokenizer implementation."""

import logging
from typing import List, Optional
import re

logger = logging.getLogger(__name__)


class KoreanTokenizer:
    """Korean text tokenizer for RAG system."""
    
    def __init__(self):
        """Initialize Korean tokenizer."""
        self.korean_pattern = re.compile(r'[가-힣]+')
        self.punctuation_pattern = re.compile(r'[.,!?;:()[\]{}"\'-]')
        self.whitespace_pattern = re.compile(r'\s+')
        
    def tokenize(self, text: str) -> List[str]:
        """
        Tokenize Korean text.
        
        Args:
            text: Input text to tokenize
            
        Returns:
            List of tokens
        """
        try:
            if not text or not isinstance(text, str):
                return []
            
            # Clean text
            text = self._clean_text(text)
            
            # Split by Korean word boundaries
            tokens = self._split_korean_text(text)
            
            # Filter empty tokens
            tokens = [token for token in tokens if token.strip()]
            
            return tokens
            
        except Exception as e:
            logger.warning(f"Error tokenizing text: {e}")
            # Fallback to simple whitespace splitting
            return text.split()
    
    def _clean_text(self, text: str) -> str:
        """
        Clean input text.
        
        Args:
            text: Input text
            
        Returns:
            Cleaned text
        """
        # Normalize whitespace
        text = self.whitespace_pattern.sub(' ', text)
        
        # Remove excessive punctuation
        text = re.sub(r'[.]{2,}', '...', text)
        text = re.sub(r'[!]{2,}', '!!', text)
        text = re.sub(r'[?]{2,}', '??', text)
        
        return text.strip()
    
    def _split_korean_text(self, text: str) -> List[str]:
        """
        Split Korean text into tokens.
        
        Args:
            text: Input text
            
        Returns:
            List of tokens
        """
        tokens = []
        current_token = ""
        
        for char in text:
            if self._is_korean_char(char):
                current_token += char
            elif char.isspace():
                if current_token:
                    tokens.append(current_token)
                    current_token = ""
                tokens.append(" ")
            elif self.punctuation_pattern.match(char):
                if current_token:
                    tokens.append(current_token)
                    current_token = ""
                tokens.append(char)
            else:
                # Handle non-Korean characters
                if current_token:
                    tokens.append(current_token)
                    current_token = ""
                if char.strip():
                    tokens.append(char)
        
        # Add remaining token
        if current_token:
            tokens.append(current_token)
        
        return tokens
    
    def _is_korean_char(self, char: str) -> bool:
        """
        Check if character is Korean.
        
        Args:
            char: Character to check
            
        Returns:
            True if Korean character
        """
        return bool(self.korean_pattern.match(char))
    
    def tokenize_sentences(self, text: str) -> List[str]:
        """
        Split text into sentences.
        
        Args:
            text: Input text
            
        Returns:
            List of sentences
        """
        try:
            # Korean sentence endings
            sentence_endings = re.compile(r'[.!?。！？]\s*')
            sentences = sentence_endings.split(text)
            
            # Clean sentences
            sentences = [s.strip() for s in sentences if s.strip()]
            
            return sentences
            
        except Exception as e:
            logger.warning(f"Error splitting sentences: {e}")
            return [text]
    
    def preprocess_for_embedding(self, text: str) -> str:
        """
        Preprocess text for embedding.
        
        Args:
            text: Input text
            
        Returns:
            Preprocessed text
        """
        try:
            # Tokenize and rejoin with proper spacing
            tokens = self.tokenize(text)
            
            # Join tokens with spaces
            processed_text = " ".join(tokens)
            
            # Normalize spacing
            processed_text = self.whitespace_pattern.sub(' ', processed_text)
            
            return processed_text.strip()
            
        except Exception as e:
            logger.warning(f"Error preprocessing text: {e}")
            return text
