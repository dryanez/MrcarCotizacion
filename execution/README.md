# Execution Scripts

This directory contains deterministic Python scripts that handle:
- API calls
- Data processing
- File operations
- Database interactions

## Principles

**Reliability**: Scripts should be deterministic and testable
**Clarity**: Well-commented code
**Reusability**: Modular functions that can be called independently
**Error Handling**: Graceful failures with clear error messages

## Usage

Scripts are called by the AI orchestration layer (Layer 2) after reading the corresponding directive.

Environment variables and API keys are loaded from `.env` in the project root.

## Template

```python
#!/usr/bin/env python3
"""
Script description here
"""

import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def main():
    """Main execution function"""
    pass

if __name__ == "__main__":
    main()
```
