# Mba Scraper

AWS Lambda code that scrapes schedule from MBA League website and returns .ics calendar with games.

### Running Tests

```bash
just test
```

### Code Style

The project uses Ruff for linting and formatting, all linters can be run with `just`:

```bash
just lint_full
just lint_full_ff  # (fast-fail mode)
just all  # (lint + tests)
just all_ff  # (lint + tests in fast-fail mode)
```

## Building and Deployment

### Building the Lambda Package

The project includes a build system that packages the application for AWS Lambda deployment:

```bash
just build
```

This command:
1. Clears the previous build directory (`build/pkg`)
2. Generates a frozen requirements file without dev dependencies
3. Installs all dependencies targeting `x86_64-manylinux2014` platform (compatible with AWS Lambda)
4. Copies the lambda handler shim (`lambda_function.py`) to the package
5. Creates a timestamped zip file in the `build/` directory (e.g., `mba_scraper_20260201_005935.zip`)

The resulting zip file contains:
- All Python dependencies (requests, beautifulsoup4, icalendar, aws-lambda-powertools, etc.)
- The `mba_scraper` package with your application code
- A `lambda_function.py` shim that exposes the handler

### Lambda Handler Shim

The project uses a shim file (`lambda_function.py`) at the root level to expose the Lambda handler:

This allows AWS Lambda to use the default handler configuration `lambda_function.lambda_handler` while keeping the actual implementation inside the `mba_scraper` package.

**Package Structure:**
```
build/pkg/
├── lambda_function.py          # Shim that exposes the handler
├── mba_scraper/
│   ├── __init__.py
│   ├── lambda_function.py      # Actual handler implementation
│   └── ...
├── requests/
├── aws_lambda_powertools/
└── ... (other dependencies)
```

**Note:** The shim file can be safely deleted if you update the AWS Lambda **Runtime settings** → **Handler** configuration to point directly to `mba_scraper.lambda_function.lambda_handler`.
