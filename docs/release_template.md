## Release Process

### Semantic Versioning
We follow semantic versioning: `major.minor.patch` (e.g., `v1.2.3`)

**Major Release (v2.0.0)** - Breaking changes requiring user action:
- Configuration file format changes
- Removed or renamed features
- API changes that break existing integrations

**Minor Release (v1.1.0)** - New features that are backward compatible:
- New authentication methods
- Additional file type support
- New UI features
- Performance improvements

**Patch Release (v1.0.1)** - Bug fixes and security updates:
- Security vulnerabilities
- Bug fixes
- Documentation corrections
- Dependency updates

### Release Template
```txt
# Navigator v1.2.3

## What's Changed
- Brief description of changes
- Use past tense ("Added", "Fixed", "Updated")
- Group by type: Features, Bug Fixes, Security, etc.

## Breaking Changes (if major release)
- List any breaking changes
- Include migration instructions

## Upgrade Notes
- Any special upgrade considerations
- Configuration changes needed

**Full Changelog**: https://github.com/thatsnotamuffin/efs-navigator/compare/v1.2.2...v1.2.3
```
