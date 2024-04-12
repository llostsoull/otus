FROM bellsoft/liberica-openjdk-alpine:17
ARG JAR_FILE=target/user-service-0.0.2-SNAPSHOT.jar
WORKDIR /opt/app  
COPY ${JAR_FILE} app.jar  
ENTRYPOINT ["java","-jar","app.jar"]  