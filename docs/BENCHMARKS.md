# CrimeNet AI: Empirical Performance Benchmarks

This document records **real, reproducible performance benchmarks** measured directly on the CrimeNet AI backend pipeline. 

> [!IMPORTANT]
> **Defensible Metrics Policy**: Zero fabricated numbers. All metrics reported below were computed from repeated statistical trials using Python's `time.perf_counter()` under actual execution conditions.

---

## 1. Summary of Empirical Results

| Benchmark Target | Samples | Median Latency | P95 Latency | P99 Latency | Measured Throughput |
| :--- | :---: | :---: | :---: | :---: | :---: |
| **SHA-256 Hashing (1MB blocks)** | 50 | `0.455 ms` | `0.597 ms` | `0.643 ms` | 2079.49 MB/s |
| **AES-256-GCM Encrypt+Decrypt (PII Envelope)** | 100 | `0.012 ms` | `0.014 ms` | `0.021 ms` | N/A |
| **NetworkX PageRank (100 nodes, d=0.85)** | 50 | `0.672 ms` | `1.413 ms` | `1.58 ms` | N/A |
| **NetworkX Dijkstra Shortest Path (Weighted)** | 50 | `0.08 ms` | `0.152 ms` | `0.324 ms` | N/A |
| **NetworkX Louvain Community Detection** | 50 | `5.745 ms` | `6.549 ms` | `6.618 ms` | N/A |
| **Isolation Forest Fit (1,000 synthetic records)** | 10 | `116.143 ms` | `122.858 ms` | `122.858 ms` | N/A |
| **Isolation Forest + Mahalanobis Inference (Single Record)** | 100 | `8.688 ms` | `9.771 ms` | `10.317 ms` | N/A |
| **Merkle Tree Construction & Inclusion Proof (64 leaves)** | 50 | `0.196 ms` | `0.242 ms` | `0.292 ms` | N/A |
| **ReportLab Dossier PDF Compilation (Multi-page)** | 10 | `3.502 ms` | `4.448 ms` | `4.448 ms` | N/A |

---

## 2. Benchmark Methodology

### Cryptographic Hashing (SHA-256)
- **Workload**: 50 iterations over 1 MB synthetic memory buffers using Python standard library `hashlib.sha256()`.
- **Purpose**: Validates evidence vault chunking and Merkle tree scaling under heavy ingest.

### Authenticated Encryption (AES-256-GCM)
- **Workload**: 100 round-trips of authenticated encryption and decryption with 64 KB blocks using `cryptography.hazmat.primitives.ciphers.aead.AESGCM` with a 12-byte random IV.

### Graph Analytics (NetworkX 3.6)
- **Workload**: 100-node, 500-edge Erdős–Rényi graph ($G_{n,m}$) with random edge weights.
- **PageRank**: Damping factor $d = 0.85$, tolerance $\epsilon = 10^{-6}$, maximum iterations 100.
- **Shortest Path**: Dijkstra's algorithm across randomly chosen vertex pairs.
- **Community Detection**: Louvain modularity maximization algorithm.

### Machine Learning Ensemble (Isolation Forest + Mahalanobis)
- **Workload**: 1,000 synthetic records with 5-dimensional feature vectors (`financial_velocity`, `nocturnal_ratio`, `cdr_burst_zscore`, `entropy_deviation`, `cycle_risk`).
- **Inference**: Scikit-learn `IsolationForest.decision_function()` combined with Covariance inversion Mahalanobis distance.

### Forensic Merkle Tree
- **Workload**: 64 cryptographic leaf nodes, calculating binary Merkle root and generating $O(\log N)$ inclusion proof path.

### Evidence Report Compilation
- **Workload**: ReportLab PDF document compilation with running two-pass page numbers, tables, disclaimers, and cryptographic SHA-256 headers.

---

## 3. How to Reproduce

Execute the benchmarking script from repository root:

```bash
python backend/scripts/run_benchmarks.py
```
