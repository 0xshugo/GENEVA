# Changelog

All notable changes to GENEVA will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Fixed
- Resolved merge conflicts that caused duplicate function definitions
- Fixed syntax errors in `src/text_check.py` and `src/image_check.py`
- Fixed duplicate code in `app.py` and `README.md`
- Improved error handling in Streamlit image upload

### Added
- Comprehensive edge case tests for text and image processing
- Tests for empty strings, whitespace, non-ASCII characters
- Tests for parameter validation and error handling
- Streamlit configuration file with security settings
- File upload size limit (10MB)
- CONTRIBUTING.md with development guidelines
- CHANGELOG.md for tracking project changes

### Changed
- Pinned dependency versions for security and reproducibility
- Updated Python requirement from >=3.12 to >=3.11
- Enhanced error messages for better user experience
- Improved code documentation and type hints

### Security
- Added dependency version pinning in requirements.txt
- Configured Streamlit security settings (maxUploadSize, XSRF protection)
- Added error handling to prevent information disclosure

## [0.1.0] - 2024-12-09

### Added
- Initial release of GENEVA (Generative Ethics Validator)
- Text similarity detection using TF-IDF cosine similarity
- AI repetition score calculation using n-gram analysis
- Image similarity detection using perceptual hashing (pHash)
- Streamlit web interface with Text Check and Image Check tabs
- Unit tests for core functionality
- MIT License
- README with usage instructions and algorithm explanations

[Unreleased]: https://github.com/YOUR_USERNAME/GENEVA/compare/v0.1.0...HEAD
[0.1.0]: https://github.com/YOUR_USERNAME/GENEVA/releases/tag/v0.1.0
