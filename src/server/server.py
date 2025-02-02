from typing import ClassVar, Optional

from fastapi import HTTPException
from pywhispercpp.model import Model


class WhisperServer:
    _instance: ClassVar[Optional["WhisperServer"]] = None
    _model: Optional[Model] = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self, model_name: str = "base.en"):
        """Initialize Whisper server with specified model"""
        # Only initialize if not already initialized
        if self._model is None:
            try:
                self._model = Model(
                    model_name,
                    print_realtime=False,
                    print_progress=False,
                )
            except Exception as e:
                raise RuntimeError(f"Failed to load Whisper model: {str(e)}")

    async def transcribe_audio(self, audio_file) -> list:
        """
        Transcribe audio file using Whisper model
        Returns list of transcription segments
        """
        try:
            result = self._model.transcribe(audio_file)
            return result
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Transcription failed: {str(e)}")
