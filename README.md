# Gmail Rule Engine

Automatically process Gmail emails based on configurable rules. Built with Python, Gmail API, and PostgreSQL.

## Features

- Fetch emails via Gmail API (OAuth 2.0)
- Store in PostgreSQL database and SQLAlchemy for ORM
- Apply rules based on sender, subject, message content, and date
- Actions: mark as read/unread, move to folders
- Batch processing with error isolation

## Quick Start

### 1. Prerequisites

- Python 3.10+
- PostgreSQL
- Gmail account

### 2. Installation

```bash
# Clone and setup
git clone https://github.com/Tejaa25/GmailRuleEngine.git
cd gmail_rule_engine
python -m venv venv
venv\Scripts\activate # for windows
pip install -r requirements.txt
```

### 3. Gmail API Setup

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create project → Enable Gmail API
3. Create OAuth 2.0 credentials (Desktop app)
4. Download as `credentials.json` in project root
5. Add your email as test user in OAuth consent screen

### 4. Database Setup

```bash
# Create database
createdb gmail_db

# Configure .env file with your db creds 
DATABASE_USER=postgres
DATABASE_PASSWORD=your_password
DATABASE_HOST=localhost
DATABASE_PORT=5432
DATABASE_NAME=gmail_db

# Initialize
python main.py --init-db
```

### 5. Run

```bash
# Fetch & Process emails
python main.py
```

## Rule Configuration

Available in `rules.json`

### Supported Conditions

| Field | Predicates |
|-------   |-----------|
| String | contains, not_contains, equals, not_equals |
| Datetime | less_than, greater_than |

**Predicate Types:**
- `All` - similar to AND condition.
- `Any` - similar to OR condition

**Available Actions:**
- `mark_as_read`
- `mark_as_unread`  
- `move_message`

## Command-Line Options

```bash
python main.py --help

Options:
  --init-db       Initialize database tables
  --fetch-only    Only fetch emails, skip rules
  --process-only  Only process rules, skip fetch
```

## Requirements

- Python 3.10+
- PostgreSQL 12+
- Gmail account with API access
- Dependencies in `requirements.txt`
