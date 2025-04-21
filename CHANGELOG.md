# Changelog

All notable changes to the Belgian Bingo Game will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Planned
- Enhanced animations for ball drawing
- Improved UI design and transitions
- Sound effect improvements
- Multiple player cards support
- Network play capability

## [0.1.0] - 2025-04-21

### Added
- Initial game implementation
- 5x5 Belgian bingo card layout
- Ball drawing system with Arduino hardware integration
- Sound effects and background music
- Auto-detection for Arduino hardware
- Fallback simulation mode
- Settings menu with customization options:
  - Serial settings (port, auto-detect)
  - Display settings (resolution, fullscreen)
  - Audio settings (music/SFX volume)
  - Game settings (ball draw speed, winning pattern)
- Win detection for various patterns (horizontal, vertical, diagonal, corners, full card)
- Score tracking

### Fixed
- Win detection logic improvement
- Settings menu navigation bug
- Arduino connection handling

### Known Issues
- Some operating systems may have issues with font rendering
- Arduino auto-detection can pick up system ports incorrectly
- Settings button functionality may be unreliable on some systems