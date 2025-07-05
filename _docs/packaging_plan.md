# BugIt CLI Packaging Plan

## Executive Summary

This document outlines the comprehensive plan to convert the BugIt CLI codebase into a proper installable Python package that can be distributed via PyPI, installed with pip, and used as both a CLI tool and a Python library.

## Current State Analysis

### Project Structure
```
bugit/
├── .git/
├── _docs/                    # Documentation
├── commands/                 # Command implementations  
├── core/                     # Core modules
├── tests/                    # Test suite (447 tests, 91% coverage)
├── mcp_local/               # MCP server integration
├── bugit.py                 # Main entry point (CLI/shell router)
├── cli.py                   # CLI application (Typer-based)
├── shell.py                 # Interactive shell
├── requirements.txt         # Production dependencies
├── requirements-dev.txt     # Development dependencies
├── pytest.ini             # Test configuration
├── .bugitrc               # Default configuration
├── cursor_mcp_config.json # MCP configuration
└── README.md              # Comprehensive documentation
```

### Key Characteristics
- **Language**: Python 3.8+ (based on dependencies)
- **CLI Framework**: Typer with Rich for styling
- **AI Integration**: LangGraph + OpenAI API
- **Testing**: pytest with 91% coverage
- **Current Usage**: Direct Python execution (`python bugit.py`)
- **Target Usage**: Installable package (`pip install bugit-cli`)

## Packaging Strategy

### 1. Modern Python Packaging Approach

We'll use **pyproject.toml** (PEP 621) as the primary configuration file, which is the modern standard for Python packaging, replacing the older setup.py approach.

### 2. Package Structure Transformation

**Current**: Flat structure with modules in root
**Target**: Proper package structure with source layout

```
bugit-cli/
├── src/
│   └── bugit/
│       ├── __init__.py
│       ├── __main__.py          # Entry point for `python -m bugit`
│       ├── cli.py               # CLI application
│       ├── shell.py             # Interactive shell
│       ├── core/                # Core modules
│       │   ├── __init__.py
│       │   ├── config.py
│       │   ├── console.py
│       │   ├── errors.py
│       │   ├── model.py
│       │   ├── schema.py
│       │   ├── storage.py
│       │   └── styles.py
│       ├── commands/            # Command implementations
│       │   ├── __init__.py
│       │   ├── new.py
│       │   ├── list.py
│       │   ├── show.py
│       │   ├── edit.py
│       │   ├── delete.py
│       │   ├── config.py
│       │   └── server.py
│       └── mcp_local/          # MCP server integration
├── tests/                       # Test suite
├── docs/                        # Documentation (renamed from _docs)
├── pyproject.toml              # Modern packaging configuration
├── README.md                   # Package description
├── LICENSE                     # License file
├── CHANGELOG.md               # Version history
├── .gitignore                 # Git ignore patterns
└── scripts/                   # Build and development scripts
```

### 3. Distribution Strategy

**Primary Distribution**: PyPI (Python Package Index)
- Package name: `bugit-cli` (to avoid conflicts with existing packages)
- Command name: `bugit` (via console_scripts entry point)

**Secondary Distribution**: GitHub Releases
- Source distribution (.tar.gz)
- Built distribution (.whl)
- Pre-built binaries (future enhancement)

## Implementation Plan

### Phase 1: Package Structure Setup

#### 1.1 Create Package Directory Structure
```bash
mkdir -p src/bugit/core
mkdir -p src/bugit/commands
mkdir -p src/bugit/mcp_local
mkdir -p scripts
mkdir -p docs
```

#### 1.2 Move and Reorganize Files
```bash
# Move core modules
mv core/* src/bugit/core/
mv commands/* src/bugit/commands/
mv mcp_local/* src/bugit/mcp_local/

# Move main files
mv cli.py src/bugit/
mv shell.py src/bugit/

# Move documentation
mv _docs/* docs/

# Create __init__.py files
touch src/bugit/__init__.py
touch src/bugit/core/__init__.py
touch src/bugit/commands/__init__.py
touch src/bugit/mcp_local/__init__.py
```

#### 1.3 Create Entry Point Module
Create `src/bugit/__main__.py` for `python -m bugit` support and `src/bugit/main.py` for the console script entry point.

### Phase 2: Configuration Files

