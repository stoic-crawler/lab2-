pipeline {
    agent any

    options {
        // If any stage marks the build UNSTABLE, skip subsequent stages.
        // Remove this if you want to continue through unstable stages.
        skipStagesAfterUnstable()
        // show timestamps in console log
        timestamps()
    }

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
                    echo "Creating virtual environment (if missing)..."
                    sh """
                        if [ ! -d "${VENV_DIR}" ]; then
                            python3 -m venv ${VENV_DIR}
                        fi
                        ${VENV_DIR}/bin/pip install --upgrade pip
                        ${VENV_DIR}/bin/pip install -r requirements.txt
                    """
                }
            }
        }

        stage('Run Tests') {
            steps {
                script {
                    echo "Running pytest..."
                    sh "mkdir -p ${CI_LOGS}"
                    // This will fail the stage if pytest exits non-zero
                    sh "${VENV_DIR}/bin/pytest -v test_app.py | tee ${CI_LOGS}/pytest.log"
                }
            }
        }

        stage('Static Code Analysis (Bandit)') {
            steps {
                script {
                    echo "Running Bandit..."
                    sh "mkdir -p ${CI_LOGS}"
                    // Remove '|| true' so pipeline fails if Bandit returns non-zero.
                    sh "${VENV_DIR}/bin/bandit -r app -f json -o ${CI_LOGS}/bandit-report.json"
                }
            }
        }

        stage('Dependency Vulnerabilities (Safety)') {
            steps {
                script {
                    echo "Running Safety..."
                    sh "mkdir -p ${CI_LOGS}"
                    // Fail pipeline if safety finds vulnerabilities (non-zero exit)
                    sh "${VENV_DIR}/bin/safety check --json > ${CI_LOGS}/safety-report.json"
                }
            }
        }

        stage('Build Docker Image') {
            steps {
                script {
                    echo "Building Docker image..."
                    // Fail pipeline if docker build fails
                    sh "docker-compose build"
                }
            }
        }

        stage('Container Vulnerability Scan (Trivy)') {
            steps {
                script {
                    echo "Running Trivy..."
                    sh "mkdir -p ${CI_LOGS}"
                    // Fail pipeline if Trivy exits non-zero (i.e. vulnerabilities of requested severities found)
                    sh "trivy image --severity CRITICAL,HIGH --format json -o ${CI_LOGS}/trivy-report.json ${IMAGE_NAME}:latest"
                }
            }
        }

        stage('Deploy Application') {
            steps {
                script {
                    echo "Deploying Docker container..."
                    // Fail pipeline if docker-compose up fails
                    sh "docker-compose up -d"
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
