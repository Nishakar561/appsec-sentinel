# Secure Java Spring Boot Wrapper (AppSec Sentinel)

This is a pre-hardened DevSecOps "Golden Path" template. It provides a baseline architecture with a non-root Dockerfile, patched framework dependencies, and a strict CI/CD pipeline enforcing SAST, Container Scanning, SBOM generation, and Secret Scanning.

## Quick Start & Setup

### 1. Clone & Secure Your Local Environment

Clone this repository and immediately activate the local pre-commit security wrapper. This prevents accidental hardcoded secrets from ever reaching Git history.

```bash
git clone [https://github.com/Nishakar561/appsec-sentinel](https://github.com/Nishakar561/appsec-sentinel)
cd appsec-sentinel
git config core.hooksPath .githooks
```

### 2. Integrate Spring Initializr (Automated Setup)

If you are generating a new project from start.spring.io, use the included Python script to securely merge your codebase without breaking the DevSecOps guardrails.

Download: Generate your project ZIP from Spring Initializr.

Prepare: Move your downloaded .zip file into the existing temp/ folder located in the root of this repository.

Execute: Run the setup script. It will extract your files, overlay your src/ directory, securely inject strict Tomcat and Jackson vulnerability patches into your pom.xml, and verify the integration by running a Maven clean compile.

```bash
python3 setup.py
```

Cleanup: Once the setup has successfully run the .mvnw clean compile command and verified the build, delete the temp/ folder, the .setup_state.json file, and the setup.py script itself.

## 3. Build & Deploy

Once the script finishes and cleans up the temporary files, commit and push. The GitHub Actions pipeline will automatically trigger to:

- Scan for secrets (Gitleaks)
- Perform Static Application Security Testing (Semgrep)
- Build the container and scan layers for OS vulnerabilities (Trivy)
- Generate a cryptographic Software Bill of Materials (Syft)
