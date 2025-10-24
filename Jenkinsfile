pipeline {
    agent any

    environment {
        PYTHON_IMAGE = 'python:3.13-slim'
        IMAGE_NAME = 'flask_app'
        VENV_DIR = 'venv'
        LOG_DIR = 'ci_logs'
    }

    options {
        // Keep build logs for troubleshooting
        timestamps()
        ansiColor('xterm')
        buildDiscarder(logRotator(numToKeepStr: '10'))
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
                    echo "Installing dependencies..."
                    sh "${VENV_DIR}/bin/pip install --upgrade pip"
                    sh "${VENV_DIR}/bin/pip install -r requirements.txt"
                }
            }
        }

        stage('Run Tests') {
            steps {
                script {
                    echo "Running pytest..."
                    sh """
                        mkdir -p ${LOG_DIR}
                        ${VENV_DIR}/bin/pytest -v test_app.py --junitxml=${LOG_DIR}/pytest-results.xml || (echo 'Pytest failed, check logs.' && exit 1)
                    """
                }
            }
        }

        stage('Static Code Analysis (Bandit)') {
            steps {
                script {
                    echo "Running Bandit..."
                    sh """
                        mkdir -p ${LOG_DIR}
                        ${VENV_DIR}/bin/bandit -r app -f json -o ${LOG_DIR}/bandit-report.json || (echo 'Bandit found issues.' && exit 1)
                    """
                }
            }
        }

        stage('Container Build & Vulnerability Scan (Trivy)') {
            steps {
                script {
                    echo "Building Docker image..."
                    sh "docker-compose build --no-cache"
                    echo "Running Trivy scan..."
                    sh """
                        mkdir -p ${LOG_DIR}
                        trivy image ${IMAGE_NAME}:latest --format json --output ${LOG_DIR}/trivy-report.json || (echo 'Trivy found vulnerabilities.' && exit 1)
                    """
                }
            }
        }

        stage('Dependency Vulnerability Check (Safety)') {
            steps {
                script {
                    echo "Checking Python dependencies with Safety..."
                    sh """
                        mkdir -p ${LOG_DIR}
                        ${VENV_DIR}/bin/safety check --json > ${LOG_DIR}/safety-report.json || (echo 'Safety found vulnerabilities.' && exit 1)
                    """
                }
            }
        }

        stage('Deploy Application') {
            steps {
                script {
                    echo "Deploying Flask application via Docker Compose..."
                    sh "docker-compose up -d"
                }
            }
        }

    }

    post {
        always {
            echo "Cleaning workspace..."
            cleanWs()
            archiveArtifacts artifacts: "${LOG_DIR}/*", allowEmptyArchive: true
        }
        failure {
            echo "Build failed. Check logs for details."
        }
        success {
            echo "Build succeeded."
        }
    }
}

