from typing import List, Optional, Dict
from pydantic import BaseModel, Field

class CharacterFingerprint(BaseModel):
    hair: str
    eyes: str
    face: str
    skin: str
    body: str
    clothing: str

class CharacterVersion(BaseModel):
    version: int
    chapter_start: int
    chapter_end: int
    age: str
    clothes: str

class CharacterSnapshot(BaseModel):
    id: str
    canonical_name: str
    version: int
    chapter_start: int
    chapter_end: int
    age: str
    clothes: str
    hair: str
    eyes: str
    face: str
    skin: str
    body: str
    clothing: str

class CharacterRegistryEntry(BaseModel):
    id: str
    canonical_name: str
    aliases: List[str] = Field(default_factory=list)
    fingerprint: Optional[CharacterFingerprint] = None
    reference_image: Optional[str] = None
    versions: List[CharacterVersion] = Field(default_factory=list)
    fingerprint_confidence: float = 1.0
    needs_review: bool = False

class Scene(BaseModel):
    scene_id: int
    chapter: str
    chunk: int
    narration: str
    tts_text: str
    word_count: int
    start_time: float = 0.0
    end_time: float = 0.0
    duration: float = 0.0
    characters: List[str]
    location: str
    emotion: str
    camera: str
    image_prompt: str
    prompt_version: str = "1.0"
    generator_version: str = "0.2.1"
    prompt_hash: Optional[str] = None

class VerificationScores(BaseModel):
    character_consistency: int
    scene_accuracy: int
    composition: int
    image_quality: int

class SceneStatus(BaseModel):
    scene_id: int
    status: str  # "passed", "failed"
    attempts: int = 1
    scores: Optional[VerificationScores] = None
    reason: Optional[str] = None
    word_count: Optional[int] = None
    estimated_duration: Optional[float] = None
    density_score: Optional[float] = None
    prompt_hash: Optional[str] = None

class ChunkManifestEntry(BaseModel):
    id: int
    file: str
    word_count: int
    start_chapter: Optional[int] = None
    end_chapter: Optional[int] = None
    previous_chunk: Optional[int] = None
    next_chunk: Optional[int] = None

class ChunkManifest(BaseModel):
    total_chunks: int = 0
    total_words: int = 0
    chunk_size_target: int = 7000
    chunks: List[ChunkManifestEntry] = Field(default_factory=list)

class ChunkSummary(BaseModel):
    chunk_id: int
    characters: List[str] = Field(default_factory=list)
    locations: List[str] = Field(default_factory=list)
    word_count: int = 0

class TimelineEntry(BaseModel):
    scene: str
    duration: float
    image: str
    audio: str

class ProjectInfo(BaseModel):
    novel_name: str
    part: int = 1
    created: str
    
    # Generation Statistics
    chapters: int = 0
    chunks: int = 0
    scenes: int = 0
    images_generated: int = 0
    images_failed: int = 0
    audio_generated: int = 0
    video_duration_seconds: float = 0.0
    prompt_version: str = "1.0"

class ProjectManifest(BaseModel):
    project: str
    completed_stage: int = 0
    last_scene: Optional[int] = None
    last_image: Optional[int] = None
    last_audio: Optional[int] = None
    
    # Cost Tracking
    gemini_requests: int = 0
    estimated_tokens: int = 0
    gemini_input_tokens: int = 0
    gemini_output_tokens: int = 0
    estimated_cost: float = 0.0
    images_generated: int = 0
    flux_rerenders: int = 0

class ProductionReport(BaseModel):
    total_words: int
    chunks: int
    scenes: int
    images_generated: int
    flux_rerenders: int
    video_length: str
    generation_time: str
    success_rate: float

class SceneManifest(BaseModel):
    total_scenes: int = 0
    completed_images: int = 0
    completed_audio: int = 0
    last_generated_scene: Optional[int] = None
    verified_scenes: Dict[int, SceneStatus] = Field(default_factory=dict)

class SeriesManifest(BaseModel):
    latest_part: int = 1
    total_scenes: int = 0
    characters: int = 0

class ThumbnailCandidate(BaseModel):
    file: str
    score: float
