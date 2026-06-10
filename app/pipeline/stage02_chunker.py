import re
import json
from pathlib import Path
from typing import List, Tuple
from app.models.schemas import ChunkManifest, ChunkManifestEntry, ChunkSummary
from app.utils.logger import logger

class SmartChunker:
    def __init__(self, target_words: int = 7000, max_words: int = 10000):
        self.target_words = target_words
        self.max_words = max_words

    def get_word_count(self, text: str) -> int:
        return len(text.split())
        
    def validate_chunks(self, original_text: str, chunks: List[str]) -> bool:
        orig_words = self.get_word_count(original_text)
        chunk_words = sum(self.get_word_count(c) for c in chunks)
        
        # Empty chunk check
        for i, c in enumerate(chunks):
            if self.get_word_count(c) < 100:
                logger.error(f"Validation Failed: Chunk {i+1} has < 100 words.")
                return False
                
        # Max words check (Allowing a tiny 10% buffer for unbreakable paragraphs)
        for i, c in enumerate(chunks):
            if self.get_word_count(c) > self.max_words * 1.1:
                logger.error(f"Validation Failed: Chunk {i+1} exceeds max words limit ({self.get_word_count(c)}).")
                return False
                
        # Text loss check (max 1% variance allowed)
        diff = abs(orig_words - chunk_words)
        margin = max(1, orig_words * 0.01)
        if diff > margin:
            logger.error(f"Validation Failed: Text loss detected! Original: {orig_words}, Chunks: {chunk_words}")
            return False
            
        logger.info(f"Chunk Validation Passed! (Original: {orig_words} words -> Chunks: {chunk_words} words)")
        return True

    def chunk_text(self, text: str) -> List[str]:
        # Split by double newline preserving single newlines
        paragraphs = re.split(r'\n\s*\n', text)
        chunks = []
        current_chunk = []
        current_words = 0
        
        for p in paragraphs:
            p = p.strip()
            if not p: continue
            
            words = self.get_word_count(p)
            is_chapter = bool(re.match(r'^(chapter|ch\.|episode|volume)\s*\d+', p, re.IGNORECASE))
            
            # Condition 1: Chapter boundary and decent word count reached
            if is_chapter and current_words >= self.target_words * 0.75:
                chunks.append("\n\n".join(current_chunk))
                current_chunk = [p]
                current_words = words
                continue
                
            # Condition 2: Hard limit reached, force split
            if current_words + words > self.max_words:
                if current_chunk:
                    chunks.append("\n\n".join(current_chunk))
                    current_chunk = [p]
                    current_words = words
                else:
                    # Single paragraph is larger than max_words (very rare)
                    current_chunk.append(p)
                    current_words += words
                continue
                
            current_chunk.append(p)
            current_words += words
            
        if current_chunk:
            chunks.append("\n\n".join(current_chunk))
            
        return chunks

class Stage02Chunker:
    def __init__(self, project_path: Path):
        self.project_path = project_path
        self.script_path = project_path / "script.txt"
        self.chunks_dir = project_path / "chunks"
        self.chunker = SmartChunker()
        
    def run(self):
        logger.info("Executing Stage 02: Smart Chunker")
        if not self.script_path.exists():
            raise FileNotFoundError(f"Missing {self.script_path}")
            
        with open(self.script_path, "r", encoding="utf-8") as f:
            text = f.read()
            
        chunks = self.chunker.chunk_text(text)
        
        if not self.chunker.validate_chunks(text, chunks):
            raise ValueError("Chunk validation failed! Data loss detected.")
            
        self.chunks_dir.mkdir(parents=True, exist_ok=True)
        
        manifest = ChunkManifest(
            total_chunks=len(chunks),
            total_words=sum(self.chunker.get_word_count(c) for c in chunks)
        )
        
        for i, chunk_text in enumerate(chunks):
            chunk_id = i + 1
            filename = f"chunk_{chunk_id:04d}.txt"
            filepath = self.chunks_dir / filename
            
            with open(filepath, "w", encoding="utf-8") as f:
                f.write(chunk_text)
                
            # Create stub summary
            summary = ChunkSummary(
                chunk_id=chunk_id,
                word_count=self.chunker.get_word_count(chunk_text)
            )
            summary_filename = f"chunk_{chunk_id:04d}_summary.json"
            with open(self.chunks_dir / summary_filename, "w", encoding="utf-8") as f:
                f.write(summary.model_dump_json(indent=2))
                
            # Append to manifest
            manifest.chunks.append(ChunkManifestEntry(
                id=chunk_id,
                file=filename,
                word_count=summary.word_count,
                previous_chunk=(chunk_id - 1) if chunk_id > 1 else None,
                next_chunk=(chunk_id + 1) if chunk_id < len(chunks) else None
            ))
            
        with open(self.chunks_dir / "chunk_manifest.json", "w", encoding="utf-8") as f:
            f.write(manifest.model_dump_json(indent=2))
            
        logger.info(f"Successfully generated {len(chunks)} chunks and chunk_manifest.json.")
