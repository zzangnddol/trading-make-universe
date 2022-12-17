DOCKER_IMAGE_NAME = 'trading/trading-make-universe'
DOCKER_CONTAINER_NAME = 'trading-make-universe'

// DOCKER_HOST_MOUNT_BASE = '/data/ybsong/docker/apim-portal-v2'

pipeline {
    agent any
    triggers {
        pollSCM('* * * * *')
    }
    stages {
        stage("Docker build") {
            steps {
                sh "docker build -t ${DOCKER_IMAGE_NAME} ."
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
