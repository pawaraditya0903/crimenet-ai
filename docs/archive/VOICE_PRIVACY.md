# 🎙️ CrimeNet AI — Voice Processing & Client Privacy Charter (VOICE_PRIVACY.md)

**System Classification:** Local Browser-Sandboxed Voice Interface  
**Lead Architect:** Aditya Pawar  

---

## 1. Zero Cloud Audio Transmission Policy

CrimeNet AI strictly adheres to client-side data minimization principles for all voice and biometric features:

* **Local Audio Processing:** Voice recognition is executed locally through the user's browser via the native **W3C Web Speech API (`SpeechRecognition` / `webkitSpeechRecognition`)**.
* **Zero Audio Uploads:** Raw audio files, ambient room recordings, and voice waveforms are **never transmitted to external cloud servers, third-party speech APIs, or saved to disk**.
* **Transient Memory:** Audio buffers are captured into volatile browser memory during speech recognition and cleared immediately upon transcript completion.

---

## 2. Text-to-Speech (TTS) Privacy

Voice playback is generated using the client browser's native **SpeechSynthesis API**:
* No speech synthesis requests leave the user's browser.
* Pitch, rate, and voice accents are rendered natively using the operating system's built-in text-to-speech synthesizers (e.g., Microsoft David/Zira or macOS Siri/Samantha).

---

## 3. Hardware Permission Transparency

* **Microphone Access:** Requested on-demand only when clicking the 🎤 button.
* **Microphone Status Indicator:** A live pulsating red indicator and animated waveform explicitly notify the user whenever the microphone is active.
* **Revocation:** Microphone permissions can be revoked at any time via standard browser settings without degrading text chat capabilities.
