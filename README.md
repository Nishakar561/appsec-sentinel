# Secure Java Spring Boot Wrapper (AppSec Sentinel)

This is a pre-hardened DevSecOps "Golden Path" template. It provides a baseline architecture with a non-root Dockerfile, patched framework dependencies, and a strict CI/CD pipeline enforcing SAST, Container Scanning, SBOM generation, and Secret Scanning.

## Quick Start & Setup

### 1. Clone & Secure Your Local Environment

Clone this repository and immediately activate the local pre-commit security wrapper. This prevents accidental hardcoded secrets from ever reaching Git history.

`git clone <your-repository-url>`
`cd <your-repository-folder>`
`git config core.hooksPath .githooks`

### 2. Integrate Spring Initializr (The Overlay Method)

If you are generating a new project from `start.spring.io`, follow these steps to merge it securely without breaking the DevSecOps guardrails:

1. **Download & Extract:** Generate your project ZIP from Spring Initializr and extract it.
2. **Overlay the Source:** Delete the default `src/` folder in this repository and replace it entirely with the `src/` folder from your extracted Initializr project.
3. **Merge Dependencies Securely:** **DO NOT** overwrite the `pom.xml`. Open your Initializr `pom.xml` and copy only your new `<dependency>` blocks (e.g., PostgreSQL, Spring Data JPA) into the `pom.xml` of this repository. This ensures the strict Tomcat, Jackson, and Spring Boot framework security patches remain intact.

### 3. Build & Deploy

Once your code and dependencies are merged, commit and push. The GitHub Actions pipeline will automatically trigger to:

- Scan for secrets (**Gitleaks**)
- Perform Static Application Security Testing (**Semgrep**)
- Build the container and scan layers for OS vulnerabilities (**Trivy**)
- Generate a cryptographic Software Bill of Materials (**Syft**)
