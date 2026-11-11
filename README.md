
# Andheri Dastaan AI Video Studio — Free-first MVP

## What works in this first build
- Mobile-friendly Streamlit interface
- Hindi horror story idea → starter narration + scene breakdown
- Visual prompts per scene
- Upload scene images in order
- Render a basic MP4 using FFmpeg (uploaded images or cinematic text-cards)
- Download script, scene prompt JSON and MP4

## Important limitations
This is a functional first MVP, not yet a full generative video engine.
- It does not generate AI images/video clips automatically yet.
- It does not currently synthesize a Hindi voice track.
- Google Flow/PixVerse are not API-connected; their free account interfaces and credits vary.
- YouTube upload/OAuth is not connected.

## Run locally (Windows)
1. Install Python 3.11+ and FFmpeg.
2. Extract this ZIP.
3. Open Command Prompt in this folder:
   `py -m venv .venv`
   `.venv\Scripts\activate`
   `pip install -r requirements.txt`
   `streamlit run app.py`
4. Open the local URL shown by Streamlit.

## Mobile use
For phone access, deploy the project to a private Streamlit Community Cloud app (GitHub account required). Add the repository and choose `app.py`. Cloud deployment may need an FFmpeg buildpack/system package configuration; local rendering is the reliable first test.

## Free next steps
1. Connect an available free image model/API or add a manual image import step from a free generator.
2. Add TTS with a supported free engine and render voiceover.
3. Add subtitle timing, ambience and sound effects.
4. Add optional YouTube OAuth with explicit upload approval.