#### 2.1 Create pyproject.toml
```toml
[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[project]
name = "bugit-cli"
dynamic = ["version"]
description = "AI-powered bug report management CLI"
readme = "README.md"
license = {text = "MIT"}
authors = [
    {name = "BugIt Team", email = "contact@bugit.dev"},
]
maintainers = [
    {name = "BugIt Team", email = "contact@bugit.dev"},
]
classifiers = [
    "Development Status :: 5 - Production/Stable",
    "Environment :: Console",
    "Intended Audience :: Developers",
    "License :: OSI Approved :: MIT License",
    "Operating System :: OS Independent",
    "Programming Language :: Python :: 3",
    "Programming Language :: Python :: 3.8",
    "Programming Language :: Python :: 3.9",
    "Programming Language :: Python :: 3.10",
    "Programming Language :: Python :: 3.11",
    "Programming Language :: Python :: 3.12",
    "Topic :: Software Development :: Bug Tracking",
    "Topic :: Software Development :: Quality Assurance",
    "Topic :: Utilities",
]
keywords = ["bug", "tracking", "cli", "ai", "development", "automation"]
requires-python = ">=3.8"
dependencies = [
    "annotated-types>=0.7.0",
    "anyio>=4.9.0",
    "certifi>=2025.6.15",
    "charset-normalizer>=3.4.2",
    "click>=8.2.1",
    "colorama>=0.4.6",
    "distro>=1.9.0",
    "h11>=0.16.0",
    "httpcore>=1.0.9",
    "httpx>=0.28.1",
    "idna>=3.10",
    "jiter>=0.10.0",
    "jsonpatch>=1.33",
    "jsonpointer>=3.0.0",
    "langchain-core>=0.3.67",
    "langchain-openai>=0.3.27",
    "langgraph>=0.5.0",
    "langgraph-checkpoint>=2.1.0",
    "langgraph-prebuilt>=0.5.2",
    "langgraph-sdk>=0.1.72",
    "langsmith>=0.4.4",
    "markdown-it-py>=3.0.0",
    "mdurl>=0.1.2",
    "openai>=1.93.0",
    "orjson>=3.10.18",
    "ormsgpack>=1.10.0",
    "packaging>=24.2",
    "psutil>=6.1.0",
    "pydantic>=2.11.7",
    "pydantic-core>=2.33.2",
    "Pygments>=2.19.2",
    "python-dotenv>=1.1.1",
    "PyYAML>=6.0.2",
    "regex>=2024.11.6",
    "requests>=2.32.4",
    "requests-toolbelt>=1.0.0",
    "rich>=14.0.0",
    "shellingham>=1.5.4",
    "sniffio>=1.3.1",
    "tenacity>=9.1.2",
    "tiktoken>=0.9.0",
    "tqdm>=4.67.1",
    "typer>=0.16.0",
    "typing-extensions>=4.14.0",
    "urllib3>=2.5.0",
    "xxhash>=3.5.0",
    "zstandard>=0.23.0",
    "mcp[cli]>=1.0.0",
]

[project.optional-dependencies]
dev = [
    "pytest>=8.0.0",
    "pytest-cov>=4.0.0",
    "pytest-asyncio>=1.0.0",
    "black>=23.0.0",
    "isort>=5.12.0",
    "mypy>=1.0.0",
    "types-requests>=2.31.0",
    "coverage>=7.9.1",
    "build>=0.10.0",
    "twine>=4.0.0",
]

[project.urls]
Homepage = "https://github.com/your-org/bugit-cli"
Repository = "https://github.com/your-org/bugit-cli"
Documentation = "https://bugit-cli.readthedocs.io"
"Bug Tracker" = "https://github.com/your-org/bugit-cli/issues"
Changelog = "https://github.com/your-org/bugit-cli/blob/main/CHANGELOG.md"

[project.scripts]
bugit = "bugit.main:main"

[tool.hatch.version]
path = "src/bugit/__init__.py"

[tool.hatch.build.targets.sdist]
include = [
    "/src",
    "/tests",
    "/docs",
    "/README.md",
    "/LICENSE",
    "/CHANGELOG.md",
]

[tool.hatch.build.targets.wheel]
packages = ["src/bugit"]

[tool.black]
line-length = 88
target-version = ["py38"]
include = '\.pyi?$'
extend-exclude = '''
/(
  # directories
  \.eggs
  | \.git
  | \.hg
  | \.mypy_cache
  | \.tox
  | \.venv
  | _build
  | buck-out
  | build
  | dist
)/
'''

[tool.isort]
profile = "black"
line_length = 88
multi_line_output = 3
include_trailing_comma = true
force_grid_wrap = 0
use_parentheses = true
ensure_newline_before_comments = true

[tool.mypy]
python_version = "3.8"
warn_return_any = true
warn_unused_configs = true
disallow_untyped_defs = true
disallow_incomplete_defs = true
check_untyped_defs = true
disallow_untyped_decorators = true
no_implicit_optional = true
warn_redundant_casts = true
warn_unused_ignores = true
warn_no_return = true
warn_unreachable = true
strict_equality = true

[tool.pytest.ini_options]
testpaths = ["tests"]
python_files = ["test_*.py", "*_test.py"]
python_classes = ["Test*"]
python_functions = ["test_*"]
addopts = [
    "--strict-markers",
    "--strict-config",
    "--cov=src/bugit",
    "--cov-report=term-missing",
    "--cov-report=html",
    "--cov-report=xml",
]
markers = [
    "slow: marks tests as slow (deselect with '-m \"not slow\"')",
    "integration: marks tests as integration tests",
    "unit: marks tests as unit tests",
]

[tool.coverage.run]
source = ["src/bugit"]
branch = true
omit = [
    "*/tests/*",
    "*/test_*",
    "*/conftest.py",
    "src/bugit/__main__.py",
]

[tool.coverage.report]
exclude_lines = [
    "pragma: no cover",
    "def __repr__",
    "raise AssertionError",
    "raise NotImplementedError",
    "if __name__ == .__main__.:",
    "if TYPE_CHECKING:",
    "class .*\\bProtocol\\):",
    "@(abc\\.)?abstractmethod",
]
```

