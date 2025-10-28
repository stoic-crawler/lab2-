pipeline {
    agent any

    options {
        skipStagesAfterUnstable()
        timestamps()
    }

    environment {
        VENV_DIR = 'venv'
        CI_LOGS = 'ci_logs'
        IMAGE_NAME = 'lab-2-app'
        SUDO = 'sudo'
    }

    stages {
        stage('Checkout') {
            steps {
                echo "Cloning repository..."
                sh "${SUDO} bash -lc 'git rev-parse --is-inside-work-tree || true; git config --global --add safe.directory $(pwd); git status --porcelain || true; git rev-parse --abbrev-ref HEAD || true'"
                // fallback: use checkout scm if preferred
                checkout scm
            }
        }

        stage('Setup Virtual Environment') {
            steps {
                script {
                    echo "Creating virtual environment (if missing)..."
                    sh """
                        ${SUDO} bash -lc '
                            if [ ! -d "${VENV_DIR}" ]; then
                                python3 -m venv ${VENV_DIR}
                                chown -R $(whoami):$(whoami) ${VENV_DIR} || true
                            fi
                            ${VENV_DIR}/bin/pip install --upgrade pip
                            ${VENV_DIR}/bin/pip install -r requirements.txt
                        '
                    """
                }
            }
        }

        stage('Run Tests') {
            steps {
                script {
                    echo "Running pytest..."
                    sh "${SUDO} mkdir -p ${CI_LOGS}"
                    // run entire pipeline under sudo so tee and pytest are run as root
                    sh """${SUDO} bash -lc '${VENV_DIR}/bin/pytest -v test_app.py | tee ${CI_LOGS}/pytest.log'"""
                }
            }
        }

        stage('Static Code Analysis (Bandit)') {
            steps {
                script {
                    echo "Running Bandit..."
                    sh "${SUDO} mkdir -p ${CI_LOGS}"
                    sh "${SUDO} bash -lc '${VENV_DIR}/bin/bandit -r app -f json -o ${CI_LOGS}/bandit-report.json'"
                }
            }
        }

        stage('Dependency Vulnerabilities (Safety)') {
            steps {
                script {
                    echo "Running Safety..."
                    sh "${SUDO} mkdir -p ${CI_LOGS}"
                    sh "${SUDO} bash -lc '${VENV_DIR}/bin/safety check --json > ${CI_LOGS}/safety-report.json'"
                }
            }
        }

        stage('Build Docker Image') {
            steps {
                script {
                    echo "Building Docker image..."
                    // uses sudo to invoke docker-compose
                    sh "${SUDO} bash -lc 'docker-compose build'"
                }
            }
        }

        stage('Container Vulnerability Scan (Trivy)') {
            steps {
                script {
                    echo "Running Trivy..."
                    sh "${SUDO} mkdir -p ${CI_LOGS}"
                    sh "${SUDO} bash -lc 'trivy image --severity CRITICAL,HIGH --format json -o ${CI_LOGS}/trivy-report.json ${IMAGE_NAME}:latest'"
                }
            }
        }

        stage('Deploy Application') {
            steps {
                script {
                    echo "Deploying Docker container..."
                    sh "${SUDO} bash -lc 'docker-compose up -d'"
                }
            }
        }
    }

    post {
        always {
            echo "Archiving CI logs..."
            // archiveArtifacts runs on the Jenkins master and typically does not require sudo,
            // but we leave it as-is (it doesn't run via sh)
            archiveArtifacts artifacts: "${CI_LOGS}/*.json, ${CI_LOGS}/*.log", allowEmptyArchive: true
            echo "Pipeline finished. Check archived logs for details."
        }
    }
}
