pipeline {
    agent any

    options {
        skipStagesAfterUnstable()
        timestamps()
    }

    environment {
        VENV_DIR  = 'venv'
        CI_LOGS   = 'ci_logs'
        IMAGE_NAME = 'lab-2-app'
        SUDO      = 'sudo'
    }

    stages {
        stage('Checkout') {
            steps {
                echo "Cloning repository..."
                // Use declarative checkout (safer than custom git sh that contained $(pwd))
                checkout scm
            }
        }

        stage('Setup Virtual Environment') {
            steps {
                script {
                    echo "Creating virtual environment (if missing)..."
                    // Use Groovy interpolation for env vars, avoid $(...) shell expansions
                    sh "${env.SUDO} bash -lc 'if [ ! -d \"${env.VENV_DIR}\" ]; then python3 -m venv \"${env.VENV_DIR}\"; fi; \"${env.VENV_DIR}\"/bin/pip install --upgrade pip; \"${env.VENV_DIR}\"/bin/pip install -r requirements.txt'"
                }
            }
        }

        stage('Run Tests') {
            steps {
                script {
                    echo "Running pytest..."
                    sh "${env.SUDO} mkdir -p \"${env.CI_LOGS}\""
                    sh "${env.SUDO} bash -lc '\"${env.VENV_DIR}\"/bin/pytest -v test_app.py | tee \"${env.CI_LOGS}\"/pytest.log'"
                }
            }
        }

        stage('Static Code Analysis (Bandit)') {
            steps {
                script {
                    echo "Running Bandit..."
                    sh "${env.SUDO} mkdir -p \"${env.CI_LOGS}\""
                    sh "${env.SUDO} bash -lc '\"${env.VENV_DIR}\"/bin/bandit -r app -f json -o \"${env.CI_LOGS}\"/bandit-report.json'"
                }
            }
        }

        stage('Dependency Vulnerabilities (Safety)') {
            steps {
                script {
                    echo "Running Safety..."
                    sh "${env.SUDO} mkdir -p \"${env.CI_LOGS}\""
                    sh "${env.SUDO} bash -lc '\"${env.VENV_DIR}\"/bin/safety check --json > \"${env.CI_LOGS}\"/safety-report.json'"
                }
            }
        }

        stage('Build Docker Image') {
            steps {
                script {
                    echo "Building Docker image..."
                    sh "${env.SUDO} bash -lc 'docker-compose build'"
                }
            }
        }

        stage('Container Vulnerability Scan (Trivy)') {
            steps {
                script {
                    echo "Running Trivy..."
                    sh "${env.SUDO} mkdir -p \"${env.CI_LOGS}\""
                    sh "${env.SUDO} bash -lc 'trivy image --severity CRITICAL,HIGH --format json -o \"${env.CI_LOGS}\"/trivy-report.json ${env.IMAGE_NAME}:latest'"
                }
            }
        }

        stage('Deploy Application') {
            steps {
                script {
                    echo "Deploying Docker container..."
                    sh "${env.SUDO} bash -lc 'docker-compose up -d'"
                }
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
