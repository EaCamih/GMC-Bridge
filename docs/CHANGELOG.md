# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [1.0.0] - 2026-09-29

### Added
- Initial release based on smtc-bridge
- Cross-platform support for Windows (SMTC) and Linux (MPRIS)
- System tray integration for both platforms
- Auto-startup functionality for Windows and Linux
- REST API endpoints for media information
- Thumbnail caching with LRU eviction
- Rate limiting to prevent excessive CPU usage
- GitHub Actions workflow for automated builds
- Semantic release configuration for automated versioning
- Comprehensive documentation

### Features
- Windows SMTC API integration for media control
- Linux MPRIS D-Bus integration for media control
- Base64 encoded artwork in API responses
- Single instance check to prevent conflicts
- Crash logging with automatic cleanup
- Configurable server host and port
- JSON API endpoint for current media state
- HTML endpoint for active sessions list

[Unreleased]: https://github.com/yourusername/GMC-Bridge/compare/v1.0.0...HEAD
[1.0.0]: https://github.com/yourusername/GMC-Bridge/releases/tag/v1.0.0
