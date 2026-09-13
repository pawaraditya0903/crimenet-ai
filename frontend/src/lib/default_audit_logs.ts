import { SAMPLE_MUGSHOT_ADITYA, SAMPLE_MUGSHOT_GIRL, SAMPLE_MUGSHOT_GUY } from './sample_photo'

export interface AuditLogEntry {
  id: string
  timestamp: string
  ip: string
  device: string
  action: string
  status: string
  badge: string
  photo: string
  epoch: number
}

export const CANONICAL_AUDIT_LOGS: AuditLogEntry[] = [
  {
    id: 'log-01',
    timestamp: '23-Aug-2026 15:50:56 IST',
    ip: '49.15.92.19',
    device: 'Mozilla/5.0 (Linux; Android 10; K) AppleWebKi',
    action: 'AUTHORIZED_ACCESS',
    status: 'AUTHORIZED',
    badge: 'INV-2026-AP01',
    photo: '',
    epoch: 1787480456
  },
  {
    id: 'log-02',
    timestamp: '23-Aug-2026 15:47:18 IST',
    ip: '122.170.196.117',
    device: 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) App',
    action: 'PASSCODE_AUTHORIZED',
    status: 'AUTHORIZED',
    badge: 'Chief Officer Aditya Pawar',
    photo: SAMPLE_MUGSHOT_ADITYA,
    epoch: 1787480238
  },
  {
    id: 'log-03',
    timestamp: '23-Aug-2026 15:45:52 IST',
    ip: '49.15.92.19',
    device: 'Mozilla/5.0 (Linux; Android 10; K) AppleWebKi',
    action: 'AUTHORIZED_ACCESS',
    status: 'AUTHORIZED',
    badge: 'INVESTIGATOR',
    photo: '',
    epoch: 1787480152
  },
  {
    id: 'log-04',
    timestamp: '23-Aug-2026 15:45:30 IST',
    ip: '49.15.92.19',
    device: 'Mozilla/5.0 (Linux; Android 10; K) AppleWebKi',
    action: 'PASSCODE_FAILED',
    status: 'BLOCKED_INTRUDER',
    badge: 'UNAUTHORIZED_PROBE',
    photo: SAMPLE_MUGSHOT_GIRL,
    epoch: 1787480130
  },
  {
    id: 'log-05',
    timestamp: '23-Aug-2026 15:45:20 IST',
    ip: '122.170.196.117',
    device: 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) App',
    action: 'PASSCODE_AUTHORIZED',
    status: 'AUTHORIZED',
    badge: 'Chief Officer Aditya Pawar',
    photo: SAMPLE_MUGSHOT_ADITYA,
    epoch: 1787480120
  },
  {
    id: 'log-06',
    timestamp: '23-Aug-2026 15:44:39 IST',
    ip: '122.170.196.117',
    device: 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) App',
    action: 'PASSCODE_AUTHORIZED',
    status: 'AUTHORIZED',
    badge: 'Chief Officer Aditya Pawar',
    photo: '',
    epoch: 1787480079
  },
  {
    id: 'log-07',
    timestamp: '23-Aug-2026 15:43:59 IST',
    ip: '49.15.92.19',
    device: 'Mozilla/5.0 (Linux; Android 10; K) AppleWebKi',
    action: 'INTRUDER_FACE_FAILED_0%',
    status: 'BLOCKED_INTRUDER',
    badge: 'PROBE_SUSPECT',
    photo: SAMPLE_MUGSHOT_GUY,
    epoch: 1787480039
  },
  {
    id: 'log-08',
    timestamp: '23-Aug-2026 15:43:39 IST',
    ip: '49.15.92.19',
    device: 'Mozilla/5.0 (Linux; Android 10; K) AppleWebKi',
    action: 'PASSCODE_FAILED',
    status: 'BLOCKED_INTRUDER',
    badge: 'UNKNOWN_PROBE',
    photo: '',
    epoch: 1787480019
  },
  {
    id: 'log-09',
    timestamp: '23-Aug-2026 15:43:35 IST',
    ip: '122.170.196.117',
    device: 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) App',
    action: 'PASSCODE_FAILED',
    status: 'BLOCKED_INTRUDER',
    badge: 'PROBE_ATTEMPT',
    photo: '',
    epoch: 1787480015
  },
  {
    id: 'log-10',
    timestamp: '23-Aug-2026 15:43:15 IST',
    ip: '49.15.92.19',
    device: 'Mozilla/5.0 (Linux; Android 10; K) AppleWebKi',
    action: 'PASSCODE_FAILED',
    status: 'BLOCKED_INTRUDER',
    badge: 'UNKNOWN_PROBE',
    photo: '',
    epoch: 1787479995
  },
  {
    id: 'log-11',
    timestamp: '23-Aug-2026 15:43:14 IST',
    ip: '49.15.92.19',
    device: 'Mozilla/5.0 (Linux; Android 10; K) AppleWebKi',
    action: 'PASSCODE_FAILED',
    status: 'BLOCKED_INTRUDER',
    badge: 'UNKNOWN_PROBE',
    photo: '',
    epoch: 1787479994
  },
  {
    id: 'log-12',
    timestamp: '23-Aug-2026 15:43:08 IST',
    ip: '49.15.92.19',
    device: 'Mozilla/5.0 (Linux; Android 10; K) AppleWebKi',
    action: 'PASSCODE_FAILED',
    status: 'BLOCKED_INTRUDER',
    badge: 'UNKNOWN_PROBE',
    photo: '',
    epoch: 1787479988
  }
]
