pipeline {
    agent any
    environment {
        IMAGE_NAME = 'flask_app'
        LOG_DIR = 'ci_logs'
    }
    stages {
        stage('Checkout') {
            steps {
                echo 'Cloning repository...'
                checkout scm
            }
        }

        stage('Setup Virtual Environment') {
            steps {
                script {
                    echo 'Creating virtual environment...'
                    sh 'python3 -m venv venv'
                    echo 'Installing dependencies...'
                    sh 'venv/bin/pip install --upgrade pip'
                    sh 'venv/bin/pip install -r requirements.txt'
                }
            }
        }

        stage('Run Tests (pytest)') {
            steps {
                script {
                    echo 'Running pytest...'
                    sh """
                        mkdir -p ${LOG_DIR}
                        venv/bin/pytest -v test_app.py | tee ${LOG_DIR}/pytest.log
                    """
                }
            }
        }

        stage('Static Code Analysis (Bandit)') {
            steps {
                script {
                    echo 'Running Bandit...'
                    sh """
                        mkdir -p ${LOG_DIR}
                        venv/bin/bandit -r app -f json -o ${LOG_DIR}/bandit-report.json || true
                    """
                }
            }
        }

        stage('Dependency Vulnerability Scan (Safety)') {
            steps {
                script {
                    echo 'Running Safety...'
                    sh """
                        mkdir -p ${LOG_DIR}
                        venv/bin/safety check --json > ${LOG_DIR}/safety-report.json || true
                    """
                }
            }
        }

        stage('Container Vulnerability Scan (Trivy)') {
            steps {
                script {
                    echo 'Building Docker image...'
                    sh 'docker-compose build'
                    echo 'Running Trivy scan...'
                    sh """
                        mkdir -p ${LOG_DIR}
                        trivy image --format json --output ${LOG_DIR}/trivy-report.json ${IMAGE_NAME}:latest || true
                    """
                }
            }
        }

        stage('Build Docker Image') {
            steps {
                echo 'Building Docker image...'
                sh 'docker-compose build'
            }
        }

        stage('Deploy Application') {
            steps {
                echo 'Deploying application...'
                sh 'docker-compose up -d'
            }
        }
    }

    post {
        always {
            echo 'Pipeline finished. Logs saved in ci_logs/'
            archiveArtifacts artifacts: 'ci_logs/**', allowEmptyArchive: true
        }
    }
}

