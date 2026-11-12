
# JourneyIQ – Cross-Channel Customer Journey Analytics & Friction Detection

## Live Demo

Try the deployed JourneyIQ application:

**Live Application:** [Open JourneyIQ](https://journeyiq-9iaegnicxad4k5s6v8qstc.streamlit.app)

## Output Video / Project Demo

Watch the output video to see the JourneyIQ application and its main features:

**Project Demo Video:** [Watch JourneyIQ Demo](PASTE_YOUR_VIDEO_URL_HERE)

The demonstration video covers:

- Business Overview dashboard and key performance indicators.
- Customer Journey Funnel and drop-off analysis.
- Channel Performance comparison.
- Anomaly Detection results.
- Session Explorer and event history.
- Performance Benchmark results.

## 1. Project Overview

JourneyIQ is a customer journey analytics platform that helps businesses understand how customers interact with their digital channels, identify where customers drop off during the purchase journey, and detect unusual activities that may affect conversion.

The platform analyzes customer activity across channels such as web, mobile app, and support. It converts raw session and event data into funnel metrics, channel performance insights, anomaly reports, identity-resolution results, and an interactive Streamlit dashboard.

### Main Aim

The main aim of JourneyIQ is to help businesses understand where customers leave without completing a purchase and what issues may be affecting their journey, so that teams can make data-informed improvements to customer experience and conversion.

### Problem Statement

A business may receive many visitors, but only a portion of them complete a purchase. Looking only at the final number of purchases does not explain where or why customers leave.

For example, customers may:
- Visit a website but never view a product.
- View a product but not add it to the cart.
- Add a product to the cart but not begin checkout.
- Begin checkout but not complete the purchase.
- Interact across multiple channels or sessions.
- Generate unusual events, such as bot traffic or duplicate purchase events.

JourneyIQ analyzes these activities and presents the results in one dashboard.

## 2. Project Objectives

1. **Customer Journey Analysis:** Analyze customer activity across channels and sessions.
2. **Funnel Analysis:** Measure progression through the purchase journey and identify drop-offs between stages.
3. **Channel Performance:** Compare sessions, conversions, abandonment, and support contacts across channels.
4. **Anomaly Detection:** Identify unusual patterns such as bot traffic, delayed event ingestion, and duplicate purchase events.
5. **Identity Stitching:** Connect customer activity using identity links while handling conflicts and consent restrictions.
6. **Anomaly Evaluation:** Compare detected anomalies with generated ground truth using precision, recall, and F1-score.
7. **Performance Benchmarking:** Measure execution time and Python-tracked memory allocations for key processing modules.
8. **Interactive Visualization:** Present analytics and investigation tools through a Streamlit dashboard.

## 3. Customer Journey Workflow

A typical purchase journey in JourneyIQ follows these stages:

1. **Page View** – A customer visits a page.
2. **Product View** – The customer views a product.
3. **Add to Cart** – The customer adds a product to the cart.
4. **Checkout Start** – The customer begins checkout.
5. **Purchase** – The customer completes a purchase.

The funnel uses the order of events within a session. A later stage is counted only when it occurs after the preceding stage.

### Example

Suppose 10,000 eligible sessions enter a website and 2,000 sessions complete a purchase. JourneyIQ helps the business understand how many sessions reached each stage and where the largest drop-off occurred.

## 4. Key Modules

### 4.1 Data Generation

The data-generation script creates sample customers, sessions, journey events, products, pages, identity links, and ground-truth anomalies.

The generated dataset is synthetic and is intended for development, testing, and demonstration.

### 4.2 Data Validation

The validation module checks data quality and relationships, including:

- Customer primary-key uniqueness.
- Session primary-key uniqueness.
- Event primary-key uniqueness.
- Valid session foreign keys.
- Valid customer foreign keys.
- Valid product foreign keys.
- Valid page foreign keys.
- Allowed channel values.
- Parseable event timestamps.

### 4.3 Funnel Analytics

The analytics module builds session-level metrics and sequential funnel metrics.

It produces:
- `session_metrics.csv`
- `funnel_metrics.csv`
- `channel_performance.csv`

The funnel helps identify where customers stop progressing toward a purchase.

### 4.4 Channel Performance

Channel performance compares customer journeys across channels, such as web, app, and support.

The available output includes:
- Total sessions.
- Converted sessions.
- Abandoned sessions.
- Conversion rate.
- Abandonment rate.
- Support contacts.

### 4.5 Anomaly Detection

The anomaly-detection module identifies unusual journey activity.

The project includes these anomaly categories:

| Rule | Anomaly Type | Description |
|---|---|---|
| RULE-01 | DELAYED_INGESTION | Events received later than expected |
| RULE-02 | DUPLICATE_PURCHASE_EVENT | Duplicate purchase events |
| RULE-03 | BOT_TRAFFIC | Sessions identified as bot traffic |
| RULE-04 | INCORRECT_IDENTITY_MERGE | An anonymous identity linked to multiple customers |

Detected anomalies include an entity ID, issue type, severity, rule ID, and evidence.

### 4.6 Identity Stitching

Identity stitching attempts to connect anonymous activity to known customer identities using identity links.

The module:
- Checks identity-link consent.
- Detects anonymous IDs linked to multiple customers.
- Flags identity conflicts.
- Avoids resolving conflicting anonymous IDs to a customer.
- Produces identity-resolved events and identity anomaly outputs.

It generates:
- `identity_resolved_events.csv`
- `identity_anomalies.csv`

The project handles identity conflicts conservatively rather than choosing one customer arbitrarily.

### 4.7 Anomaly Evaluation

The evaluation module compares detected anomalies with the generated ground-truth dataset.

It calculates:
- True Positives (TP).
- False Positives (FP).
- False Negatives (FN).
- Precision.
- Recall.
- F1-score.

It generates:
- `anomaly_evaluation_summary.csv`
- `anomaly_evaluation_by_rule.csv`
- `anomaly_evaluation_details.csv`

### 4.8 Performance Benchmarking

The benchmark module measures execution time and Python-tracked memory allocations for key modules:

- Data Validation.
- Funnel and Channel Analytics.
- Anomaly Detection.
- Identity Stitching.
- Anomaly Evaluation.

It generates `benchmark_results.csv`.

**Note:** The benchmark uses Python memory-tracking measurements. These are not the same as total operating-system process memory.

### 4.9 Streamlit Dashboard

The dashboard brings the project outputs together in an interactive interface.

The six dashboard sections are:

1. **Overview** – Key performance indicators, funnel summary, conversion versus abandonment, channel snapshot, and recent detected issues.
2. **Funnel Analytics** – Funnel-stage counts and drop-off analysis.
3. **Channel Performance** – Channel-level conversion and abandonment comparisons.
4. **Anomaly Detection** – Anomaly types, severity, and evidence.
5. **Session Explorer** – Explore an individual session and its event history.
6. **Performance Benchmark** – Review module execution time, memory measurements, and benchmark status.

## 5. Technology Stack

| Technology | Purpose |
|---|---|
| Python | Core programming language and data processing |
| Pandas | Data cleaning, transformation, joins, and analysis |
| NumPy | Numerical operations |
| SQLite (sqlite3) | Local relational database storage |
| Streamlit | Interactive analytics dashboard |
| Plotly | Interactive charts and visualizations |
| Pytest | Automated testing |
| tracemalloc | Python memory-allocation benchmarking |
| time.perf_counter | Execution-time measurement |

## 6. High-Level Architecture

```text
Synthetic Data Generation
          |
          v
Raw CSV Dataset
          |
          v
Data Validation
          |
          +-------------------------------+
          |               |               |
          v               v               v
   Funnel & Channel   Anomaly         Identity
     Analytics       Detection        Stitching
          |               |               |
          v               +-------+-------+
    Processed Metrics             |
          |                       v
          |                 Anomaly Evaluation
          |                       |
          +-----------+-----------+
                      |
                      v
              Performance Benchmark
                      |
                      v
              Streamlit Dashboard
```

## 7. Project Results

The following figures were observed in the current generated 10,000-session dataset and dashboard run:

| Metric | Result |
|---|---:|
| Generated sessions | 10,000 |
| Generated events | 200,000 |
| Ground-truth anomalies | 291 |
| Eligible sessions | 9,897 |
| Converted sessions | 2,051 |
| Conversion rate | 20.72% |
| Detected issues | 291 |

### Anomaly Detection Results

| Anomaly Type | Count |
|---|---:|
| BOT_TRAFFIC | 103 |
| DELAYED_INGESTION | 99 |
| DUPLICATE_PURCHASE_EVENT | 88 |
| INCORRECT_IDENTITY_MERGE | 1 |
| **Total** | **291** |

### Anomaly Evaluation Results

| Metric | Result |
|---|---:|
| Ground-truth anomalies | 291 |
| Detected anomalies | 291 |
| True positives | 291 |
| False positives | 0 |
| False negatives | 0 |
| Precision | 100% |
| Recall | 100% |
| F1-score | 100% |

All four generated rules achieved 100% in that evaluation run.

**Important:** These scores are based on the project's synthetic dataset. They do not establish 100% accuracy on real-world customer data. Real-world performance must be tested using representative, independently labelled data.

The automated test suite also passed **10 tests** in the reported run.

## 8. Project Folder Structure

```text
JourneyIQ_starter_project/
|
|-- app.py
|-- requirements.txt
|-- README.md
|
|-- config/
|   |-- settings.py
|
|-- src/
|   |-- generate_data.py
|   |-- database.py
|   |-- validation.py
|   |-- analytics.py
|   |-- anomaly_detection.py
|   |-- identity_stitching.py
|   |-- evaluate_anomalies.py
|   |-- benchmark.py
|
|-- tests/
|   |-- test_project.py
|
|-- data/
    |-- raw/
    |   |-- starter/
    |   |-- ground_truth/
    |
    |-- processed/
```

## 9. Installation and Setup

### Prerequisites

- Python 3.10 or later.
- Visual Studio Code or another Python editor.
- PowerShell or a terminal.
- Git (optional).

### Step 1: Open the project folder

Open `JourneyIQ_starter_project` in VS Code and open its terminal.

### Step 2: Create a virtual environment

```powershell
python -m venv venv
```

### Step 3: Activate the environment

```powershell
.\venv\Scripts\Activate.ps1
```

### Step 4: Install dependencies

```powershell
python -m pip install -r requirements.txt
```

## 10. Running the Project

Run these commands from the project root folder.

### Step 1: Generate the dataset

```powershell
python -m src.generate_data --sessions 10000 --events 200000 --seed 20261022 --output data/raw/starter
```

### Step 2: Validate the data

```powershell
python -m src.validation
```

### Step 3: Load data into SQLite

```powershell
python -m src.database
```

### Step 4: Build funnel and channel analytics

```powershell
python -m src.analytics
```

### Step 5: Detect anomalies

```powershell
python -m src.anomaly_detection
```

### Step 6: Run identity stitching

```powershell
python -m src.identity_stitching
```

### Step 7: Evaluate anomalies

```powershell
python -m src.evaluate_anomalies
```

### Step 8: Run performance benchmarks

```powershell
python -m src.benchmark
```

### Step 9: Launch the dashboard

```powershell
python -m streamlit run app.py
```

Streamlit will provide a local URL, usually:

`http://localhost:8501`

## 11. Running Automated Tests

Run the test suite from the project root:

```powershell
python -m pytest -q
```

The reported project test run completed with:

```text
10 passed
```

The tests cover starter data availability, data relationships, validation, anomaly detection, identity-conflict handling, and analytics output files.

## 12. Key Output Files

| Output File | Purpose |
|---|---|
| `session_metrics.csv` | Session-level analytics |
| `funnel_metrics.csv` | Counts and drop-off by funnel stage |
| `channel_performance.csv` | Channel-level performance metrics |
| `detected_anomalies.csv` | Rule-based anomaly findings |
| `identity_resolved_events.csv` | Events with identity-resolution results |
| `identity_anomalies.csv` | Identity conflicts and related findings |
| `anomaly_evaluation_summary.csv` | Overall evaluation metrics |
| `anomaly_evaluation_by_rule.csv` | Evaluation metrics for each rule |
| `anomaly_evaluation_details.csv` | Record-level evaluation comparison |
| `benchmark_results.csv` | Execution-time and memory benchmark results |


## 13. Business Benefits

JourneyIQ can help business teams:

- Identify stages where customers abandon a purchase.
- Compare the performance of different customer channels.
- Investigate unusual or unreliable event activity.
- Understand identity conflicts instead of silently merging uncertain identities.
- Prioritize improvements using measurable funnel and channel metrics.
- Monitor the execution performance of analytics components.

The platform provides analytical evidence to support decisions. It does not automatically change a business website or guarantee an increase in sales.

## 14. Limitations and Future Enhancements

### Current Limitations

- The current project uses synthetic data rather than live production customer data.
- Anomaly rules and evaluation results are based on the generated dataset.
- The dashboard analyzes available CSV outputs and local project data.
- Identity stitching avoids resolving conflicting IDs; it does not determine the true identity in an unresolved conflict.
- Benchmark memory figures represent Python-tracked allocations, not total machine memory.

### Future Enhancements

- Connect to live event streams and production data sources.
- Add configurable date-range and advanced anomaly filters.
- Add searchable and downloadable investigation reports.
- Introduce machine-learning-based anomaly detection and compare it with rule-based detection.
- Add customer cohort, retention, and repeat-purchase analysis.
- Add role-based access control and deployment monitoring.
- Evaluate the system using independently labelled real-world data.

## 15. Project Explanation

### Short Explanation

JourneyIQ is a cross-channel customer journey analytics platform. Its main aim is to understand customer behaviour and identify where customers drop off during their purchase journey. It analyzes activities across web, mobile app, and support channels. It uses funnel analytics to measure conversion, anomaly detection to identify unusual events, and identity stitching to connect customer interactions while handling conflicts. Finally, it presents the results through an interactive Streamlit dashboard.

### What Makes the Project Useful?

JourneyIQ does more than count purchases. It shows how customers move through the purchase funnel, where they stop, how channels perform, and which unusual events may need investigation. This gives business teams clearer information for improving customer experience and conversion.

## 16. Conclusion

JourneyIQ combines data validation, customer journey analytics, anomaly detection, identity stitching, evaluation, and performance benchmarking in one platform.

Its purpose is to make customer journey friction easier to understand and investigate, helping businesses make better-informed decisions about their digital customer experience.
