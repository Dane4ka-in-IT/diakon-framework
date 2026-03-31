FROM eclipse-temurin:17-jre-alpine
WORKDIR /app
COPY NoCodePlatform/target/NoCodePlatform-0.0.1-SNAPSHOT.jar app.jar
EXPOSE 1000
ENTRYPOINT ["java", "-jar", "app.jar"]
