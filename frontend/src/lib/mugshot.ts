import { SAMPLE_INTRUDER_PHOTO } from './sample_photo'

export function getForensicMugshot(
  badge?: string,
  status?: string,
  action?: string,
  ip?: string
): string {
  const badgeStr = String(badge || '')
  const statusStr = String(status || '')

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

  // Authentic Photographic Sample Mugshot matching Forensic Dossier (from user sample)
  return SAMPLE_INTRUDER_PHOTO
}
