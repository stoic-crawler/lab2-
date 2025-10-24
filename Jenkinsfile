pipeline {
    agent any

    environment {
        VENV_DIR = 'venv'
        CI_LOGS = 'ci_logs'
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
                script {
                    echo "Creating virtual environment..."
                    sh "python3 -m venv ${VENV_DIR}"
                    echo "Upgrading pip and installing dependencies..."
                    sh "${VENV_DIR}/bin/pip install --upgrade pip"
                    sh "${VENV_DIR}/bin/pip install -r requirements.txt"
                }
            }
        }

        stage('Run Tests') {
            steps {
                script {
                    echo "Running pytest..."
                    sh "mkdir -p ${CI_LOGS}"
                    sh "${VENV_DIR}/bin/pytest -v test_app.py | tee ${CI_LOGS}/pytest.log"
                }
            }
        }

        stage('Static Code Analysis (Bandit)') {
            steps {
                script {
                    echo "Running Bandit..."
                    sh "mkdir -p ${CI_LOGS}"
                    // Run Bandit, save JSON output
                    sh "${VENV_DIR}/bin/bandit -r app -f json -o ${CI_LOGS}/bandit-report.json || true"
                }
            }
        }

        stage('Dependency Vulnerabilities (Safety)') {
            steps {
                script {
                    echo "Running Safety..."
                    sh "mkdir -p ${CI_LOGS}"
                    sh "${VENV_DIR}/bin/safety check --json > ${CI_LOGS}/safety-report.json || true"
                }
            }
        }

        stage('Build Docker Image') {
            steps {
                script {
                    echo "Building Docker image..."
                    sh "docker-compose build || true"
                }
            }
        }

        stage('Container Vulnerability Scan (Trivy)') {
            steps {
                script {
                    echo "Running Trivy..."
                    sh "mkdir -p ${CI_LOGS}"
                    // Only scan the image, don't fail the pipeline on low/medium
                    sh "trivy image --severity CRITICAL,HIGH --format json -o ${CI_LOGS}/trivy-report.json ${IMAGE_NAME}:latest || true"
                }
            }
        }

        stage('Deploy Application') {
            steps {
                script {
                    echo "Deploying Docker container..."
                    sh "docker-compose up -d || true"
                }
            }
        }
    }

    post {
        always {
            echo "Archiving CI logs..."
            archiveArtifacts artifacts: "${CI_LOGS}/*.json, ${CI_LOGS}/*.log", allowEmptyArchive: true
            echo "Pipeline finished. Check archived logs for details."
        }
    }
}

