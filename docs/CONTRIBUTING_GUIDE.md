# Contributing Guide

> Guidelines for contributing to the Local Council Data Explorer project.

---

## Table of Contents

- [Getting Started](#getting-started)
- [Development Setup](#development-setup)
- [Contribution Workflow](#contribution-workflow)
- [Code Standards](#code-standards)
- [Pull Request Guidelines](#pull-request-guidelines)
- [Testing Requirements](#testing-requirements)
- [Documentation](#documentation)
- [Community Guidelines](#community-guidelines)

---

## Getting Started

Thank you for your interest in contributing to the Local Council Data Explorer! This document outlines the process and guidelines for contributing.

### Ways to Contribute

| Contribution Type | Description |
|-------------------|-------------|
| 🐛 Bug Reports | Report issues you've found |
| ✨ Feature Requests | Suggest new features |
| 📝 Documentation | Improve docs and guides |
| 🧪 Tests | Add or improve tests |
| 💻 Code | Fix bugs or implement features |
| 🎨 Design | UI/UX improvements |

---

## Development Setup

### Prerequisites

- Python 3.11+
- Node.js 20+
- Docker and Docker Compose (optional)
- Git

### Local Setup

1. **Fork the repository**
   
   Click "Fork" on GitHub to create your copy.

2. **Clone your fork**
   ```bash
   git clone https://github.com/YOUR-USERNAME/local-council-data-explorer.git
   cd local-council-data-explorer
   ```

3. **Set up backend**
   ```bash
   cd backend
   python -m venv .venv
   source .venv/bin/activate  # or .venv\Scripts\activate on Windows
   pip install -r requirements.txt
   ```

4. **Set up frontend**
   ```bash
   cd frontend
   npm install
   ```

5. **Start development servers**
   ```bash
   # Terminal 1: Backend
   cd backend
   uvicorn main:app --reload

   # Terminal 2: Frontend
   cd frontend
   npm run dev
   ```

6. **Verify everything works**
   - Frontend: http://localhost:5173
   - Backend: http://localhost:8000/docs

---

## Contribution Workflow

### 1. Create a Branch

```bash
# Sync with upstream first
git fetch origin
git checkout main
git pull origin main

# Create feature branch
git checkout -b feature/your-feature-name
```

### Branch Naming Convention

| Type | Pattern | Example |
|------|---------|---------|
| Feature | `feature/description` | `feature/add-council-search` |
| Bug Fix | `fix/description` | `fix/cache-expiration` |
| Documentation | `docs/description` | `docs/api-examples` |
| Refactor | `refactor/description` | `refactor/service-layer` |

### 2. Make Changes

- Write clean, well-documented code
- Follow the code standards (below)
- Add/update tests as needed
- Update documentation if necessary

### 3. Commit Changes

```bash
git add .
git commit -m "feat: add new council search feature"
```

#### Commit Message Format

We follow [Conventional Commits](https://www.conventionalcommits.org/):

```
<type>(<scope>): <description>

[optional body]

[optional footer]
```

**Types**:

| Type | Description |
|------|-------------|
| `feat` | New feature |
| `fix` | Bug fix |
| `docs` | Documentation only |
| `style` | Formatting, no code change |
| `refactor` | Code change, no new feature |
| `test` | Adding tests |
| `chore` | Maintenance tasks |

**Examples**:

```bash
git commit -m "feat(bins): add support for garden waste bins"
git commit -m "fix(cache): correct TTL expiration calculation"
git commit -m "docs: update API reference with new endpoints"
```

### 4. Push and Create PR

```bash
git push origin feature/your-feature-name
```

Then create a Pull Request on GitHub.

---

## Code Standards

### Python (Backend)

#### Style

- Follow [PEP 8](https://pep8.org/)
- Use [Black](https://black.readthedocs.io/) for formatting
- Use [Ruff](https://docs.astral.sh/ruff/) for linting
- Maximum line length: 88 characters

#### Type Hints

All functions must have type hints:

```python
async def get_bin_collections(
    self,
    postcode: Optional[str],
    uprn: Optional[str],
) -> BinCollectionResponse:
    ...
```

#### Docstrings

Use Google-style docstrings:

```python
def calculate_days_until(collection_date: date) -> int:
    """Calculate days until a collection date.
    
    Args:
        collection_date: The date of the collection.
    
    Returns:
        Number of days until the collection date.
        Returns 0 if the date is today or in the past.
    
    Raises:
        ValueError: If collection_date is None.
    """
    ...
```

#### Formatting

```bash
# Format with Black
black backend/

# Lint with Ruff
ruff check backend/
```

### TypeScript (Frontend)

#### Style

- Follow ESLint configuration
- Use Prettier for formatting
- Use strict TypeScript mode

#### Type Safety

- No `any` types
- Explicit return types for functions
- Interfaces for all props and API responses

```typescript
interface BinPanelProps {
  data: BinCollectionResponse | null;
  loading: boolean;
  error: string | null;
  onRetry: () => void;
}

export default function BinPanel({ 
  data, 
  loading, 
  error, 
  onRetry 
}: BinPanelProps): JSX.Element {
  ...
}
```

#### Formatting

```bash
# Lint and fix
npm run lint

# Format with Prettier
npx prettier --write "src/**/*.{ts,tsx}"
```

---

## Pull Request Guidelines

### Before Submitting

- [ ] Code follows project style guidelines
- [ ] All tests pass locally
- [ ] New code has appropriate tests
- [ ] Documentation is updated if needed
- [ ] Commit messages follow conventions

### PR Description Template

```markdown
## Description
Brief description of the changes.

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Documentation update
- [ ] Refactoring
- [ ] Other (please describe)

## Testing
Describe how you tested these changes.

## Screenshots (if applicable)
Add screenshots for UI changes.

## Checklist
- [ ] My code follows the project style guidelines
- [ ] I have added tests that prove my fix/feature works
- [ ] All new and existing tests pass
- [ ] I have updated documentation as needed
```

### Review Process

1. **Automated Checks** - CI runs tests and linting
2. **Code Review** - Maintainers review the changes
3. **Feedback** - Address any requested changes
4. **Approval** - PR is approved and merged

---

## Testing Requirements

### Backend Tests

```bash
cd backend
pytest
```

#### Test Coverage

- All new features must have tests
- Bug fixes should include regression tests
- Aim for high test coverage

#### Test Patterns

```python
import pytest
from services.bins_service import BinsService

@pytest.fixture
def service():
    """Create service instance for tests."""
    return BinsService()

@pytest.mark.asyncio
async def test_get_bins_with_valid_postcode(service):
    """Test bin collection retrieval with valid postcode."""
    result = await service.get_bin_collections("YO1 1AA", None)
    
    assert result.council == "City of York Council"
    assert len(result.bins) > 0
```

### Frontend Tests

```bash
cd frontend
npm run lint
```

Currently, the frontend uses TypeScript for type-checking. Additional testing with React Testing Library is encouraged for new features.

---

## Documentation

### When to Update Docs

- Adding new features
- Changing API endpoints
- Modifying configuration options
- Adding new dependencies

### Documentation Files

| File | Purpose |
|------|---------|
| `README.md` | Project overview |
| `docs/ARCHITECTURE_OVERVIEW.md` | System architecture |
| `docs/BACKEND_STRUCTURE.md` | Backend details |
| `docs/FRONTEND_STRUCTURE.md` | Frontend details |
| `docs/DEPLOYMENT_GUIDE.md` | Deployment instructions |
| `docs/TROUBLESHOOTING.md` | Common issues |
| `API_REFERENCE.md` | API documentation |

### Documentation Style

- Use clear, concise language
- Include code examples
- Use tables for structured data
- Add diagrams where helpful

---

## Community Guidelines

### Code of Conduct

- Be respectful and inclusive
- Constructive feedback only
- Help others learn
- Assume good intentions

### Getting Help

- **Questions**: Open a GitHub Discussion
- **Bugs**: Open a GitHub Issue
- **Security**: Report privately (see SECURITY.md)

### Recognition

Contributors are acknowledged in:

- GitHub contributors list
- Release notes for significant contributions

---

## Quick Reference

### Common Commands

```bash
# Backend
cd backend
source .venv/bin/activate
uvicorn main:app --reload
pytest
black .
ruff check .

# Frontend
cd frontend
npm run dev
npm run build
npm run lint

# Docker
docker compose up -d
docker compose logs -f
docker compose down
```

### Useful Links

- [Project README](../README.md)
- [API Reference](../API_REFERENCE.md)
- [Architecture](./ARCHITECTURE_OVERVIEW.md)
- [Troubleshooting](./TROUBLESHOOTING.md)

---

Thank you for contributing to the Local Council Data Explorer! 🙏
