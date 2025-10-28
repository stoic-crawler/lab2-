pipeline {
    agent any

    options {
        // skip later stages if the build becomes UNSTABLE
        skipStagesAfterUnstable()
        timestamps()
    }

    environment {
        VENV_DIR   = 'venv'
        CI_LOGS    = 'ci_logs'
        IMAGE_NAME = 'lab-2-app'
        // use -n so sudo will NOT prompt for a password (it will fail fast if not allowed)
        SUDO       = 'sudo -n'
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
                    // don't run the venv creation under sudo (creates root-owned venv and causes trouble)
                    // but show a short sudo availability debug line so we know whether sudo would block later.
                    timeout(time: 10, unit: 'MINUTES') {
                        sh """
                           echo "=== Debug: user and sudo availability ==="
                           id
                           ${env.SUDO} true >/dev/null 2>&1 && echo "sudo works (no password required)" || echo "sudo not available or requires password"
                        """

                        // create venv as the Jenkins runtime user (no sudo)
                        sh "/usr/bin/python3 -m venv ${env.VENV_DIR} || echo 'venv exists or creation failed'"

                        // upgrade pip and install deps (in-user venv)
                        sh "${env.VENV_DIR}/bin/pip install --upgrade pip"
                        sh "${env.VENV_DIR}/bin/pip install -r requirements.txt"
                    }
                }
            }
        }

        stage('Run Tests') {
            steps {
                script {
                    timeout(time: 10, unit: 'MINUTES') {
                        sh "mkdir -p ${env.CI_LOGS}"
                        // run pytest as the Jenkins runtime user (no sudo)
                        sh "${env.VENV_DIR}/bin/pytest -v test_app.py | tee ${env.CI_LOGS}/pytest.log"
                    }
                }
            }
        }

        stage('Static Code Analysis (Bandit)') {
            steps {
                script {
                    timeout(time: 5, unit: 'MINUTES') {
                        sh "mkdir -p ${env.CI_LOGS}"
                        sh "${env.VENV_DIR}/bin/bandit -r app -f json -o ${env.CI_LOGS}/bandit-report.json"
                    }
                }
            }
        }

        stage('Dependency Vulnerabilities (Safety)') {
            steps {
                script {
                    timeout(time: 5, unit: 'MINUTES') {
                        sh "mkdir -p ${env.CI_LOGS}"
                        sh "${env.VENV_DIR}/bin/safety check --json > ${env.CI_LOGS}/safety-report.json"
                    }
                }
            }
        }

        stage('Build Docker Image') {
            steps {
                script {
                    timeout(time: 15, unit: 'MINUTES') {
                        echo "Building Docker image (will use sudo -n so it won't prompt for a password)"
                        // docker-compose likely needs elevated privileges — use sudo -n so it fails fast if not allowed
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
                        // Trivy may require docker privileges if scanning images; use sudo -n to avoid prompts
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
    }

    post {
        always {
            echo "Archiving CI logs..."
            archiveArtifacts artifacts: "${env.CI_LOGS}/*.json, ${env.CI_LOGS}/*.log", allowEmptyArchive: true
            echo "Pipeline finished. Check archived logs for details."
        }
    }
}