#### 2.2 Create Other Configuration Files

**LICENSE** (MIT License)
**CHANGELOG.md** (Version history)
**MANIFEST.in** (Additional files for source distribution)

### Phase 3: Code Modifications

#### 3.1 Update Import Statements
All relative imports need to be updated to use the new package structure:
```python
# Old
from core.config import Config
from commands.new import new

# New
from bugit.core.config import Config
from bugit.commands.new import new
```

#### 3.2 Create Entry Points
```python
# src/bugit/__main__.py
"""Allow bugit to be executed as a module with python -m bugit."""
from bugit.main import main

if __name__ == "__main__":
    main()
```

```python
# src/bugit/main.py
"""Main entry point for the bugit CLI."""
import sys
from pathlib import Path

def main():
    """Main entry point - routes to shell or CLI based on arguments"""
    if len(sys.argv) > 1:
        from bugit.cli import app
        app()
    else:
        from bugit.shell import main as shell_main
        shell_main()

if __name__ == "__main__":
    main()
```

#### 3.3 Update Version Management
```python
# src/bugit/__init__.py
"""BugIt CLI - AI-powered bug report management tool."""

__version__ = "1.0.0"
__author__ = "BugIt Team"
__email__ = "contact@bugit.dev"
__description__ = "AI-powered bug report management CLI"

# Export main components
from bugit.core.config import Config
from bugit.core.model import IssueModel
from bugit.core.schema import IssueSchema
from bugit.core.storage import Storage

__all__ = [
    "__version__",
    "__author__",
    "__email__",
    "__description__",
    "Config",
    "IssueModel", 
    "IssueSchema",
    "Storage",
]
```

### Phase 4: Testing Updates

#### 4.1 Update Test Imports
All test files need to be updated to use the new package structure:
```python
# Old
from core.config import Config

# New
from bugit.core.config import Config
```

#### 4.2 Update Test Configuration
```python
# tests/conftest.py updates
import sys
from pathlib import Path

# Add src to path for testing
src_path = Path(__file__).parent.parent / "src"
sys.path.insert(0, str(src_path))
```

### Phase 5: Documentation Updates

#### 5.1 Update README.md
- Update installation instructions
- Add pip install method
- Update usage examples
- Add development setup instructions

#### 5.2 Create Additional Documentation
- **CONTRIBUTING.md**: Development guidelines
- **SECURITY.md**: Security policy
- **CODE_OF_CONDUCT.md**: Community guidelines

### Phase 6: Build and Distribution Setup

#### 6.1 Build Scripts
```bash
# scripts/build.sh
#!/bin/bash
set -e

echo "Building BugIt CLI package..."

# Clean previous builds
rm -rf dist/ build/ src/bugit.egg-info/

# Build package
python -m build

echo "Build complete. Files in dist/:"
ls -la dist/
```

