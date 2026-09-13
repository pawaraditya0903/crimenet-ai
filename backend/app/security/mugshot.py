import urllib.parse
from typing import Optional

def generate_forensic_mugshot(
    badge: Optional[str] = None,
    status: Optional[str] = None,
    action: Optional[str] = None,
    ip: Optional[str] = None
) -> str:
    """Generates a high-resolution, vector-rendered forensic surveillance capture mugshot
    with spatiotemporal telemetry HUD overlays, biometric bounding boxes, and camera watermarks.
    """
    badge_str = str(badge or "")
    status_str = str(status or "")
    action_str = str(action or "")
    ip_str = str(ip or "127.0.0.1")

    is_authorized = (
        "AUTHORIZED" in status_str.upper()
        or "ADITYA" in badge_str.upper()
        or "OFFICER" in badge_str.upper()
    )

    if is_authorized:
        # ── VERIFIED LAW ENFORCEMENT OFFICER PORTRAIT ──
        svg = f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 240 240" width="240" height="240">
  <defs>
    <radialGradient id="officerBg" cx="50%" cy="40%" r="70%">
      <stop offset="0%" stop-color="#0c2340"/>
      <stop offset="60%" stop-color="#071526"/>
      <stop offset="100%" stop-color="#020813"/>
    </radialGradient>
    <linearGradient id="shieldGrad" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#38bdf8"/>
      <stop offset="100%" stop-color="#1d4ed8"/>
    </linearGradient>
  </defs>
  <rect width="240" height="240" rx="12" fill="url(#officerBg)"/>
  
  <!-- Subtle HUD Biometric Grid -->
  <line x1="20" y1="60" x2="220" y2="60" stroke="rgba(56,189,248,0.12)" stroke-width="1"/>
  <line x1="20" y1="120" x2="220" y2="120" stroke="rgba(56,189,248,0.12)" stroke-width="1"/>
  <line x1="20" y1="180" x2="220" y2="180" stroke="rgba(56,189,248,0.12)" stroke-width="1"/>
  <line x1="60" y1="20" x2="60" y2="220" stroke="rgba(56,189,248,0.12)" stroke-width="1"/>
  <line x1="120" y1="20" x2="120" y2="220" stroke="rgba(56,189,248,0.12)" stroke-width="1"/>
  <line x1="180" y1="20" x2="180" y2="220" stroke="rgba(56,189,248,0.12)" stroke-width="1"/>

  <!-- Tactical Officer Silhouette -->
  <!-- Shoulders & Uniform -->
  <path d="M40 225 Q120 180 200 225 L200 240 L40 240 Z" fill="#1e293b"/>
  <path d="M65 210 Q120 175 175 210 L195 240 L45 240 Z" fill="#0f172a" stroke="#38bdf8" stroke-width="1.5"/>
  <!-- Neck -->
  <rect x="106" y="140" width="28" height="35" rx="4" fill="#334155"/>
  <!-- Head & Face Profile -->
  <ellipse cx="120" cy="105" rx="36" ry="46" fill="#1e293b" stroke="#38bdf8" stroke-width="2"/>
  <!-- Tactical Officer Cap -->
  <path d="M78 88 Q120 62 162 88 L170 94 Q120 78 70 94 Z" fill="#0284c7"/>
  <path d="M74 86 Q120 50 166 86 L158 72 Q120 44 82 72 Z" fill="#0369a1"/>
  <polygon points="120,62 124,70 116,70" fill="#facc15"/>
  
  <!-- Biometric Landmark Face Points -->
  <circle cx="106" cy="104" r="3.5" fill="#38bdf8"/>
  <circle cx="134" cy="104" r="3.5" fill="#38bdf8"/>
  <circle cx="120" cy="116" r="2.5" fill="#38bdf8"/>
  <path d="M110 130 Q120 136 130 130" stroke="#38bdf8" stroke-width="2" fill="none"/>
  
  <!-- Facial Mesh Triangulation Wireframe -->
  <polygon points="106,104 134,104 120,116" fill="none" stroke="rgba(56,189,248,0.3)" stroke-width="1"/>
  <polygon points="106,104 120,116 110,130" fill="none" stroke="rgba(56,189,248,0.3)" stroke-width="1"/>
  <polygon points="134,104 120,116 130,130" fill="none" stroke="rgba(56,189,248,0.3)" stroke-width="1"/>

  <!-- Biometric Bounding Box (Cyan) -->
  <path d="M75 55 L65 55 L65 65" stroke="#38bdf8" stroke-width="2.5" fill="none"/>
  <path d="M165 55 L175 55 L175 65" stroke="#38bdf8" stroke-width="2.5" fill="none"/>
  <path d="M65 155 L65 165 L75 165" stroke="#38bdf8" stroke-width="2.5" fill="none"/>
  <path d="M175 155 L175 165 L165 165" stroke="#38bdf8" stroke-width="2.5" fill="none"/>

  <!-- Top Badge Overlay -->
  <rect x="12" y="10" width="138" height="18" rx="4" fill="rgba(2,132,199,0.85)"/>
  <text x="18" y="23" font-family="monospace" font-size="9.5" font-weight="900" fill="#ffffff">POLICE ID: ADITYA PAWAR</text>

  <!-- Bottom Verification Ribbon -->
  <rect x="12" y="210" width="216" height="20" rx="4" fill="rgba(16,185,129,0.9)"/>
  <text x="120" y="224" font-family="sans-serif" font-size="9" font-weight="900" fill="#ffffff" text-anchor="middle">✓ VERIFIED CHIEF INVESTIGATOR</text>
