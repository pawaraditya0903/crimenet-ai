export function getForensicMugshot(
  badge?: string,
  status?: string,
  action?: string,
  ip?: string
): string {
  const badgeStr = String(badge || '')
  const statusStr = String(status || '')
  const ipStr = String(ip || '127.0.0.1')

  const isAuthorized =
    statusStr.toUpperCase().includes('AUTHORIZED') ||
    badgeStr.toUpperCase().includes('ADITYA') ||
    badgeStr.toUpperCase().includes('OFFICER')

  if (isAuthorized) {
    // Verified Officer Portrait
    const svg = `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 240 240" width="240" height="240">
  <defs>
    <radialGradient id="officerBg" cx="50%" cy="40%" r="70%">
      <stop offset="0%" stop-color="#0c2340"/>
      <stop offset="60%" stop-color="#071526"/>
      <stop offset="100%" stop-color="#020813"/>
    </radialGradient>
  </defs>
  <rect width="240" height="240" rx="12" fill="url(#officerBg)"/>
  <line x1="20" y1="60" x2="220" y2="60" stroke="rgba(56,189,248,0.15)" stroke-width="1"/>
  <line x1="20" y1="120" x2="220" y2="120" stroke="rgba(56,189,248,0.15)" stroke-width="1"/>
  <line x1="20" y1="180" x2="220" y2="180" stroke="rgba(56,189,248,0.15)" stroke-width="1"/>
  <line x1="60" y1="20" x2="60" y2="220" stroke="rgba(56,189,248,0.15)" stroke-width="1"/>
  <line x1="120" y1="20" x2="120" y2="220" stroke="rgba(56,189,248,0.15)" stroke-width="1"/>
  <line x1="180" y1="20" x2="180" y2="220" stroke="rgba(56,189,248,0.15)" stroke-width="1"/>
  <path d="M40 225 Q120 180 200 225 L200 240 L40 240 Z" fill="#1e293b"/>
  <path d="M65 210 Q120 175 175 210 L195 240 L45 240 Z" fill="#0f172a" stroke="#38bdf8" stroke-width="1.5"/>
  <rect x="106" y="140" width="28" height="35" rx="4" fill="#334155"/>
  <ellipse cx="120" cy="105" rx="36" ry="46" fill="#1e293b" stroke="#38bdf8" stroke-width="2"/>
  <path d="M78 88 Q120 62 162 88 L170 94 Q120 78 70 94 Z" fill="#0284c7"/>
  <path d="M74 86 Q120 50 166 86 L158 72 Q120 44 82 72 Z" fill="#0369a1"/>
  <polygon points="120,62 124,70 116,70" fill="#facc15"/>
  <circle cx="106" cy="104" r="3.5" fill="#38bdf8"/>
  <circle cx="134" cy="104" r="3.5" fill="#38bdf8"/>
  <circle cx="120" cy="116" r="2.5" fill="#38bdf8"/>
  <path d="M110 130 Q120 136 130 130" stroke="#38bdf8" stroke-width="2" fill="none"/>
  <polygon points="106,104 134,104 120,116" fill="none" stroke="rgba(56,189,248,0.35)" stroke-width="1"/>
  <polygon points="106,104 120,116 110,130" fill="none" stroke="rgba(56,189,248,0.35)" stroke-width="1"/>
  <polygon points="134,104 120,116 130,130" fill="none" stroke="rgba(56,189,248,0.35)" stroke-width="1"/>
  <path d="M75 55 L65 55 L65 65" stroke="#38bdf8" stroke-width="2.5" fill="none"/>
  <path d="M165 55 L175 55 L175 65" stroke="#38bdf8" stroke-width="2.5" fill="none"/>
  <path d="M65 155 L65 165 L75 165" stroke="#38bdf8" stroke-width="2.5" fill="none"/>
  <path d="M175 155 L175 165 L165 165" stroke="#38bdf8" stroke-width="2.5" fill="none"/>
  <rect x="12" y="10" width="138" height="18" rx="4" fill="rgba(2,132,199,0.85)"/>
  <text x="18" y="23" font-family="monospace" font-size="9.5" font-weight="900" fill="#ffffff">POLICE ID: ADITYA PAWAR</text>
  <rect x="12" y="210" width="216" height="20" rx="4" fill="rgba(16,185,129,0.9)"/>
  <text x="120" y="224" font-family="sans-serif" font-size="9" font-weight="900" fill="#ffffff" text-anchor="middle">✓ VERIFIED CHIEF INVESTIGATOR</text>
</svg>`
    return `data:image/svg+xml;utf8,${encodeURIComponent(svg)}`
  }

  // Infrared CCTV Intruder Mugshot
  const seedNum = (ipStr.split('').reduce((acc, c) => acc + c.charCodeAt(0), 0)) % 4 + 1
  const threatText = statusStr.toUpperCase().includes('5 FAILS') || statusStr.toUpperCase().includes('429')
    ? 'CRITICAL PROBE'
    : 'SUSPECT DETECTED'

  const svg = `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 240 240" width="240" height="240">
  <defs>
    <radialGradient id="intruderBg" cx="50%" cy="40%" r="75%">
      <stop offset="0%" stop-color="#1e0505"/>
      <stop offset="50%" stop-color="#100202"/>
      <stop offset="100%" stop-color="#050101"/>
    </radialGradient>
    <pattern id="cctvScan" width="240" height="4" patternUnits="userSpaceOnUse">
      <rect width="240" height="2" fill="rgba(0,0,0,0.3)"/>
      <rect y="2" width="240" height="2" fill="rgba(239,68,68,0.03)"/>
    </pattern>
  </defs>
  <rect width="240" height="240" rx="12" fill="url(#intruderBg)"/>
  <rect width="240" height="240" rx="12" fill="url(#cctvScan)"/>

  <!-- High-Tech CCTV Biometric Grid Overlay -->
  <line x1="20" y1="60" x2="220" y2="60" stroke="rgba(239,68,68,0.1)" stroke-width="1"/>
  <line x1="20" y1="120" x2="220" y2="120" stroke="rgba(239,68,68,0.1)" stroke-width="1"/>
  <line x1="20" y1="180" x2="220" y2="180" stroke="rgba(239,68,68,0.1)" stroke-width="1"/>
  <line x1="60" y1="20" x2="60" y2="220" stroke="rgba(239,68,68,0.1)" stroke-width="1"/>
  <line x1="120" y1="20" x2="120" y2="220" stroke="rgba(239,68,68,0.1)" stroke-width="1"/>
  <line x1="180" y1="20" x2="180" y2="220" stroke="rgba(239,68,68,0.1)" stroke-width="1"/>

  <!-- Tactical Hooded Suspect Silhouette with Real Contours -->
  <path d="M20 240 L30 220 Q70 180 120 180 Q170 180 210 220 L220 240 Z" fill="#140404"/>
  <path d="M40 240 L50 222 Q85 190 120 190 Q155 190 190 222 L200 240 Z" fill="#0c0202" stroke="rgba(239,68,68,0.4)" stroke-width="1"/>

  <!-- Outer Deep Hood -->
  <path d="M68 150 C60 85 80 40 120 40 C160 40 180 85 172 150 C165 178 148 185 120 185 C92 185 75 178 68 150 Z" fill="#080101" stroke="#ef4444" stroke-width="1.8"/>

  <!-- Hood Interior Shadow Depth -->
  <path d="M78 145 C72 90 88 52 120 52 C152 52 168 90 162 145 C156 168 142 175 120 175 C98 175 84 168 78 145 Z" fill="#020000"/>

  <!-- Suspect Head Structure & Forehead in Shadow -->
  <ellipse cx="120" cy="115" rx="34" ry="44" fill="#150505"/>
  <path d="M92 95 Q120 82 148 95 L146 112 Q120 102 94 112 Z" fill="#1f0707"/>

  <!-- Realistic Eye Sockets in Shadow with Infrared Sensor Glint -->
  <ellipse cx="106" cy="108" rx="8" ry="4" fill="#050000"/>
  <ellipse cx="134" cy="108" rx="8" ry="4" fill="#050000"/>
  <circle cx="107" cy="108" r="2.2" fill="#ef4444"/>
  <circle cx="133" cy="108" r="2.2" fill="#ef4444"/>
  <circle cx="107.8" cy="107.2" r="0.7" fill="#ffffff"/>
  <circle cx="133.8" cy="107.2" r="0.7" fill="#ffffff"/>

  <!-- Realistic Nose Bridge & Shadow -->
  <path d="M120 105 L117 122 L124 123 Z" fill="#2d0a0a"/>

  <!-- Tactical Half-Mask / Balaclava Folds -->
  <path d="M94 125 C100 123 110 122 120 122 C130 122 140 123 146 125 C148 145 142 165 120 168 C98 165 92 145 94 125 Z" fill="#0a0202" stroke="rgba(239,68,68,0.5)" stroke-width="1.2"/>
  <path d="M102 135 Q120 138 138 135" stroke="rgba(239,68,68,0.25)" stroke-width="1" fill="none"/>
  <path d="M106 145 Q120 148 134 145" stroke="rgba(239,68,68,0.25)" stroke-width="1" fill="none"/>

  <!-- Biometric AFIS Facial Landmark Mesh (68-point representation) -->
  <circle cx="98" cy="100" r="1.5" fill="#f87171"/>
  <circle cx="142" cy="100" r="1.5" fill="#f87171"/>
  <circle cx="120" cy="94" r="1.5" fill="#f87171"/>
  <circle cx="120" cy="122" r="1.5" fill="#f87171"/>
  <circle cx="104" cy="155" r="1.5" fill="#f87171"/>
  <circle cx="136" cy="155" r="1.5" fill="#f87171"/>
  <circle cx="120" cy="168" r="1.5" fill="#f87171"/>
  <polygon points="98,100 120,94 142,100 134,108 120,122 106,108" fill="none" stroke="rgba(239,68,68,0.3)" stroke-width="0.8"/>
  <polygon points="106,108 120,122 104,155 120,168 136,155 134,108" fill="none" stroke="rgba(239,68,68,0.25)" stroke-width="0.8"/>

  <!-- Surveillance Face Bounding Box with Red Corner Brackets -->
  <path d="M55 45 L42 45 L42 58" stroke="#ef4444" stroke-width="3" fill="none"/>
  <path d="M185 45 L198 45 L198 58" stroke="#ef4444" stroke-width="3" fill="none"/>
  <path d="M42 172 L42 185 L55 185" stroke="#ef4444" stroke-width="3" fill="none"/>
  <path d="M198 172 L198 185 L185 185" stroke="#ef4444" stroke-width="3" fill="none"/>

  <!-- Crosshair Centering on Subject -->
  <line x1="120" y1="36" x2="120" y2="48" stroke="#ef4444" stroke-width="1.5"/>
  <line x1="120" y1="178" x2="120" y2="190" stroke="#ef4444" stroke-width="1.5"/>
  <line x1="32" y1="115" x2="44" y2="115" stroke="#ef4444" stroke-width="1.5"/>
  <line x1="196" y1="115" x2="208" y2="115" stroke="#ef4444" stroke-width="1.5"/>

  <!-- CCTV Recording Header -->
  <circle cx="20" cy="18" r="4.5" fill="#ef4444"/>
  <text x="30" y="22" font-family="monospace" font-size="9" font-weight="900" fill="#f87171">REC [CAM-0${seedNum}]</text>
  <text x="228" y="22" font-family="monospace" font-size="8.5" font-weight="700" fill="#cbd5e1" text-anchor="end">${ipStr.slice(0, 16)}</text>

  <!-- Telemetry Bar Above Footer -->
  <text x="120" y="202" font-family="monospace" font-size="7.5" font-weight="800" fill="#f87171" text-anchor="middle" letter-spacing="1">NO AFIS MATCH · UNIDENTIFIED SUBJECT</text>

  <!-- Bottom Incident Dossier Ribbon -->
  <rect x="10" y="208" width="220" height="22" rx="4" fill="rgba(220,38,38,0.95)"/>
  <text x="120" y="223" font-family="sans-serif" font-size="9" font-weight="900" fill="#ffffff" text-anchor="middle">🚨 ${threatText} — SURVEILLANCE CAPTURE</text>
</svg>`

  return `data:image/svg+xml;utf8,${encodeURIComponent(svg)}`
}
