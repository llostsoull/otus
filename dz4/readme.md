# Проект
- mvn package

# Docker
- docker build --platform linux/amd64 -t otus-dz2-docker-health-0.0.1 .
- docker tag user-service:0.0.1 itzz/user-service:0.0.1
- docker push itzz/user-service:0.0.1

# Ставим постгрес хелмом
- helm repo add bitnami https://charts.bitnami.com/bitnami
- helm install dev-pg bitnami/postgresql --set primary.persistence.existingClaim=pg-pvc,auth.postgresPassword=pgpass

# Секреты для postgres + для учетки сервиса
- kubectl apply -f k8s/secret.yaml

# Настройки БД сервиса
- kubectl apply -f k8s/migration/migration_configmap.yml

# Джоба для создание БД под сервис
- kubectl apply -f k8s/migration/migration-job.yml

# Cервис + ингрес
- kubectl apply -f k8s/configmap.yaml
- kubectl apply -f k8s/deployment.yaml
- kubectl apply -f k8s/service.yaml
- kubectl apply -f k8s/ingress.yaml

# В хостах прописываем arch.homework / Свайгер доступен по адресу:
https://arch.homework/swagger-ui/index.html

# Резултат
папка postman содержит коллекцию и скрины результатов