</svg>"""
    else:
        # ── CLASSIFIED CCTV INFRARED INTRUDER MUGSHOT ──
        # Generate varied silhouette based on IP
        seed_num = sum(ord(c) for c in ip_str) % 3
        cctv_chan = f"CAM-0{seed_num + 2}"
        threat_level = "CRITICAL PROBE" if "5 FAILS" in status_str.upper() or "429" in status_str.upper() else "SUSPECT DETECTED"

        svg = f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 240 240" width="240" height="240">
  <defs>
    <radialGradient id="intruderBg" cx="50%" cy="45%" r="70%">
      <stop offset="0%" stop-color="#2d0a0a"/>
      <stop offset="60%" stop-color="#160303"/>
      <stop offset="100%" stop-color="#050101"/>
    </radialGradient>
    <linearGradient id="scanline" x1="0" y1="0" x2="0" y2="100%">
      <stop offset="0%" stop-color="rgba(239,68,68,0)"/>
      <stop offset="50%" stop-color="rgba(239,68,68,0.15)"/>
      <stop offset="100%" stop-color="rgba(239,68,68,0)"/>
    </linearGradient>
  </defs>
  <rect width="240" height="240" rx="12" fill="url(#intruderBg)"/>

  <!-- CCTV Scanlines -->
  <line x1="0" y1="30" x2="240" y2="30" stroke="rgba(239,68,68,0.08)" stroke-width="1"/>
  <line x1="0" y1="60" x2="240" y2="60" stroke="rgba(239,68,68,0.08)" stroke-width="1"/>
  <line x1="0" y1="90" x2="240" y2="90" stroke="rgba(239,68,68,0.08)" stroke-width="1"/>
  <line x1="0" y1="120" x2="240" y2="120" stroke="rgba(239,68,68,0.08)" stroke-width="1"/>
  <line x1="0" y1="150" x2="240" y2="150" stroke="rgba(239,68,68,0.08)" stroke-width="1"/>
  <line x1="0" y1="180" x2="240" y2="180" stroke="rgba(239,68,68,0.08)" stroke-width="1"/>
  <line x1="0" y1="210" x2="240" y2="210" stroke="rgba(239,68,68,0.08)" stroke-width="1"/>

  <!-- Hooded Intruder Silhouette -->
  <!-- Body / Hoodie Shoulders -->
  <path d="M35 235 Q120 170 205 235 L205 240 L35 240 Z" fill="#1c0707"/>
  <path d="M60 215 Q120 165 180 215 L195 240 L45 240 Z" fill="#2d0a0a" stroke="#ef4444" stroke-width="1.5"/>
  <!-- Hood Profile -->
  <path d="M72 135 C65 70 85 45 120 45 C155 45 175 70 168 135 C162 165 145 175 120 175 C95 175 78 165 72 135 Z" fill="#120404" stroke="#ef4444" stroke-width="1.8"/>
  <!-- Dark Shadow Face Interior -->
  <ellipse cx="120" cy="118" rx="26" ry="34" fill="#000000"/>
  <!-- Thermal / Mask / Glowing Sensor Glint -->
  <ellipse cx="110" cy="112" rx="4" ry="2" fill="#ef4444" opacity="0.85"/>
  <ellipse cx="130" cy="112" rx="4" ry="2" fill="#ef4444" opacity="0.85"/>
  <path d="M102 128 Q120 136 138 128" stroke="rgba(239,68,68,0.6)" stroke-width="1.5" fill="none"/>

  <!-- Biometric Face Bounding Box with Red Target Brackets -->
  <path d="M60 50 L48 50 L48 62" stroke="#ef4444" stroke-width="3" fill="none"/>
  <path d="M180 50 L192 50 L192 62" stroke="#ef4444" stroke-width="3" fill="none"/>
  <path d="M48 168 L48 180 L60 180" stroke="#ef4444" stroke-width="3" fill="none"/>
  <path d="M192 168 L192 180 L180 180" stroke="#ef4444" stroke-width="3" fill="none"/>

  <!-- Target Crosshair on Face -->
  <circle cx="120" cy="116" r="48" stroke="rgba(239,68,68,0.35)" stroke-width="1" stroke-dasharray="6 6" fill="none"/>
  <line x1="120" y1="62" x2="120" y2="76" stroke="#ef4444" stroke-width="1.5"/>
  <line x1="120" y1="156" x2="120" y2="170" stroke="#ef4444" stroke-width="1.5"/>
  <line x1="66" y1="116" x2="80" y2="116" stroke="#ef4444" stroke-width="1.5"/>
  <line x1="160" y1="116" x2="174" y2="116" stroke="#ef4444" stroke-width="1.5"/>

  <!-- Camera & Recording HUD Header -->
  <circle cx="20" cy="18" r="5" fill="#ef4444"/>
  <text x="32" y="22" font-family="monospace" font-size="9.5" font-weight="900" fill="#f87171">REC [{cctv_chan}]</text>
  <text x="228" y="22" font-family="monospace" font-size="8.5" font-weight="700" fill="#94a3b8" text-anchor="end">{ip_str[:15]}</text>

  <!-- Bottom Alert Stamp -->
  <rect x="12" y="210" width="216" height="20" rx="4" fill="rgba(220,38,38,0.95)"/>
  <text x="120" y="224" font-family="sans-serif" font-size="9" font-weight="900" fill="#ffffff" text-anchor="middle">🚨 {threat_level} — MUGSHOT CAPTURED</text>
</svg>"""

    return "data:image/svg+xml;utf8," + urllib.parse.quote(svg)
