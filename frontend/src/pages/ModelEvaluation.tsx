import { useEffect, useState } from 'react'
import axios from 'axios'

export default function ModelEvaluation() {
  const [data, setData] = useState<any>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    axios.get('/api/models/evaluation')
      .then((res) => setData(res.data))
      .catch(() => {})
      .finally(() => setLoading(false))
  }, [])

  if (loading || !data) {
    return (
      <div style={{ color: '#38bdf8', padding: 30, textAlign: 'center', fontWeight: 800 }}>
        ⏳ Loading Synthetic Scientific Evaluation Benchmark Metrics...
      </div>
    )
  }

  const { dataset, supervised_anomaly_metrics, confusion_matrix, false_positive_analysis, deterministic_algorithms_calibration } = data

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: 20, paddingBottom: 40 }}>
      
      {/* HEADER BANNER */}
      <div style={{ background: 'rgba(15, 23, 42, 0.9)', padding: 20, borderRadius: 14, border: '1px solid #38bdf8' }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <div>
            <div style={{ fontSize: 16, fontWeight: 900, color: '#38bdf8', display: 'flex', alignItems: 'center', gap: 8 }}>
              <span>📈</span> SCIENTIFIC MODEL EVALUATION & TESTING BENCHMARK
            </div>
            <div style={{ fontSize: 11.5, color: '#cbd5e1', marginTop: 4 }}>
              Empirical testing metrics, train/test partitions, confusion matrix, and algorithmic calibration parameters.
            </div>
          </div>
          <div style={{ padding: '6px 14px', borderRadius: 8, background: '#78350f', color: '#fef08a', fontSize: 11, fontWeight: 800, border: '1px solid #f59e0b' }}>
            ⚠️ {dataset.classification}
          </div>
        </div>

        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: 10, marginTop: 14, background: '#020617', padding: 12, borderRadius: 10 }}>
          <div>
            <div style={{ fontSize: 10, color: '#64748b' }}>DATASET NAME</div>
            <div style={{ fontSize: 11.5, fontWeight: 800, color: 'white', marginTop: 2 }}>{dataset.name}</div>
          </div>
          <div>
            <div style={{ fontSize: 10, color: '#64748b' }}>TOTAL EVALUATION RECORDS</div>
            <div style={{ fontSize: 12, fontWeight: 800, color: '#38bdf8', marginTop: 2 }}>{dataset.total_records.toLocaleString()} Records</div>
          </div>
          <div>
            <div style={{ fontSize: 10, color: '#64748b' }}>DATASET SPLIT</div>
            <div style={{ fontSize: 11, fontWeight: 700, color: '#34d399', marginTop: 2 }}>{dataset.train_val_test_split}</div>
          </div>
          <div>
            <div style={{ fontSize: 10, color: '#64748b' }}>INJECTED ANOMALIES</div>
            <div style={{ fontSize: 12, fontWeight: 800, color: '#f87171', marginTop: 2 }}>{dataset.total_anomalies_present} Synthetic Events</div>
          </div>
        </div>
      </div>

      {/* 4 CORE ACCURACY METRICS */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: 14 }}>
        {[
          { label: 'Precision', val: `${(supervised_anomaly_metrics.precision * 100).toFixed(1)}%`, sub: 'Low False Positive Rate', color: '#34d399' },
          { label: 'Recall (Sensitivity)', val: `${(supervised_anomaly_metrics.recall * 100).toFixed(1)}%`, sub: 'High Anomaly Capture', color: '#38bdf8' },
          { label: 'F1-Score (Harmonic Mean)', val: supervised_anomaly_metrics.f1_score.toFixed(3), sub: 'Balanced Classification', color: '#a855f7' },
          { label: 'ROC-AUC Metric', val: supervised_anomaly_metrics.roc_auc.toFixed(3), sub: 'Separability Index', color: '#f59e0b' },
        ].map((m, idx) => (
          <div key={idx} style={{ background: 'rgba(15, 23, 42, 0.8)', padding: 18, borderRadius: 12, border: '1px solid #334155' }}>
            <div style={{ fontSize: 11, fontWeight: 700, color: '#94a3b8' }}>{m.label}</div>
            <div style={{ fontSize: 26, fontWeight: 900, color: m.color, marginTop: 4, fontFamily: 'monospace' }}>{m.val}</div>
            <div style={{ fontSize: 10.5, color: '#64748b', marginTop: 2 }}>{m.sub}</div>
          </div>
        ))}
      </div>

      {/* CONFUSION MATRIX & FALSE POSITIVE ANALYSIS */}
      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 16 }}>
        
        {/* Confusion Matrix Table */}
        <div style={{ background: 'rgba(15, 23, 42, 0.85)', padding: 20, borderRadius: 14, border: '1px solid #1e293b' }}>
          <div style={{ fontSize: 13.5, fontWeight: 800, color: 'white', marginBottom: 12 }}>
            📊 2×2 CONFUSION MATRIX (SYNTHETIC TEST SPLIT)
          </div>
          <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: 12, textAlign: 'center' }}>
            <thead>
              <tr style={{ background: '#020617', color: '#94a3b8' }}>
                <th style={{ padding: 8 }}>Actual \ Predicted</th>
                <th style={{ padding: 8, color: '#ef4444' }}>Predicted Anomaly</th>
                <th style={{ padding: 8, color: '#34d399' }}>Predicted Normal</th>
              </tr>
            </thead>
            <tbody>
              <tr>
                <td style={{ padding: 10, fontWeight: 700, color: '#ef4444', background: '#0c1324' }}>Actual Anomaly</td>
                <td style={{ padding: 10, background: '#064e3b', color: '#6ee7b7', fontWeight: 800 }}>
                  TP: {confusion_matrix.true_positives}
                </td>
                <td style={{ padding: 10, background: '#7f1d1d', color: '#fca5a5', fontWeight: 800 }}>
                  FN: {confusion_matrix.false_negatives}
                </td>
              </tr>
              <tr>
                <td style={{ padding: 10, fontWeight: 700, color: '#34d399', background: '#0c1324' }}>Actual Normal</td>
                <td style={{ padding: 10, background: '#78350f', color: '#fde68a', fontWeight: 800 }}>
                  FP: {confusion_matrix.false_positives}
                </td>
                <td style={{ padding: 10, background: '#064e3b', color: '#6ee7b7', fontWeight: 800 }}>
                  TN: {confusion_matrix.true_negatives.toLocaleString()}
                </td>
              </tr>
            </tbody>
          </table>
          <div style={{ fontSize: 10.5, color: '#94a3b8', marginTop: 10 }}>
            Decision Threshold ($\theta$): <b>{supervised_anomaly_metrics.decision_threshold}</b> · Contamination ($\nu$): <b>{supervised_anomaly_metrics.contamination_rate}</b>
          </div>
        </div>

        {/* False Positive & Mitigation Analysis */}
        <div style={{ background: 'rgba(15, 23, 42, 0.85)', padding: 20, borderRadius: 14, border: '1px solid #1e293b' }}>
          <div style={{ fontSize: 13.5, fontWeight: 800, color: '#f59e0b', marginBottom: 12 }}>
            🛡️ FALSE POSITIVE ANALYSIS & HUMAN-IN-THE-LOOP MITIGATION
          </div>
          <div style={{ background: '#020617', padding: 14, borderRadius: 10, border: '1px solid #334155', fontSize: 12, lineHeight: 1.6 }}>
            <div style={{ color: '#f87171', fontWeight: 700 }}>Primary False-Positive Trigger Cause:</div>
            <div style={{ color: '#cbd5e1', marginTop: 2 }}>{false_positive_analysis.common_cause}</div>
            
            <div style={{ color: '#34d399', fontWeight: 700, marginTop: 12 }}>Responsible-AI Mitigation Strategy:</div>
            <div style={{ color: '#cbd5e1', marginTop: 2 }}>{false_positive_analysis.mitigation}</div>
          </div>
        </div>

      </div>

      {/* DETERMINISTIC & GEOMETRIC ALGORITHMIC CALIBRATION */}
      <div style={{ background: 'rgba(15, 23, 42, 0.85)', padding: 20, borderRadius: 14, border: '1px solid #1e293b' }}>
        <div style={{ fontSize: 13.5, fontWeight: 800, color: '#38bdf8', marginBottom: 12 }}>
          ⚙️ DETERMINISTIC & GEOMETRIC ALGORITHMIC CALIBRATION PARAMETERS
        </div>
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: 12 }}>
          {Object.entries(deterministic_algorithms_calibration).map(([algo, params]: [string, any]) => (
            <div key={algo} style={{ background: '#020617', padding: 14, borderRadius: 10, border: '1px solid #1e293b' }}>
              <div style={{ fontSize: 12, fontWeight: 800, color: '#38bdf8', textTransform: 'uppercase' }}>
                {algo.replace('_', ' ')}
              </div>
              <div style={{ marginTop: 8, display: 'flex', flexDirection: 'column', gap: 4, fontSize: 11, color: '#cbd5e1' }}>
                {Object.entries(params).map(([k, v]: [string, any]) => (
                  <div key={k} style={{ display: 'flex', justifyContent: 'space-between' }}>
                    <span style={{ color: '#64748b' }}>{k.replace('_', ' ')}:</span>
                    <span style={{ fontWeight: 700, color: 'white' }}>{String(v)}</span>
                  </div>
                ))}
              </div>
            </div>
          ))}
        </div>
      </div>

    </div>
  )
}
