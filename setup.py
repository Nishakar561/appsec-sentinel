#!/usr/bin/env python3
import os
import sys
import zipfile
import json
import shutil
import subprocess

STATE_FILE = ".setup_state.json"
TEMP_DIR = "temp"
EXTRACT_DIR = os.path.join(TEMP_DIR, "extracted")

# The strict security patches that MUST be injected into the user's pom.xml
SECURITY_DEPENDENCY_MANAGEMENT = """
    <!-- APPSEC SENTINEL: ENFORCED SECURE DEPENDENCIES -->
    <dependencyManagement>
        <dependencies>
            <dependency>
                <groupId>org.apache.tomcat.embed</groupId>
                <artifactId>tomcat-embed-core</artifactId>
                <version>11.0.25</version>
            </dependency>
            <dependency>
                <groupId>tools.jackson.core</groupId>
                <artifactId>jackson-core</artifactId>
                <version>3.2.3</version>
            </dependency>
            <dependency>
                <groupId>tools.jackson.core</groupId>
                <artifactId>jackson-databind</artifactId>
                <version>3.2.3</version>
            </dependency>
        </dependencies>
    </dependencyManagement>
"""

def load_state():
    if os.path.exists(STATE_FILE):
        with open(STATE_FILE, "r") as f:
            return json.load(f)
    return {}

def save_state(state):
    with open(STATE_FILE, "w") as f:
        json.dump(state, f)

def run_step(step_name, func):
    state = load_state()
    if state.get(step_name):
        print(f"⏭️  Skipping [{step_name}]: Already completed successfully.")
        return

    print(f"⏳ Running [{step_name}]...")
    func()

    state[step_name] = True
    save_state(state)

def find_zip():
    if not os.path.exists(TEMP_DIR):
        os.makedirs(TEMP_DIR)
        print("❌ Error: 'temp' directory created. Please place your Spring Initializr .zip file inside it and run again.")
        sys.exit(1)

    zips = [f for f in os.listdir(TEMP_DIR) if f.endswith('.zip')]
    if not zips:
        print("❌ Error: No .zip file found in the 'temp' directory.")
        sys.exit(1)
    return os.path.join(TEMP_DIR, zips[0])

def step_extract():
    zip_path = find_zip()
    if os.path.exists(EXTRACT_DIR):
        shutil.rmtree(EXTRACT_DIR)
    os.makedirs(EXTRACT_DIR)

    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        zip_ref.extractall(EXTRACT_DIR)
    print(f"✅ Extracted {zip_path}")

def step_replace_src():
    extracted_root = EXTRACT_DIR
    for root, dirs, files in os.walk(EXTRACT_DIR):
        if "pom.xml" in files:
            extracted_root = root
            break

    user_src = os.path.join(extracted_root, "src")
    if not os.path.exists(user_src):
        print("❌ Error: Valid src/ directory not found in the extracted zip.")
        sys.exit(1)

    if os.path.exists("src"):
        shutil.rmtree("src")

    shutil.copytree(user_src, "src")
    print("✅ Replaced application src/ directory.")

def step_inject_security_pom():
    extracted_root = EXTRACT_DIR
    for root, dirs, files in os.walk(EXTRACT_DIR):
        if "pom.xml" in files:
            extracted_root = root
            break

    user_pom = os.path.join(extracted_root, "pom.xml")

    with open(user_pom, "r") as f:
        pom_content = f.read()

    if "APPSEC SENTINEL" not in pom_content:
        pom_content = pom_content.replace("<dependencies>", SECURITY_DEPENDENCY_MANAGEMENT + "\n    <dependencies>", 1)

        with open("pom.xml", "w") as f:
            f.write(pom_content)
        print("✅ Injected AppSec Sentinel security dependencies into pom.xml.")
    else:
        print("✅ Security dependencies already present in pom.xml.")

def step_install_dependencies():
    mvn_cmd = "./mvnw" if os.name != 'nt' else "mvnw.cmd"

    if os.name != 'nt' and os.path.exists(mvn_cmd):
        os.chmod(mvn_cmd, 0o755)

    print("📦 Resolving and verifying Maven dependencies (this may take a minute)...")

    # We combine stdout and stderr to ensure we capture the error wherever Maven prints it
    result = subprocess.run([mvn_cmd, "clean", "compile"], capture_output=True, text=True)

    if result.returncode != 0:
        print("\n❌ Maven build failed. Analyzing error...\n")
        output = result.stdout + "\n" + result.stderr

        # 1. Catch Java Version Mismatch
        if "release version" in output and "not supported" in output or "invalid target release" in output:
            print("🔍 DIAGNOSTIC: Java Version Mismatch Detected")
            print("💡 WHY: Your Spring Initializr project requests a newer Java version than what your machine is currently running.")
            print("🔧 FIX: Open 'pom.xml', locate the <java.version> tag near the top, and change the number (e.g., from 21 or 27) to match your local Java version (e.g., 17).")

        # 2. Catch Missing Dependencies / Offline Errors
        elif "Could not resolve dependencies" in output:
            print("🔍 DIAGNOSTIC: Dependency Resolution Failure")
            print("💡 WHY: Maven cannot download the required packages. You may be offline, or a specific version does not exist in the Maven repository.")
            print("🔧 FIX: Check your internet connection and verify the package versions in your pom.xml.")

        # 3. Catch Framework Clashes (Tomcat/Spring)
        elif "does not exist" in output or "ClassNotFound" in output:
            print("🔍 DIAGNOSTIC: Framework Version Clash")
            print("💡 WHY: The Spring Boot version you generated is likely incompatible with the AppSec Sentinel Tomcat/Jackson security overrides.")
            print("🔧 FIX: Generate a compatible Spring Boot version, or adjust the Tomcat/Jackson dependency overrides in pom.xml.")

        # 4. Fallback for Unknown Errors
        else:
            print("🔍 DIAGNOSTIC: Uncategorized Build Error")
            print("Please review the raw Maven output below to determine the cause:")
            print("-" * 50)
            print(output)
            print("-" * 50)

        sys.exit(1)

    print("✅ Dependencies installed and build verified.")

def step_cleanup():
    if os.path.exists(TEMP_DIR):
        shutil.rmtree(TEMP_DIR)
    if os.path.exists(STATE_FILE):
        os.remove(STATE_FILE)
    print("✅ Cleaned up temporary files and state trackers.")

if __name__ == "__main__":
    print("🛡️  Initializing AppSec Sentinel Workspace Setup...\n")

    run_step("Extracting Zip", step_extract)
    run_step("Replacing Source Code", step_replace_src)
    run_step("Injecting Security Governance", step_inject_security_pom)
    run_step("Verifying Build", step_install_dependencies)
    run_step("Final Cleanup", step_cleanup)

    print("\n🎉 Setup Complete! Your Spring Boot application is securely integrated with the DevSecOps wrapper.")
    print("   Run 'git add .' and 'git commit' to push your secure baseline.")
