pipeline {
    agent any

    options {
        skipStagesAfterUnstable()
        timestamps()
    }

    environment {
        VENV_DIR   = 'venv'
        CI_LOGS    = 'ci_logs'
        IMAGE_NAME = 'lab-2-app'
        // REMOVED: SUDO environment variable. It's safer to be explicit.
    }

    stages {
        stage('Checkout') {
            steps {
                echo "Cloning repository..."
                checkout scm
            }
        }

        stage('Setup Virtual Environment') {
            steps {
                echo "Creating virtual environment (if missing)..."
                // This is the main fix:
                // 1. Removed 'sudo bash -lc' wrapper.
                // 2. Used a clean multiline sh step.
                // 3. No sudo is needed to create a venv in the workspace.
                sh """
                    #!/bin/bash
                    set -ex  // Exit on error, print commands

                    if [ ! -d "${env.VENV_DIR}" ]; then
                        python3 -m venv "${env.VENV_DIR}"
                    fi
                    
                    "${env.VENV_DIR}/bin/pip" install --upgrade pip
                    "${env.VENV_DIR}/bin/pip" install -r requirements.txt
                """
            }
        }

        stage('Run Tests') {
            steps {
                echo "Running pytest..."
                // No sudo needed to create a dir or run pytest in the workspace
                sh """
                    mkdir -p "${env.CI_LOGS}"
                    "${env.VENV_DIR}/bin/pytest" -v test_app.py | tee "${env.CI_LOGS}/pytest.log"
                """
            }
        }

        stage('Static Code Analysis (Bandit)') {
            steps {
                echo "Running Bandit..."
                // No sudo needed
                sh """
                    mkdir -p "${env.CI_LOGS}"
                    "${env.VENV_DIR}/bin/bandit" -r app -f json -o "${env.CI_LOGS}/bandit-report.json"
                """
            }
        }

        stage('Dependency Vulnerabilities (Safety)') {
            steps {
                echo "Running Safety..."
                // No sudo needed
                sh """
                    mkdir -p "${env.CI_LOGS}"
                    "${env.VENV_DIR}/bin/safety" check --json > "${env.CI_LOGS}/safety-report.json"
                """
            }
        }

        stage('Build Docker Image') {
            steps {
                echo "Building Docker image..."
                // Kept 'sudo' for Docker as it often needs it, but removed 'bash -lc'
                sh "sudo docker-compose build"
            }
        }

        stage('Container Vulnerability Scan (Trivy)') {
            steps {
                echo "Running Trivy..."
                // Kept 'sudo' for Trivy as requested, but removed 'bash -lc'
                sh """
                    mkdir -p "${env.CI_LOGS}"
                    sudo trivy image --severity CRITICAL,HIGH --format json -o "${env.CI_LOGS}/trivy-report.json" ${env.IMAGE_NAME}:latest
                """
            }
        }

        stage('Deploy Application') {
            steps {
                echo "Deploying Docker container..."
                // Kept 'sudo' for Docker, but removed 'bash -lc'
                sh "sudo docker-compose up -d"
            }
        }
    }

    post {
        always {
            echo "Archiving CI logs..."
            archiveArtifacts artifacts: "${env.CI_LOGS}/*.json, ${env.CI_LOGS}/*.log", allowEmptyArchive: true
            echo "Pipeline finished. Check archived logs for details."
        }
    }
}
