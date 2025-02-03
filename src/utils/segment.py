from typing import List

from pywhispercpp.model import Segment


def list_of_segments_to_text(segments: List[Segment]) -> str:
    return " ".join([segment.text for segment in segments])


def list_of_segments_to_text_with_timestamps(segments: List[Segment]) -> str:
    return " ".join([f"[{segment.t0}-{segment.t1}] {segment.text}" for segment in segments])
