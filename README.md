# ⚡ Praxiotech Revenue Intelligence Engine v1.2

A high-fidelity market audit platform designed to identify "Silent Winners" in the Frankfurt hospitality sector and convert data gaps into high-margin service contracts.

## 🚀 Key Features
* **Silent Winner Detection**: Proprietary logic that flags high-rated establishments (4.5★+) with critical engagement gaps (<30% response rate).
* **Dimension Radar**: A 5-pillar performance visualization (Reputation, Responsiveness, Digital Presence, Intelligence, Visibility) benchmarked against the Frankfurt Top 25th percentile.
* **AI Strategy Assistant**: Automated sales hooks in English and German tailored to specific restaurant personas.
* **Executive PDF Generation**: 6-page professional intelligence briefs featuring data tables, trend momentum, and 90-day investment roadmaps.

## 🛠️ Modular Architecture
The system is decoupled to ensure transition from 'Tool' to 'Infrastructure':
1. **`app.py`**: High-performance Streamlit UI using a custom light-mode SaaS theme.
2. **`scoring_engine.py`**: Mathematical modeling of 5 key business dimensions.
3. **`data_audit.py`**: Automated cleaning, German date normalization, and district benchmarking.
4. **`report_generator.py`**: Logic-driven PDF compilation using ReportLab and Matplotlib.

## 📊 Data Model
* **Digital Health Score**: A weighted composite (0-100) based on market responsiveness (25%), star quality (30%), and digital footprint (20%).
* **Momentum Tracker**: 13-month review velocity analysis to predict local SEO authority.

## 🚀 Deployment & Installation
1. Install dependencies: `pip install -r requirements.txt`
2. Run the engine: `streamlit run app.py`

---
*Internal Sales Document | Confidential | © 2026 Praxiotech GmbH*