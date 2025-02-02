import asyncio
import tempfile
from typing import AsyncGenerator, Callable, ClassVar, Optional

import numpy as np
from fastapi import HTTPException, WebSocket, WebSocketDisconnect
from pywhispercpp.model import Model, Segment

from ..utils.logger import get_logger

logger = get_logger()


class WhisperServer:
    _instance: ClassVar[Optional["WhisperServer"]] = None
    _model: Optional[Model] = None
    HEARTBEAT_INTERVAL = 30  # seconds
    MIN_AUDIO_LENGTH = 16000  # 1 second at 16kHz

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
                    print_realtime=False,  # Disable printing, use callbacks instead
                    print_progress=False,
                    print_timestamps=False,
                    single_segment=True,  # Better for streaming
                    no_context=True,  # Don't use past transcriptions for streaming
                )
            except Exception as e:
                raise RuntimeError(f"Failed to load Whisper model: {str(e)}")

    def process_audio(self, buffer: bytearray) -> np.ndarray:
        """Convert raw audio bytes to normalized numpy array and pad if needed"""
        # Ensure buffer length is multiple of 2 (int16 = 2 bytes)
        if len(buffer) % 2 != 0:
            buffer = buffer[:-1]  # Remove last byte

        # Convert to int16 first
        samples = np.frombuffer(buffer, dtype=np.int16)

        # Pad with silence if too short
        if len(samples) < self.MIN_AUDIO_LENGTH:
            padding = np.zeros(self.MIN_AUDIO_LENGTH - len(samples), dtype=np.int16)
            samples = np.concatenate([samples, padding])

        # Normalize to float32 in range [-1, 1]
        audio_array = samples.astype(np.float32) / np.iinfo(np.int16).max
        return audio_array

    async def transcribe_websocket(self, websocket: WebSocket) -> AsyncGenerator[dict, None]:
        """Handle WebSocket connection for real-time transcription"""
        await websocket.accept()
        logger.info("WebSocket connection accepted")

        buffer = bytearray()
        total_chunks = 0
        last_end_time = 0
        seen_segments = set()

        # Create a synchronous callback that queues messages
        message_queue = asyncio.Queue()

        def segment_callback(segment: Segment):
            """Synchronous callback that queues messages"""
            nonlocal last_end_time

            # Create unique key for segment
            segment_key = f"{segment.text}:{segment.t0}:{segment.t1}"
            if segment_key in seen_segments:
                return  # Skip duplicate segments
            seen_segments.add(segment_key)

            # Ensure timing is monotonically increasing
            start_time = max(last_end_time, segment.t0)
            end_time = max(start_time + 0.1, segment.t1)
            last_end_time = end_time

            message = {
                "type": "transcription",
                "text": segment.text,
                "start": start_time,
                "end": end_time,
                "is_final": False,
            }
            logger.debug(f"New segment: {start_time:.2f}s -> {end_time:.2f}s: {segment.text}")
            asyncio.create_task(message_queue.put(message))

        try:
            while True:
                try:
                    chunk = await asyncio.wait_for(
                        websocket.receive_bytes(), timeout=self.HEARTBEAT_INTERVAL
                    )
                    total_chunks += 1

                    # Check if this is the final chunk
                    is_end = chunk[-4:] == b"END\n"
                    if is_end:
                        chunk = chunk[:-4]  # Remove END marker
                        logger.debug("Processing final chunk")

                    buffer.extend(chunk)
                    chunk_size = len(buffer)
                    logger.debug(f"Received chunk {total_chunks}, buffer size: {chunk_size} bytes")

                    # Calculate approximate duration based on buffer size
                    # 16-bit samples at 16kHz = 32000 bytes per second
                    approx_duration = chunk_size / 32000

                    # Process when buffer is large enough or we get END marker
                    if chunk_size >= self.MIN_AUDIO_LENGTH * 2 or is_end:
                        logger.info(
                            f"Processing buffer of size {chunk_size} bytes (~{approx_duration:.2f}s)"
                        )
                        try:
                            audio_data = self.process_audio(buffer)
                            result = self._model.transcribe(
                                audio_data, new_segment_callback=segment_callback
                            )

                            # Process all queued messages
                            while not message_queue.empty():
                                msg = await message_queue.get()
                                await websocket.send_json(msg)

                            # Send final result if we have one
                            if result and result[-1].text:
                                final_message = {
                                    "type": "transcription",
                                    "text": result[-1].text,
                                    "start": max(0, result[-1].t0),
                                    "end": max(result[-1].t0 + 0.1, result[-1].t1),
                                    "is_final": is_end,  # Only final if this is the last chunk
                                }
                                logger.debug(f"Sending message: {final_message}")
                                await websocket.send_json(final_message)
                                yield final_message

                            if is_end:
                                # Send an explicit final message
                                final_message = {
                                    "type": "transcription",
                                    "text": result[-1].text if result else "",
                                    "start": last_end_time,
                                    "end": last_end_time + 0.1,
                                    "is_final": True,
                                }
                                logger.info(f"Sending final message: {final_message}")
                                await websocket.send_json(final_message)
                                yield final_message
                                break

                        except Exception as e:
                            logger.error(f"Audio processing failed: {str(e)}")
                            raise
                        finally:
                            buffer.clear()

                except asyncio.TimeoutError:
                    try:
                        logger.debug("Sending heartbeat")
                        await websocket.send_json({"type": "heartbeat"})
                    except WebSocketDisconnect:
                        logger.info("WebSocket disconnected during heartbeat")
                        break
                except WebSocketDisconnect:
                    logger.info("WebSocket disconnected")
                    break

        except Exception as e:
            logger.error(f"Streaming failed: {str(e)}")
            await websocket.close()
            raise HTTPException(status_code=500, detail=f"Streaming failed: {str(e)}")
        finally:
            if buffer:
                buffer.clear()
            logger.info(f"WebSocket connection closed. Processed {total_chunks} chunks")

    async def transcribe_file(self, audio_file) -> list:
        """
        Transcribe audio file using Whisper model
        Returns list of transcription segments
        """
        try:
            # For files, we want all segments at once
            result = self._model.transcribe(
                audio_file,
                single_segment=False,  # Get all segments
                no_context=False,  # Use context for better accuracy
            )
            return result
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Transcription failed: {str(e)}")
