pipeline {
  agent any

  environment {
    IMAGE_NAME = "abhishekram404/ecom-backend"
    IMAGE_TAG = "latest"
    CONTAINER_NAME = "ecom_backend"
    APP_PORT = "8000"
    DISCORD_WEBHOOK = credentials('discord-webhook-url')
  }

  stages {

    stage('Notify Start') {
      steps {
        sh """
        curl -H 'Content-Type: application/json' -X POST -d '{
          "content": "**⏱ Build Started**",
          "embeds": [
            {
              "title": "🚧 Pipeline Info",
              "color": 5814783,
              "fields": [
                { "name": "Job", "value": "${env.JOB_NAME}", "inline": true },
                { "name": "Build", "value": "#${env.BUILD_NUMBER}", "inline": true },
                { "name": "Branch", "value": "${env.GIT_BRANCH}" }
              ]
            }
          ]
        }' $DISCORD_WEBHOOK
        """
      }
    }

    stage('Checkout') {
      steps {
        checkout scm
      }
    }

    stage('Build Docker Image') {
      steps {
        sh '''
          echo "Building Docker image..."
          DOCKER_BUILDKIT=1 docker build -t $IMAGE_NAME:$IMAGE_TAG .
        '''
      }
    }

    stage('Push to DockerHub') {
      steps {
        withCredentials([
          usernamePassword(
            credentialsId: 'dockerhub',
            usernameVariable: 'DOCKER_USER',
            passwordVariable: 'DOCKER_PASS'
          )
        ]) {
          sh '''
            echo "$DOCKER_PASS" | docker login -u "$DOCKER_USER" --password-stdin
            docker push $IMAGE_NAME:$IMAGE_TAG
          '''
        }
      }
    }
  }

  post {
    success {
      sh """
      curl -H 'Content-Type: application/json' -X POST -d '{
        "content": "**✅ Build & Deploy Succeeded**",
        "embeds": [
          {
            "title": "🎉 Success",
            "color": 3066993,
            "fields": [
              { "name": "Job", "value": "${env.JOB_NAME}", "inline": true },
              { "name": "Build", "value": "#${env.BUILD_NUMBER}", "inline": true },
              { "name": "URL", "value": "${env.BUILD_URL}" }
            ]
          }
        ]
      }' $DISCORD_WEBHOOK
      """
    }

    failure {
      sh """
      curl -H 'Content-Type: application/json' -X POST -d '{
        "content": "**❌ Build Failed**",
        "embeds": [
          {
            "title": "🚨 Failure",
            "color": 15158332,
            "fields": [
              { "name": "Job", "value": "${env.JOB_NAME}", "inline": true },
              { "name": "Build", "value": "#${env.BUILD_NUMBER}", "inline": true },
              { "name": "URL", "value": "${env.BUILD_URL}" }
            ]
          }
        ]
      }' $DISCORD_WEBHOOK
      """
    }
  }
}