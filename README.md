# SmartExpense ? Personal Financial Analytics Platform

![Python](https://img.shields.io/badge/Python-3.14+-3776AB?style=for-the-badge&logo=python&logoColor=white)
![Flask](https://img.shields.io/badge/Flask-3.1+-000000?style=for-the-badge&logo=flask&logoColor=white)
![SQLAlchemy](https://img.shields.io/badge/SQLAlchemy-2.0+-D71F00?style=for-the-badge&logo=sqlalchemy&logoColor=white)
![SQLite](https://img.shields.io/badge/SQLite-003B57?style=for-the-badge&logo=sqlite&logoColor=white)
![Chart.js](https://img.shields.io/badge/Chart.js-FF6384?style=for-the-badge&logo=chartdotjs&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-green?style=for-the-badge)

> **SmartExpense** is an enterprise-grade full-stack personal finance decision-support platform. Engineered to supersede basic "expense trackers", it delivers real-time cash flow analytics, algorithmic budget pacing warnings, rule-based intelligence, and a calculated **Financial Health Score (0?100)**.

---

## ?? Key Capabilities & Architectural Highlights

- **Executive KPI Dashboard:** Real-time calculation of Total Income, Total Outflow, Net Retained Savings, and Savings Rate with Month-over-Month (MoM) trend velocities.
- **Financial Health Score Engine (0?100):** A multi-factor quantitative resilience rating analyzing savings rate (40%), budget compliance (30%), spending growth (20%), and cash surplus stability (10%).
- **Rule-Based Smart Insights Engine:** Algorithmic detectors flagging category spending surges (>20% MoM), budget exhaustion pacing risks, and discretionary savings optimization scenarios.
- **Transaction Ledger & Data Pipeline:** Full CRUD with multi-variable filtering (category, type, date range), live search, multi-column sorting, pagination, and bidirectional CSV export/import.
- **Dynamic Budget Discipline System:** Category monthly limits with color-shifting threshold alerts at 80% utilization and 100%+ overrun warnings.
- **Deep-Dive Visual Analytics:** 6-month historical stacked trends, burn-rate metrics, and category concentration audits built with Chart.js.
- **Monthly Audit Reports & PDF Export:** Comprehensive printable financial statements with clean CSS `@media print` layout.
- **Bespoke Modern Fintech UI:** Dark/Light theme switching, glassmorphism card elevation, fluid typography, and responsive drawer navigation.

---

## ??? System Architecture

```
???????????????????????????????????????????????????????????????????????????
?                           Client Presentation                           ?
?  ? HTML5 Semantic Shell   ? Bespoke Modern CSS (Tailwind-grade design)  ?
?  ? Lucide Modern Icons    ? Modular Vanilla JS (ES6+)                   ?
?  ? Chart.js Visualizations (Gradients, Area, Doughnut, Multi-Axis Bars) ?
???????????????????????????????????????????????????????????????????????????
                                     ? HTTP / REST & Form Submissions
???????????????????????????????????????????????????????????????????????????
?                         Application Server (Flask)                      ?
?  ? Application Factory Pattern (`create_app`)                           ?
?  ? Modular Blueprints: Auth, Dashboard, Transactions, Budgets,          ?
?    Analytics, Insights, Reports, API                                    ?
?  ? Flask-Login Session Management + Werkzeug Password Hashing           ?
?  ? Flash Alert / Toast Notification Pipeline                            ?
???????????????????????????????????????????????????????????????????????????
                                     ? SQLAlchemy ORM
???????????????????????????????????????????????????????????????????????????
?                         Relational Persistence                          ?
?  ? SQLite3 with Foreign Key Cascading                                   ?
?  ? Models: User, Transaction, Category, Budget                          ?
?  ? Server-Side Aggregations (SUM, AVG, GROUP BY, MoM Windowing)         ?
???????????????????????????????????????????????????????????????????????????
```

---

## ??? Relational Data Models

```
???????????????????????????           ???????????????????????????
?          User           ?           ?        Category         ?
???????????????????????????           ???????????????????????????
? id (PK)                 ?           ? id (PK)                 ?
? username                ?           ? user_id (FK -> User)    ?
? email                   ?           ? name                    ?
? password_hash           ?           ? type (income/expense)   ?
? full_name               ?           ? icon                    ?
? currency_symbol         ?           ? color                   ?
? monthly_income_target   ?           ???????????????????????????
???????????????????????????                       ?
            ? 1:N                                 ? 1:N
            ????????????????????????              ?
            ?                      ?              ?
??????????????????????????? ???????????????????????????????
?         Budget          ? ?        Transaction          ?
??????????????????????????? ???????????????????????????????
? id (PK)                 ? ? id (PK)                     ?
? user_id (FK -> User)    ? ? user_id (FK -> User)        ?
? category_id (FK -> Cat) ? ? category_id (FK -> Category)?
? monthly_limit           ? ? title                       ?
? month (1-12)            ? ? type (income/expense)       ?
? year                    ? ? amount                      ?
? Unique(user,cat,mo,yr)  ? ? date                        ?
??????????????????????????? ? payment_method              ?
                            ? notes                       ?
                            ???????????????????????????????
```

---

## ?? Algorithmic Business Logic

### 1. Financial Health Score Algorithm (0?100 Points)
The platform evaluates an individual's fiscal posture across four weighted pillars:
$$	ext{Health Score} = S_{	ext{rate}} + B_{	ext{discipline}} + E_{	ext{control}} + C_{	ext{buffer}}$$
- **Savings Rate Component (Max 40 pts):**
  - $\ge 50\% 
ightarrow 40	ext{ pts}$
  - $35\% - 49\% 
ightarrow 35	ext{ pts}$
  - $20\% - 34\% 
ightarrow 28	ext{ pts}$
  - $10\% - 19\% 
ightarrow 18	ext{ pts}$
  - $< 10\% 
ightarrow 10	ext{ pts}$ (or $0	ext{ pts}$ if negative).
- **Budget Discipline Component (Max 30 pts):**
  - $	ext{Score} = \left( rac{	ext{Budgets within Limit}}{	ext{Total Active Budgets}} 
ight) 	imes 30$
- **Spending Growth Control (Max 20 pts):**
  - Compares current monthly expenditure against prior month ($M-1$). Flat or negative growth awards 20 pts; progressive penalties are incurred for expansions $> 5\%$, $> 15\%$, and $> 30\%$.
- **Income Stability & Cash Buffer (Max 10 pts):**
  - Evaluates positive net cash retention against target income baseline.

### 2. Pacing & Projected Burn Rate
$$	ext{Daily Burn} = rac{	ext{Current Cumulative Spend}}{	ext{Elapsed Billing Days}}$$
$$	ext{Projected Month-End Spend} = 	ext{Daily Burn} 	imes 	ext{Total Days in Month}$$

### 3. Rule-Based Smart Insights
1. **Category Spike Detector:** Triggers a `Spending Alert` if a category's expenses surged by $\ge 20\%$ and $> 	ext{?}800$ compared to the previous month.
2. **Discretionary Haircut Opportunity:** Aggregates lifestyle expenditures (dining, entertainment, shopping) and models a 20% optimization dividend.
3. **Pacing Exhaustion Risk:** Alerts users when category budget consumption hits $\ge 80\%$ with significant calendar days remaining.

---

## ?? Quick Start Guide

### 1. Prerequisites
- Python 3.10+ installed
- Git installed

### 2. Clone Repository
```bash
git clone https://github.com/<your-username>/SmartExpense.git
cd SmartExpense
```

### 3. Setup Virtual Environment & Install Dependencies
```bash
python -m venv venv
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

pip install -r requirements.txt
```

### 4. Seed Demo Portfolio Data
Populate the database with realistic multi-month Indian Rupee (?) demo data:
```bash
python seed.py
```
*Pre-configured Demo Account:*
- **Email:** `tejasprataps891@gmail.com` (or username `tejas`)
- **Password:** `admin123`

### 5. Launch the Application
```bash
python run.py
```
Open **`http://127.0.0.1:5000`** in your browser.

---

## ?? Automated Testing

Execute the comprehensive test suite verifying models, authentication, service calculations, and routes:
```bash
python -m unittest discover tests
```

---

## ?? Resume Description & Talking Points

### Resume Bullet Points
- **SmartExpense ? Personal Financial Analytics Platform** | *Python, Flask, SQLAlchemy, SQLite, JavaScript, Chart.js*
  - Engineered a production-grade personal financial analytics platform featuring session authentication, transaction ledgering, budget management, and multi-variable financial reporting.
  - Designed relational database schemas (User, Category, Transaction, Budget) with foreign key cascading and server-side aggregations for cash flow calculations.
  - Implemented an algorithmic **Financial Health Score (0?100)** and a **Rule-Based Insights Engine** that detects spending anomalies (>20% MoM surges) and budget overrun risks.
  - Created an interactive, responsive dashboard with smooth Chart.js visualizations, dark/light theme switching, and client-side CSV import/export capabilities.

---

## ?? Interview Preparation: Key Engineering Decisions

#### Q1: Why build SmartExpense with Flask instead of React + Django or Node?
> **Answer:** "I prioritized building a cohesive, maintainable full-stack application with deep server-side rendering and minimal unnecessary client runtime overhead. Flask's lightweight Application Factory pattern allowed me to structure blueprints cleanly (Auth, Transactions, Budgets, Analytics, Reports, API) while retaining full control over SQLAlchemy queries and relational data isolation without client-server state synchronization issues."

#### Q2: How is data isolation and security enforced between users?
> **Answer:** "Every transaction and budget record is strictly scoped to the authenticated `current_user.id`. SQLAlchemy queries always filter by `user_id == current_user.id`, ensuring zero cross-tenant leakage. Passwords are salted and hashed using Werkzeug's PBKDF2/SHA-256 implementation, and routes are protected with Flask-Login decorators."

#### Q3: How does the Rule-Based Insights Engine operate?
> **Answer:** "Rather than relying on non-deterministic LLMs for financial calculations, I designed a deterministic rule engine. It performs windowed queries across adjacent calendar periods ($M$ vs $M-1$), computes category variances and burn rates, and generates contextual alerts (such as a 24% surge in dining out or a 91% budget consumption pace with 12 days remaining). This ensures 100% mathematical accuracy and zero hallucination."

---

## ?? License
This project is licensed under the MIT License ? see the [LICENSE](LICENSE) file for details.
