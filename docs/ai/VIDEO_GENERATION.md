# Video Generation & Assembly

## Overview
The final video is stitched together in `Stage13FFmpegAssembly` using outputs from the Image (SDXL/Flux) and Audio (Kokoro TTS) pipelines.

## Logic Flow
1. **Audio Sync**: TTS narration files are generated first. The exact millisecond duration of each `.wav` file dictates exactly how long its corresponding image remains on screen.
2. **Ken Burns Effect**: FFmpeg applies dynamic pan and zoom filters (e.g., zooming into the center of an image slowly over 6 seconds) to create the illusion of animation.
3. **Subtitles**: `Stage18SubtitleGen` generates an `.srt` file mapped directly to the TTS cadence.
4. **Export**: FFmpeg multiplexes the Video Stream, Audio Stream, Subtitles, and background music into the final `final_video.mp4`.
