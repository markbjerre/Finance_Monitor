# Project: My Awesome App

## Project Description
This will be a personal finance tracking and AI hobby exploration site. It is part of a bigger hobby-website project, and will be part of that eco-system. It will however be stand-alone, with option for connecting to API's, AI models and have webscrape for news. 

The project wil will be a dashboard showing stock price (as live as possible), Top news stories (pulled from API). And the website should have AI generated commentary on buy ideas or macro data insights. 

This file will guide your thoughts, adhere to the principles and re-read these instructions carefully often. 

## Tech Stack (proposed, do not overthink this yet)
- **Frontend**: Flask with Jinja2 templates, HTML/CSS, Bootstrap
- **Backend**: Python 3.x, Flask web framework
- **Database**: PostgreSQL (primary production) + Parquet files (portable backup)
- **Data Processing**: Pandas, NumPy for data manipulation and analysis
- **API Integration**: public live data free websites. 
- **Data Formats**: Parquet (columnar compression), CSV exports
- **Testing**: pytest (recommended for future unit tests)

Files are hosted in a VPS hosted in hostinger under the name "ai-vearkstedet.cloud". 


## Code Conventions
- 4-space indentation (Python PEP 8 standard)
- `snake_case` for variables, functions, and file names
- `UPPER_SNAKE_CASE` for constants
- `CapitalCase` for class names
- Type hints for all function signatures
- Google-style docstrings for all public functions
- Comments explaining complex logic and API quirks
- Error handling with try/except for API calls and database operations

## Project Structure
TBD


## Important Notes
- Keep everything simple until scope is expanded

## Known Issues


## Future Plans



Custom Instructions
Add specific instructions for how Claude should behave when working with your project:

## Instructions for Claude

When working on this project, please:

- **Challenge assumptions**: Question if the user's approach might have issues or if there's better logic available
- **Ask for clarity**: Request elaboration when instructions are vague or where context could provide significant additional value
- **Strive for simplicity**: Prefer simple solutions over complex ones; prevent unnecessary file proliferation
- **Archive aggressively**: Move unused files to `archive/`, delete empty folders, consolidate test scripts
- **Minimize documentation**: Keep docs in `README.md`, `TODO.md`, and `claude.md` only; use folder-specific `claude.md` only for complex directories
- **Type everything**: Always include Python type hints for all function parameters and return values
- **Optimize performance**: Prioritize performance improvements, especially for operations on 200K+ property datasets
- **Follow existing patterns**: Use established error handling, database query patterns, and API integration approaches
- **Document public functions**: Include comprehensive docstrings for all public functions and classes
- **Pandas over raw Python**: Use vectorized operations for data manipulation when possible (avoid loops)
- **SQL efficiency**: Optimize database queries; avoid N+1 problems; use proper joins and indexing
- **Production mindset**: Treat this as production code; consider edge cases, error handling, and data integrity

## Environment Setup

- Environment variables (examples, not actual values):
Architecture Diagrams

Mermaid diagrams to visualize architecture:

## Architecture

```mermaid
# EXAMPLE
graph TD
    A[Client] --> B[API Gateway]
    B --> C[Auth Service]
    B --> D[User Service]
    B --> E[Content Service]
    C --> F[(Auth DB)]
    D --> G[(User DB)]
    E --> H[(Content DB)]
```

## Component Relationships

```mermaid
# EXAMPLE
graph TD
    A[App] --> B[Layout]
    B --> C[Header]
    B --> D[Main Content]
    B --> E[Footer]
    D --> F[Dashboard]
    F --> G[UserStats]
    F --> H[ActivityFeed]
    F --> I[Recommendations]
```