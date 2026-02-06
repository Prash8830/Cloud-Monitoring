# Cloud-Monitoring
Bayers hackathon project
![Cloud Monitoring Architecture](./cloud monitoring.png)
---

## 🔍 Logs Agent

**Infer intent → Scope → Filter → Reason → Explain**

* **Infer intent**
  Understand *what kind of failure to look for* from the alert
  (latency → blocking, error-rate → crashes, memory → leaks)

* **Scope**
  Narrow logs by **service + time window + severity** to remove noise

* **Filter**
  Apply intent-driven search (patterns, keywords, elastic queries)

* **Reason**
  Convert repeated log patterns into a failure class
  (DB timeout, thread exhaustion, external API failure)

* **Explain**
  Output clear evidence and conclusion for the commander

👉 *Answers:* **“What is failing?”**

---

## 📊 Telemetry Agent

**Window → Select metrics → Analyze shapes → Correlate → Explain**

* **Window**
  Look at metrics **before, during, after** the alert

* **Select metrics**
  Pull only metrics relevant to the alert type
  (latency, CPU, memory, RPS)

* **Analyze shapes**
  Detect patterns: sudden vs gradual, spike vs saturation

* **Correlate**
  Compare metrics together to identify system behavior
  (blocking, overload, degradation)

* **Explain**
  Summarize how the system behaved with supporting evidence

👉 *Answers:* **“How did the system behave?”**

---

## 🚀 Deployment (CI/CD) Agent

**Normalize → Filter by time → Filter by impact → Rank → Explain**

* **Normalize**
  Convert raw CI/CD events into canonical change types
  (code, config, feature flag, infra)

* **Filter by time**
  Keep only changes close to the incident

* **Filter by impact**
  Remove changes that *cannot* cause this kind of incident

* **Rank**
  Score remaining changes by risk and relevance

* **Explain**
  Output most likely change(s) with reasoning and confidence

👉 *Answers:* **“What change could have caused this?”**

---

## 🧠 One-line summary for the team

* **Logs Agent:** *Finds what broke*
* **Telemetry Agent:** *Explains system behavior*
* **Deployment Agent:** *Finds the risky change*

Together they produce:

> **Root cause = behavior + evidence + change correlation**


