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
        SUDO       = 'sudo -n' // fail fast if sudo would prompt
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
                    timeout(time: 12, unit: 'MINUTES') {
                        // debug: show which user / python / files exist
                        sh """
                            echo "=== Debug: user / python info ==="
                            id
                            which python3 || true
                            python3 --version || true
                            echo "PWD: $(pwd)"
                        """

                        // create venv (do not use sudo)
                        sh """
                            echo "=== Create venv if missing ==="
                            /usr/bin/python3 -m venv "${env.VENV_DIR}" || { echo "venv creation failed or already exists"; }
                            echo "=== venv contents after creation ==="
                            ls -la "${env.VENV_DIR}" || true
                        """

                        // Try ensurepip (some OSes need it), then upgrade pip via the venv Python
                        sh """
                            echo "=== Ensure pip inside venv (if supported) ==="
                            if [ -x "${env.VENV_DIR}/bin/python" ]; then
                                "${env.VENV_DIR}/bin/python" -m ensurepip --upgrade 2>/dev/null || echo "ensurepip not available or failed"
                                "${env.VENV_DIR}/bin/python" -m pip install --upgrade pip setuptools wheel || echo "pip upgrade failed (will try to proceed)"
                                echo "=== venv/bin contents ==="
                                ls -la "${env.VENV_DIR}/bin" || true
                            else
                                echo "ERROR: ${env.VENV_DIR}/bin/python not found"
                                exit 2
                            fi
                        """

                        // Install requirements via the venv Python's -m pip
                        sh """
                            echo "=== Installing requirements via venv python -m pip ==="
                            "${env.VENV_DIR}/bin/python" -m pip install --no-cache-dir -r requirements.txt
                        """
                    } // timeout
                } // script
            } // steps
        } // stage

        stage('Run Tests') {
            steps {
                script {
                    timeout(time: 10, unit: 'MINUTES') {
                        sh "mkdir -p ${env.CI_LOGS}"
                        sh "${env.VENV_DIR}/bin/python -m pytest -v test_app.py | tee ${env.CI_LOGS}/pytest.log"
                    }
                }
            }
        }

        stage('Static Code Analysis (Bandit)') {
            steps {
                script {
                    timeout(time: 5, unit: 'MINUTES') {
                        sh "mkdir -p ${env.CI_LOGS}"
                        sh "${env.VENV_DIR}/bin/python -m bandit -r app -f json -o ${env.CI_LOGS}/bandit-report.json"
                    }
                }
            }
        }

        stage('Dependency Vulnerabilities (Safety)') {
            steps {
                script {
                    timeout(time: 5, unit: 'MINUTES') {
                        sh "mkdir -p ${env.CI_LOGS}"
                        sh "${env.VENV_DIR}/bin/python -m safety check --json > ${env.CI_LOGS}/safety-report.json"
                    }
                }
            }
        }

        stage('Build Docker Image') {
            steps {
                script {
                    timeout(time: 20, unit: 'MINUTES') {
                        echo "Building Docker image (sudo -n so it won't prompt)"
                        sh "${env.SUDO} bash -lc 'docker-compose build'"
                    }
                }
            }
        }

        stage('Container Vulnerability Scan (Trivy)') {
            steps {
                script {
                    timeout(time: 10, unit: 'MINUTES') {
                        sh "mkdir -p ${env.CI_LOGS}"
                        sh "${env.SUDO} bash -lc 'trivy image --severity CRITICAL,HIGH --format json -o ${env.CI_LOGS}/trivy-report.json ${env.IMAGE_NAME}:latest'"
                    }
                }
            }
        }

        stage('Deploy Application') {
            steps {
                script {
                    timeout(time: 10, unit: 'MINUTES') {
                        echo "Deploying Docker container (uses sudo -n)"
                        sh "${env.SUDO} bash -lc 'docker-compose up -d'"
                    }
                }
            }
        }
    } // stages

    post {
        always {
            echo "Archiving CI logs..."
            archiveArtifacts artifacts: "${env.CI_LOGS}/*.json, ${env.CI_LOGS}/*.log", allowEmptyArchive: true
            echo "Pipeline finished."
        }
    }
}
