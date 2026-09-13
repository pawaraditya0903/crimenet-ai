import { SAMPLE_MUGSHOT_USER } from './sample_photo'

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
    timestamp: '30-Aug-2026 13:27:52 IST',
    ip: '122.170.193.133',
    device: 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) App',
    action: 'PAGE_VIEW',
    status: 'PAGE_VIEW',
    badge: 'REMOTE_VISITOR',
    photo: '',
    epoch: 1788076672
  },
  {
    id: 'log-02',
    timestamp: '30-Aug-2026 13:27:26 IST',
    ip: '122.170.193.133',
    device: 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) App',
    action: 'AUTHORIZED',
    status: 'AUTHORIZED',
    badge: 'Chief Officer Aditya Pawar',
    photo: '',
    epoch: 1788076646
  },
  {
    id: 'log-03',
    timestamp: '30-Aug-2026 13:27:18 IST',
    ip: '122.170.193.133',
    device: 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) App',
    action: 'PAGE_VIEW',
    status: 'PAGE_VIEW',
    badge: 'REMOTE_VISITOR',
    photo: '',
    epoch: 1788076638
  },
  {
    id: 'log-04',
    timestamp: '30-Aug-2026 13:25:39 IST',
    ip: '152.59.8.43',
    device: 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) App',
    action: 'PAGE_VIEW',
    status: 'PAGE_VIEW',
    badge: 'REMOTE_VISITOR',
    photo: '',
    epoch: 1788076539
  },
  {
    id: 'log-05',
    timestamp: '30-Aug-2026 13:24:08 IST',
    ip: '122.170.193.133',
    device: 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) App',
    action: 'AUTHORIZED',
    status: 'AUTHORIZED',
    badge: 'Chief Officer Aditya Pawar',
    photo: SAMPLE_MUGSHOT_USER,
    epoch: 1788076448
  },
  {
    id: 'log-06',
    timestamp: '30-Aug-2026 13:23:11 IST',
    ip: '122.170.193.133',
    device: 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) App',
    action: 'AUTHORIZED',
    status: 'AUTHORIZED',
    badge: 'Chief Officer Aditya Pawar',
    photo: '',
    epoch: 1788076391
  },
  {
    id: 'log-07',
    timestamp: '30-Aug-2026 13:23:02 IST',
    ip: '122.170.193.133',
    device: 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) App',
    action: 'PAGE_VIEW',
    status: 'PAGE_VIEW',
    badge: 'REMOTE_VISITOR',
    photo: '',
    epoch: 1788076382
  },
  {
    id: 'log-08',
    timestamp: '30-Aug-2026 13:04:51 IST',
    ip: '122.170.193.133',
    device: 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) App',
    action: 'AUTHORIZED',
    status: 'AUTHORIZED',
    badge: 'Chief Officer Aditya Pawar',
    photo: '',
    epoch: 1788075291
  },
  {
    id: 'log-09',
    timestamp: '23-Aug-2026 15:50:56 IST',
    ip: '49.15.92.19',
    device: 'Mozilla/5.0 (Linux; Android 10; K) AppleWebKi',
    action: 'AUTHORIZED',
    status: 'AUTHORIZED',
    badge: 'INV-2026-AP01',
    photo: '',
    epoch: 1787480456
  },
  {
    id: 'log-10',
    timestamp: '23-Aug-2026 15:47:18 IST',
    ip: '122.170.196.117',
    device: 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) App',
    action: 'AUTHORIZED',
    status: 'AUTHORIZED',
    badge: 'Chief Officer Aditya Pawar',
    photo: '',
    epoch: 1787480238
  },
  {
    id: 'log-11',
    timestamp: '23-Aug-2026 15:45:30 IST',
    ip: '49.15.92.19',
    device: 'Mozilla/5.0 (Linux; Android 10; K) AppleWebKi',
    action: 'PAGE_VIEW',
    status: 'PAGE_VIEW',
    badge: 'UNAUTHORIZED_PROBE',
    photo: '',
    epoch: 1787480130
  },
  {
    id: 'log-12',
    timestamp: '23-Aug-2026 15:43:59 IST',
    ip: '49.15.92.19',
    device: 'Mozilla/5.0 (Linux; Android 10; K) AppleWebKi',
    action: 'PAGE_VIEW',
    status: 'PAGE_VIEW',
    badge: 'PROBE_SUSPECT',
    photo: '',
    epoch: 1787480039
  }
]
