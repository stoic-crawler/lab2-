pipeline {
    agent any

    environment {
        VENV_DIR = 'venv'
        LOG_DIR = 'ci_logs'
        IMAGE_NAME = 'flask_app'
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
                        ${VENV_DIR}/bin/pytest -v test_app.py | tee ${LOG_DIR}/pytest.log
                        if [ \$? -ne 0 ]; then
                            echo 'Pytest failed, see logs.'
                            exit 1
                        fi
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
                        ${VENV_DIR}/bin/bandit -r app -f json -o ${LOG_DIR}/bandit-report.json
                        if [ \$? -ne 0 ]; then
                            echo 'Bandit found issues.'
                            exit 1
                        fi
                    """
                }
            }
        }

        stage('Build Docker Image') {
            steps {
                script {
                    echo "Building Docker image..."
                    sh "docker-compose build --no-cache"
                }
            }
        }

        stage('Deploy Application') {
            steps {
                script {
                    echo "Deploying Flask application..."
                    sh "docker-compose up -d"
                }
            }
        }

    }

    post {
        always {
            echo "Cleaning workspace and archiving logs..."
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