#### 6.2 Development Setup Script
```bash
# scripts/dev-setup.sh
#!/bin/bash
set -e

echo "Setting up BugIt CLI development environment..."

# Create virtual environment
python -m venv venv
source venv/bin/activate

# Install package in development mode
pip install -e .[dev]

# Run tests to verify setup
pytest

echo "Development environment ready!"
```

#### 6.3 Release Script
```bash
# scripts/release.sh
#!/bin/bash
set -e

if [ -z "$1" ]; then
    echo "Usage: $0 <version>"
    exit 1
fi

VERSION=$1

echo "Releasing BugIt CLI version $VERSION..."

# Update version in __init__.py
sed -i "s/__version__ = \".*\"/__version__ = \"$VERSION\"/" src/bugit/__init__.py

# Build package
python -m build

# Upload to PyPI (requires authentication)
python -m twine upload dist/*

echo "Release $VERSION complete!"
```

## Migration Checklist

### Pre-Migration
- [ ] Backup current codebase
- [ ] Ensure all tests pass
- [ ] Document current functionality
- [ ] Plan import statement changes

### Structure Migration
- [ ] Create new directory structure
- [ ] Move files to new locations
- [ ] Create __init__.py files
- [ ] Update import statements
- [ ] Create entry point modules

### Configuration
- [ ] Create pyproject.toml
- [ ] Create LICENSE file
- [ ] Create CHANGELOG.md
- [ ] Update .gitignore
- [ ] Create build scripts

### Testing
- [ ] Update test imports
- [ ] Update test configuration
- [ ] Run full test suite
- [ ] Verify coverage maintains 90%+

### Documentation
- [ ] Update README.md
- [ ] Create CONTRIBUTING.md
- [ ] Update all documentation links
- [ ] Create API documentation

### Build and Distribution
- [ ] Test local build
- [ ] Test local installation
- [ ] Test console script
- [ ] Test `python -m bugit`
- [ ] Create test PyPI upload
- [ ] Create production PyPI upload

## Post-Migration Benefits

### For Users
1. **Easy Installation**: `pip install bugit-cli`
2. **Global Command**: `bugit` available system-wide
3. **Module Usage**: `python -m bugit` support
4. **Dependency Management**: Automatic dependency resolution
5. **Virtual Environment Support**: Clean environment isolation

### For Developers
1. **Standard Structure**: Follows Python packaging best practices
2. **Easy Development**: `pip install -e .` for development
3. **Automated Testing**: CI/CD integration ready
4. **Version Management**: Automated version handling
5. **Distribution**: Easy PyPI publishing

### For Library Usage
1. **Importable Package**: `from bugit import Config`
2. **Programmatic Access**: Use BugIt in other Python projects
3. **API Documentation**: Sphinx-ready documentation
4. **Type Hints**: Full mypy support

## Risk Mitigation

### Import Compatibility
- Maintain backward compatibility for existing scripts
- Provide migration guide for users
- Test all import paths thoroughly

### Dependency Management
- Lock dependency versions for stability
- Test with multiple Python versions
- Use conservative version constraints

### Distribution
- Test on multiple platforms
- Verify all entry points work
- Test installation in clean environments

## Timeline

### Week 1: Structure Setup
- Create new directory structure
- Move and reorganize files
- Create entry point modules

### Week 2: Configuration and Testing
- Create pyproject.toml
- Update import statements
- Fix and run test suite

### Week 3: Documentation and Build
- Update documentation
- Create build scripts
- Test local builds

### Week 4: Distribution
- Create PyPI account
- Test PyPI upload
- Production release

## Success Metrics

1. **Installation Success**: `pip install bugit-cli` works on all platforms
2. **Command Availability**: `bugit` command available after installation
3. **Test Coverage**: Maintain 90%+ test coverage
4. **Documentation**: Complete and accurate documentation
5. **Distribution**: Available on PyPI with proper metadata

## Future Enhancements

1. **Binary Distribution**: PyInstaller/Nuitka binaries
2. **Homebrew Formula**: macOS package manager support
3. **Debian Package**: .deb package for Ubuntu/Debian
4. **Docker Image**: Containerized distribution
5. **Snap Package**: Universal Linux package

This plan provides a comprehensive roadmap for converting BugIt CLI into a professional, installable Python package while maintaining all existing functionality and improving the user experience.