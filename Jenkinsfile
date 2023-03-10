DOCKER_IMAGE_NAME = 'trading/trading-make-universe'
DOCKER_CONTAINER_NAME = 'trading-make-universe'

// DOCKER_HOST_MOUNT_BASE = '/data/ybsong/docker/apim-portal-v2'

pipeline {
    agent any
    triggers {
        pollSCM('* * * * *')
    }
    environment {
        NEXUS_LOGIN = credentials('nexus-login')
    }
    stages {
        stage("Docker build") {
            steps {
                echo "Nexus Login User: ${NEXUS_LOGIN_USR}"
                sh "docker build -t ${DOCKER_IMAGE_NAME} \
                    --build-arg NEXUS_LOGIN_USR=\"${NEXUS_LOGIN_USR}\" \
                    --build-arg NEXUS_LOGIN_PSW=\"${NEXUS_LOGIN_PSW}\" \
                    ."
            }
        }
        stage("Docker container start") {
            steps {
                catchError(buildResult: 'SUCCESS') {
                    sh "docker ps -q --filter name=${DOCKER_CONTAINER_NAME} | grep -q . \
                        && docker stop ${DOCKER_CONTAINER_NAME} \
                        && docker rm ${DOCKER_CONTAINER_NAME}"
                }
                sh "docker run -d \
                    --name ${DOCKER_CONTAINER_NAME} \
                    -e TZ=Asia/Seoul \
                    --restart=always \
                    ${DOCKER_IMAGE_NAME}"
            }
        }
        stage("Finish") {
            steps {
                catchError(buildResult: 'SUCCESS') {
                    sh 'docker images -qf dangling=true | xargs -I{} docker rmi {}'
                }
            }
        }
    }
}
