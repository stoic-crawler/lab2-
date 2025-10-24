pipeline {
    agent any

    environment {
        PYTHON = 'python3'
        IMAGE_NAME = 'flask_app'
        REPORT_DIR = 'reports'
        TRIVY_REPORT = "${REPORT_DIR}/trivy-report.txt"
        BANDIT_REPORT = "${REPORT_DIR}/bandit-report.txt"
        SAFETY_REPORT = "${REPORT_DIR}/safety-report.txt"
    }

    stages {
        stage('Checkout') {
            steps {
                echo 'Cloning repository...'
                checkout scm
            }
        }

        stage('Setup Python Environment') {
            steps {
                script {
                    echo 'Creating virtual environment...'
                    sh '''
                        ${PYTHON} -m venv venv
                        . venv/bin/activate
                        pip install --upgrade pip
                        pip install -r requirements.txt pytest bandit safety
                        mkdir -p ${REPORT_DIR}
                    '''
                }
            }
        }

        stage('Run Tests') {
            steps {
                script {
                    echo 'Running tests with pytest...'
                    def result = sh(script: '. venv/bin/activate && pytest --maxfail=1 --disable-warnings -q', returnStatus: true)
                    if (result != 0) {
                        error("Build stopped: pytest failed")
                    }
                }
            }
        }

        stage('Static Code Analysis (Bandit)') {
            steps {
                script {
                    echo 'Running Bandit scan...'
                    def result = sh(script: ". venv/bin/activate && bandit -r . -f txt -o ${BANDIT_REPORT}", returnStatus: true)
                    if (result != 0) {
                        echo "Bandit found issues. Report saved to ${BANDIT_REPORT}"
                        error("Build stopped: Bandit found security issues")
                    }
                }
            }
        }

        stage('Container Vulnerability Scan (Trivy)') {
            steps {
                script {
                    echo 'Building Docker image for scanning...'
                    sh 'docker-compose build'
                    echo 'Running Trivy scan...'
                    def result = sh(script: "trivy image ${IMAGE_NAME}:latest > ${TRIVY_REPORT} || true", returnStatus: true)

                    def criticalIssues = sh(script: "grep -c 'CRITICAL' ${TRIVY_REPORT} || true", returnStdout: true).trim()
                    def highIssues = sh(script: "grep -c 'HIGH' ${TRIVY_REPORT} || true", returnStdout: true).trim()

                    if (criticalIssues != '0' || highIssues != '0') {
                        echo "Trivy found ${criticalIssues} critical and ${highIssues} high vulnerabilities. Report saved to ${TRIVY_REPORT}"
                        error("Build stopped: Trivy found vulnerabilities")
                    } else {
                        echo "No critical or high vulnerabilities found by Trivy."
                    }
                }
            }
        }

        stage('Dependency Vulnerability Scan (Safety)') {
            steps {
                script {
                    echo 'Running Safety check...'
                    def result = sh(script: ". venv/bin/activate && safety check --full-report > ${SAFETY_REPORT} || true", returnStatus: true)

                    def issues = sh(script: "grep -c '>' ${SAFETY_REPORT} || true", returnStdout: true).trim()
                    if (issues != '0') {
                        echo "Safety found dependency issues. Report saved to ${SAFETY_REPORT}"
                        error("Build stopped: Safety found vulnerable dependencies")
                    } else {
                        echo "No dependency vulnerabilities found by Safety."
                    }
                }
            }
        }

        stage('Build Docker Image') {
            steps {
                echo 'Building Docker image for deployment...'
                sh 'docker-compose build'
            }
        }

        stage('Deploy Application') {
            steps {
                echo 'Deploying application container...'
                sh 'docker-compose up -d'
            }
        }
    }

    post {
        always {
            echo 'Cleaning workspace...'
            archiveArtifacts artifacts: 'reports/*.txt', onlyIfSuccessful: false
            cleanWs()
        }
    }
}

