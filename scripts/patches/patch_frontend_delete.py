with open(r"c:\Users\Aditya\Downloads\SIH 2026\frontend\src\App.tsx", "r", encoding="utf-8-sig") as f:
    code = f.read().replace("\ufeff", "")

# Add delete handler functions
delete_handlers = """
  const handleDeleteSingleLog = async (logItem: any, e: React.MouseEvent) => {
    e.stopPropagation()
    if (!confirm('Are you sure you want to delete this log entry?')) return
    try {
      await axios.post('/api/security/delete-log', {
        id: logItem.id || '',
        timestamp: logItem.timestamp || ''
      })
      setAuditLogs((prev) => prev.filter((item) => item.timestamp !== logItem.timestamp && item.id !== logItem.id))
    } catch(err) {
      alert('Error deleting log')
    }
  }

  const handleClearAllLogs = async () => {
    if (!confirm('⚠️ WARNING: Delete ALL intruder photos and IP logs?')) return
    try {
      await axios.post('/api/security/clear-all-logs')
      setAuditLogs([])
    } catch(err) {
      alert('Error clearing logs')
    }
  }
"""

if "handleDeleteSingleLog" not in code:
    code = code.replace("const openAuditLogs =", delete_handlers + "\n  const openAuditLogs =")

    # Replace table headers to include Actions
    code = code.replace(
        '<th style={{ padding: \'10px\' }}>Intruder Mugshot</th>',
        '<th style={{ padding: \'10px\' }}>Intruder Mugshot</th>\n                    <th style={{ padding: \'10px\', textAlign: \'center\' }}>Action</th>'
    )

    # Replace table row to include Delete button
    row_delete_btn = """<td style={{ padding: '10px', textAlign: 'center' }}>
                        <button
                          onClick={(e) => handleDeleteSingleLog(log, e)}
                          title="Delete this record"
                          style={{ background: 'rgba(239, 68, 68, 0.2)', border: '1px solid #ef4444', color: '#f87171', padding: '4px 8px', borderRadius: 6, cursor: 'pointer', fontSize: 12 }}
                        >
                          🗑️
                        </button>
                      </td>"""

    code = code.replace(
        '<span style={{ color: \'#64748b\', fontSize: 10 }}>No Photo</span>\n                        )}\n                      </td>',
        '<span style={{ color: \'#64748b\', fontSize: 10 }}>No Photo</span>\n                        )}\n                      </td>\n                      ' + row_delete_btn
    )

    # Add Clear All Logs button next to Close button in modal header
    header_buttons = """<div style={{ display: 'flex', gap: 8 }}>
                <button onClick={handleClearAllLogs} style={{ background: '#7f1d1d', border: '1px solid #ef4444', color: 'white', padding: '6px 12px', borderRadius: 6, cursor: 'pointer', fontSize: 11, fontWeight: 700 }}>🗑️ Clear All Logs</button>
                <button onClick={() => setAuditModalOpen(false)} style={{ background: '#334155', border: 'none', color: 'white', padding: '6px 12px', borderRadius: 6, cursor: 'pointer' }}>✕ Close</button>
              </div>"""

    code = code.replace(
        '<button onClick={() => setAuditModalOpen(false)} style={{ background: \'#334155\', border: \'none\', color: \'white\', padding: \'6px 12px\', borderRadius: 6, cursor: \'pointer\' }}>✕ Close</button>',
        header_buttons
    )

with open(r"c:\Users\Aditya\Downloads\SIH 2026\frontend\src\App.tsx", "w", encoding="utf-8") as f:
    f.write(code)

print("Frontend delete buttons added!")
