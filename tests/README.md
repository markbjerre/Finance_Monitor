# Tests

This directory contains unit tests for the Finance Dashboard application.

## Running Tests

### Run all tests:
```powershell
python -m pytest tests/ -v
```

### Run specific test file:
```powershell
python tests/test_supabase.py
```

### Run with pytest (after installing):
```powershell
pip install pytest
pytest tests/test_supabase.py -v
```

## Test Files

- `test_supabase.py` - Tests Supabase database connection and operations
- More test files will be added as we build services

## Coverage (optional)

To run tests with coverage:
```powershell
pip install pytest-cov
pytest tests/ --cov=. --cov-report=html
```
