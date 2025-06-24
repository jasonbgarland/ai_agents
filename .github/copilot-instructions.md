# Copilot Instructions

## Code Style & Preferences

### Important General Guidelines

- I want to learn and improve my skills and knowledge, so please provide explanations for your suggestions
- Always break down solutions into steps and confirm before proceeding
- Follow test driven development (TDD) principles as much as possible
- Prefer iterative solutions, start small and iterate
- Write comments for complex logic

### Language-Specific Preferences

#### Python

- Follow PEP 8 style guidelines
- Use type hints for function parameters and return values
- Prefer f-strings for string formatting
- Use descriptive variable names (avoid abbreviations)
- Use xUnit style tests using the built in `unittest` module
- Do not use the `__all__` pattern in `__init__.py` files; importing \* is not a preferred pattern in this project

## Architecture & Patterns

- Prefer composition over inheritance
- Use dependency injection where appropriate
- Follow SOLID principles

## File Organization

- Group related files in appropriate directories
- Use consistent naming conventions for files and folders
- Keep configuration files in the root or a dedicated config directory
- Separate source code from tests and documentation

## Testing Preferences

- Write unit tests for new functions and classes
- Use descriptive test names that explain what is being tested
- Include both positive and negative test cases
- Mock external dependencies in tests
- When asserting equality, the first parameter should be the expected value, and the second should be the actual value

## Documentation

- Include README files for each major component
- Document public APIs and interfaces
- Explain complex algorithms or business logic
- Keep documentation up to date with code changes

## Specific Instructions for Copilot

### When Suggesting Code:

- Suggest meaningful variable names based on context
- Optimize for readability over cleverness

### When Refactoring:

- Maintain existing functionality
- Improve code organization and clarity
- Add missing error handling
- Update documentation if needed
- Suggest breaking changes only when significantly beneficial

### For New Features:

- Start with a clear interface or API design
- Include appropriate logging, especially for debugging purposes.
- Add configuration options where useful

### Technologies I Use:

- Frontend: React
- Backend: Python
- Databases: PostgreSQL, MongoDB, Redis
- Cloud Platforms: Azure
- Development Tools: Docker, CI/CD tools

- Validation: pydantic

## Security Considerations

- Always validate user input
- Don't commit secrets or API keys
