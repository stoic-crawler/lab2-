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
                echo "Setting up virtual environment..."
                sh """
                    #!/bin/bash
                    set -ex  // Exit on error, print commands

                    # --- THIS IS THE FIX ---
                    # Install the OS package required to create venvs
                    echo "Ensuring python3-venv is installed..."
                    sudo apt update -y
                    # Using the specific version from your error log
                    sudo apt install -y python3.12-venv
                    # ---------------------

                    # Clean old virtual environment to prevent caching issues
                    echo "Cleaning old virtual environment if it exists..."
                    rm -rf "${env.VENV_DIR}"

                    # Create a new, fresh virtual environment
                    echo "Creating new virtual environment..."
                    python3 -m venv "${env.VENV_DIR}"
                    
                    # Upgrade pip
                    echo "Upgrading pip..."
                    "${env.VENV_DIR}/bin/pip" install --upgrade pip
                    
                    # Install requirements
                    echo "Installing requirements..."
                    "${env.VENV_DIR}/bin/pip" install -r requirements.txt
                """
            }
        }

        stage('Run Tests') {
            steps {
                echo "Running pytest..."
                sh """
                    mkdir -p "${env.CI_LOGS}"
                    "${env.VENV_DIR}/bin/pytest" -v test_app.py | tee "${env.CI_LOGS}/pytest.log"
                """
            }
        }

        stage('Static Code Analysis (Bandit)') {
            steps {
                echo "Running Bandit..."
                sh """
                    mkdir -p "${env.CI_LOGS}"
                    "${env.VENV_DIR}/bin/bandit" -r app -f json -o "${env.CI_LOGS}/bandit-report.json"
                """
            }
        }

        stage('Dependency Vulnerabilities (Safety)') {
            steps {
                echo "Running Safety..."
                sh """
                    mkdir -p "${env.CI_LOGS}"
                    "${env.VENV_DIR}/bin/safety" check --json > "${env.CI_LOGS}/safety-report.json"
                """
            }
        }

        stage('Build Docker Image') {
            steps {
                echo "Building Docker image..."
                sh "sudo docker-compose build"
            }
        }

        stage('Container Vulnerability Scan (Trivy)') {
            steps {
                echo "Running Trivy..."
                sh """
                    mkdir -p "${env.CI_LOGS}"
                    sudo trivy image --severity CRITICAL,HIGH --format json -o "${env.CI_LOGS}/trivy-report.json" ${env.IMAGE_NAME}:latest
                """
            }
        }

        stage('Deploy Application') {
            steps {
                echo "Deploying Docker container..."
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
