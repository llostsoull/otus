# Проект
- mvn package

# Docker
- docker build --platform linux/amd64 -t otus-dz2-docker-health-0.0.1 .
- docker tag user-service:0.0.1 itzz/user-service:0.0.1
- docker push itzz/user-service:0.0.1

# Ставим постгрес хелмом
- kubectl apply -f k8s/storage.yaml -f k8s/pv.yaml -f k8s/pvc.yaml
- helm repo add bitnami https://charts.bitnami.com/bitnami
- helm install dev-pg bitnami/postgresql --set primary.persistence.existingClaim=pg-pvc,auth.postgresPassword=pgpass

# Секреты для postgres + для учетки сервиса
- kubectl apply -f k8s/secret.yaml -f k8s/migration/migration_configmap.yml

# Джоба для создания БД под сервис
- kubectl apply -f k8s/migration/migration-job.yml

# Cервис + ингрес
- kubectl apply -f k8s/configmap.yaml -f k8s/deployment.yaml -f k8s/service.yaml -f k8s/ingress.yaml -f k8s/service-monitor.yaml

# В хостах прописываем arch.homework / Свайгер доступен по адресу:
https://arch.homework/swagger-ui/index.html

# Результат
- папка postman содержит коллекцию и скрины результатов
> newman run collection.json

- папка grafana содержит дашборды + скрины
