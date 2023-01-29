# Python script to update tables in confluence based on OpenAPI spec

# About

This script is used to update tables in confluence based on OpenAPI spec. 

The goal is to take OpenAPI spec like this:
[image](example-spec.png)
and make it look like a table in confluence like this:
[image](example-table.png)

# Getting started

# Install dependencies
```bash
pip install -r requirements.txt
```

# Configuration
```bash
export CONFLUENCE_URL=https://confluence.example.com
export JIRA_EMAIL=confluence_user_email@example.com
export JIRA_TOKEN=PERSONAL_API_TOKEN
export CONFLUENCE_SPACE=confluence_space
```

# Run the script
```bash
python update_confluence.py
```
