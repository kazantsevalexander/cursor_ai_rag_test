"""
Speech-to-Text Service.
Handles voice message transcription without ffmpeg dependency.
"""

from pathlib import Path
from typing import Union

from services.openai_client import openai_client
from utils.logging import logger


async def transcribe_voice_message(audio_path: Union[str, Path]) -> str:
    """
    Transcribe a voice message to text.
    
    OpenAI Whisper API supports multiple formats including OGG, MP3, WAV, etc.
    No conversion needed!
    
    Args:
        audio_path: Path to audio file (OGG, MP3, WAV, etc.)
    
    Returns:
        Transcribed text
    """
    audio_path = Path(audio_path)
    
    try:
        logger.debug(f"Transcribing audio file: {audio_path}")
        
        # Whisper API supports OGG directly - no conversion needed!
        text = await openai_client.transcribe_audio(audio_path)
        
        logger.info(f"Transcription completed: {len(text)} characters")
        return text
        
    except Exception as e:
        logger.error(f"Error in voice transcription: {e}")
        raise

