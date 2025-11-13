# Contributing to Moodle AI Assistant

Thank you for considering contributing to the Moodle AI Assistant project!

## How to Contribute

### Reporting Bugs

If you find a bug, please create an issue with:
- Clear description of the problem
- Steps to reproduce
- Expected vs actual behavior
- Environment details (Moodle version, PHP version, etc.)
- Error messages or logs

### Suggesting Features

Feature suggestions are welcome! Please create an issue with:
- Clear description of the feature
- Use case and benefits
- Any technical considerations

### Pull Requests

1. **Fork the repository**
2. **Create a feature branch**: `git checkout -b feature/your-feature-name`
3. **Make your changes**:
   - Follow existing code style
   - Add comments where needed
   - Update documentation
4. **Test thoroughly**:
   - Test in Moodle environment
   - Verify backend functionality
   - Check all themes work
5. **Commit with clear messages**:
   ```
   Add feature: Brief description

   Detailed explanation of changes
   ```
6. **Push to your fork**: `git push origin feature/your-feature-name`
7. **Create a Pull Request**

## Development Setup

See [INSTALLATION.md](INSTALLATION.md) for setup instructions.

For development:

```bash
# Backend with hot reload
cd backend
uvicorn app.main:app --reload

# Watch Moodle logs
tail -f /path/to/moodle/moodledata/error.log
```

## Code Style

### Python
- Follow PEP 8
- Use type hints
- Document functions with docstrings
- Keep functions focused and small

### PHP
- Follow Moodle coding standards
- Use proper documentation blocks
- Include version information

### JavaScript
- Follow Moodle AMD module format
- Use ES6+ features
- Add JSDoc comments

### CSS
- Use BEM naming convention
- Keep selectors specific
- Document complex styles

## Adding New Features

### New Themes

1. Create CSS file in `styles/themes/{theme-name}.css`
2. Add theme to language strings in `lang/en/local_aiassistant.php`
3. Add option to settings in `settings.php`
4. Update documentation

### New Document Types

1. Create loader in `backend/app/services/ingest/`
2. Update `document_service.py`
3. Add API endpoint in `backend/app/api/ingest.py`
4. Update Moodle interface in `manage_documents.php`
5. Update documentation

### New LLM Providers

1. Add provider to `backend/app/services/llm_service.py`
2. Update configuration in `backend/app/config.py`
3. Add settings in Moodle `settings.php`
4. Update documentation

## Testing

### Backend Tests

```bash
cd backend
pytest
```

### Moodle Tests

Follow Moodle's PHPUnit testing guidelines.

### Manual Testing Checklist

- [ ] Chat functionality works
- [ ] Document upload works (PDF)
- [ ] URL ingestion works
- [ ] All themes display correctly
- [ ] Age-based responses work
- [ ] Web search works (if enabled)
- [ ] Chat history saves and loads
- [ ] Settings save correctly
- [ ] Permissions work as expected

## Documentation

When adding features, update:
- README.md
- INSTALLATION.md
- Inline code comments
- API documentation
- Language strings

## Version Control

- Keep commits atomic and focused
- Write clear commit messages
- Reference issues in commits: `Fixes #123`
- Don't commit sensitive data (API keys, credentials)

## Code Review Process

All contributions go through code review:
1. Automated checks (linting, tests)
2. Manual review by maintainers
3. Request for changes if needed
4. Approval and merge

## Community Guidelines

- Be respectful and constructive
- Help others learn and grow
- Focus on the code, not the person
- Follow Moodle community standards

## Questions?

- Open an issue for questions
- Check existing issues first
- Be patient - maintainers are volunteers

## License

By contributing, you agree that your contributions will be licensed under the GNU GPL v3 license.

Thank you for contributing! 🎉
