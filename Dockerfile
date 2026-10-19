
# Stage 1: Build the application
FROM eclipse-temurin:21-jdk-jammy AS build
WORKDIR /workspace

# Copy standard Maven wrapper/pom (assuming a standard Spring Boot setup)
COPY mvnw .
COPY .mvn .mvn
COPY pom.xml .
COPY src src
RUN ./mvnw clean package -DskipTests

# Stage 2: Create the secure runtime
FROM eclipse-temurin:21-jre-jammy
WORKDIR /app

# Create a non-root user and group
RUN addgroup --system spring && adduser --system --group spring

# Switch to the non-root user
USER spring:spring

# Copy the built jar from the first stage
COPY --from=build /workspace/target/*.jar app.jar

EXPOSE 8080
ENTRYPOINT ["java", "-jar", "app.jar"]
