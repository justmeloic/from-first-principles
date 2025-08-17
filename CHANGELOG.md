# Changelog

All notable changes to this project will be documented in this file. See [standard-version](https://github.com/conventional-changelog/standard-version) for commit guidelines.

## [0.10.0](https://github.com/justmeloic/from-first-principles/compare/v0.9.2...v0.10.0) (2025-08-17)


### ⚠ BREAKING CHANGES

* **api:** Agent endpoint now requires multipart/form-data format for all requests

- Add multipart/form-data support to agent endpoint
- Implement file validation with MIME type detection
- Add artifact storage integration with Google ADK
- Support multiple file uploads with unique naming
- Add python-magic dependency for file type detection
- Update schemas to handle optional files parameter
- Enhance agent service to process file attachments

### Features

* **api:** add artifact service and file upload support ([89d8bb2](https://github.com/justmeloic/from-first-principles/commit/89d8bb2127afbf3b7ab2acbe4e2669d6b0b094f1))
* **artifacts:** add comprehensive file processing system ([dc9fc30](https://github.com/justmeloic/from-first-principles/commit/dc9fc3077b500222ca1d7f64089ad5b9ee8247b3))
* **chat:** enhance input requirements and styling ([e914af5](https://github.com/justmeloic/from-first-principles/commit/e914af57f7a84d11e0801025d8406e843c1661d3))
* **frontend:** add file upload support to chat interface ([ef8f11e](https://github.com/justmeloic/from-first-principles/commit/ef8f11e6b4d27272d6fbabdfa9ec82331dc7b2e0))
* **ui:** convert new conversation button to circular design ([e2ad4b4](https://github.com/justmeloic/from-first-principles/commit/e2ad4b4f9096b291e1bcfae820ecd7a26ff31f34))
* version bump ([7af9d2b](https://github.com/justmeloic/from-first-principles/commit/7af9d2ba2e71cbbdd4eaee19d8ec38e535f1c800))
* version bump ([307f440](https://github.com/justmeloic/from-first-principles/commit/307f44067ab2b3cf958c0528c9b64b9bb0867e24))


### Bug Fixes

* remove unused search stats loading functionality ([03fcfa9](https://github.com/justmeloic/from-first-principles/commit/03fcfa98ed482fe5928b8e7a96cc2b91d3edc11a))
* **search:** add accurate timing measurement to search results ([f66fc75](https://github.com/justmeloic/from-first-principles/commit/f66fc759831eb6ebbda1d394332cbff92b070003))
