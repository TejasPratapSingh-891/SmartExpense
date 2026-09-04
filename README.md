# SmartExpense

### Personal Financial Analytics & Decision-Support Platform

SmartExpense is a full-stack personal finance platform designed to go beyond basic expense tracking. It combines transaction management, budget monitoring, financial analytics, automated insights, and visual reporting in a single web application.

## Overview

SmartExpense helps users understand where their money goes, monitor monthly budgets, evaluate financial health, and identify spending patterns through deterministic financial calculations.

The application provides:

* Secure user authentication
* Transaction and category management
* Monthly budget tracking
* Financial Health Score
* Spending and cash-flow analytics
* Rule-based financial insights
* CSV import/export
* Interactive charts
* Monthly financial reports
* Responsive dark/light interface

## Key Features

### Financial Dashboard

The dashboard provides an overview of:

* Total income
* Total expenses
* Net savings
* Savings rate
* Monthly spending trends
* Budget utilization
* Financial health indicators

### Financial Health Score

SmartExpense calculates a **0–100 Financial Health Score** using four weighted factors:

| Factor                  | Weight |
| ----------------------- | -----: |
| Savings Rate            |    40% |
| Budget Discipline       |    30% |
| Spending Growth Control |    20% |
| Cash Buffer / Stability |    10% |

The score is generated from application data rather than relying on subjective recommendations.

### Rule-Based Insights Engine

The application analyzes financial activity and generates deterministic insights, including:

* Category spending increases
* Budget utilization warnings
* Potential budget overruns
* Spending-growth patterns
* Discretionary spending opportunities

This approach keeps financial calculations predictable and reproducible.

### Transaction Management

Users can manage their financial ledger with:

* Income and expense records
* Categories
* Dates
* Payment methods
* Notes
* Search and filtering
* Sorting
* Pagination
* CSV import/export

### Budget Management

Users can create monthly category budgets and monitor utilization.

The system provides threshold-based warnings when spending approaches or exceeds the configured budget.

### Analytics

Interactive visualizations provide:

* Category spending distribution
* Monthly income vs. expenses
* Historical spending trends
* Budget utilization
* Cash-flow analysis

### Reports

Users can generate printable monthly financial reports designed for clean browser/PDF output.

## System Architecture

```text
┌───────────────────────────────────────────────┐
│              Presentation Layer               │
│                                               │
│  HTML5  │  CSS  │  Vanilla JavaScript        │
│  Chart.js  │  Responsive UI  │  Themes        │
└───────────────────────┬───────────────────────┘
                        │
                   HTTP / Forms
                        │
┌───────────────────────▼───────────────────────┐
│              Flask Application                │
│                                               │
│  Authentication                               │
│  Dashboard                                    │
│  Transactions                                 │
│  Budgets                                      │
│  Analytics                                    │
│  Insights                                     │
│  Reports                                      │
│  API                                          │
└───────────────────────┬───────────────────────┘
                        │
                  SQLAlchemy ORM
                        │
┌───────────────────────▼───────────────────────┐
│              SQLite Database                  │
│                                               │
│  User │ Category │ Transaction │ Budget       │
└───────────────────────────────────────────────┘
```

## Database Design

The application uses a relational data model centered around user-owned financial data.

```text
User
 │
 ├───────────────┐
 │               │
 ▼               ▼
Category      Transaction
 │               │
 │               │
 └───────┐       │
         ▼       │
       Budget ◄──┘
```

### Core Models

**User**

* Authentication information
* Profile information
* Financial preferences

**Category**

* User-owned category
* Income/expense classification
* Category metadata

**Transaction**

* Amount
* Transaction type
* Date
* Category
* Payment method
* Notes

**Budget**

* Monthly spending limit
* Category association
* Month and year
* User association

## Financial Algorithms

### Daily Burn Rate

Current spending is divided by elapsed billing days:

```text
Daily Burn Rate =
Current Cumulative Spending / Elapsed Days
```

### Projected Month-End Spending

```text
Projected Spending =
Daily Burn Rate × Total Days in Month
```

These metrics help identify whether current spending is likely to exceed the expected monthly pace.

### Month-over-Month Analysis

The analytics layer compares current-period financial activity with previous periods to identify changes in:

* Spending
* Category usage
* Budget consumption
* Savings

## Technology Stack

### Backend

* Python
* Flask
* SQLAlchemy
* Flask-Login
* Werkzeug

### Database

* SQLite
* Relational database design
* SQLAlchemy ORM

### Frontend

* HTML5
* CSS3
* JavaScript (ES6+)
* Chart.js
* Responsive UI
* Dark/Light theme

### Development

* Git
* GitHub
* Python virtual environment
* Unit testing

## Project Structure

```text
SmartExpense/
│
├── app/
│   ├── ...
│
├── tests/
│   ├── ...
│
├── requirements.txt
├── config.py
├── run.py
├── seed.py
├── README.md
├── LICENSE
└── .gitignore
```

## Getting Started

### Prerequisites

* Python 3.10+
* Git

### Clone the Repository

```bash
git clone https://github.com/TejasPratapSingh-891/SmartExpense.git
cd SmartExpense
```

### Create a Virtual Environment

#### Windows

```powershell
python -m venv venv
venv\Scripts\activate
```

#### macOS / Linux

```bash
python -m venv venv
source venv/bin/activate
```

### Install Dependencies

```bash
pip install -r requirements.txt
```

### Initialize Demo Data

```bash
python seed.py
```

The seed script creates demonstration financial data for local development and testing.

**No demo credentials are published in this repository.**

### Run the Application

```bash
python run.py
```

Then open:

```text
http://127.0.0.1:5000
```

## Testing

Run the automated test suite with:

```bash
python -m unittest discover tests
```

The tests cover application behavior including models, authentication, calculations, and routes.

## Security

SmartExpense includes application-level security mechanisms such as:

* Password hashing
* Session-based authentication
* Authenticated route protection
* User-scoped database queries
* User-specific financial records

Never commit real passwords, API keys, secret keys, database credentials, or other sensitive information to GitHub.

## Current Status

SmartExpense is an actively developed portfolio project focused on demonstrating full-stack development, relational database design, financial analytics, authentication, testing, and responsive web application development.

## Future Improvements

Potential future enhancements include:

* PostgreSQL deployment
* Production cloud deployment
* REST API expansion
* Automated recurring transactions
* Advanced financial forecasting
* More granular notification systems
* Data visualization enhancements
* Automated CI/CD pipeline

## License

This project is licensed under the MIT License. See the `LICENSE` file for details.

---

**SmartExpense** — turning financial records into actionable insights.
