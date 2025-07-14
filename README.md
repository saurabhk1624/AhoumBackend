## How to Run the Project

1. **Install Docker**  
    Download and install Docker from [https://www.docker.com/get-started](https://www.docker.com/get-started).

2. **Start Docker**  
    Make sure Docker is running on your system.

3. **Build the Docker Containers**  
    ```bash
    docker compose build
    ```

4. **Start the Containers in Detached Mode**  
    ```bash
    docker compose up -d
    ```

5. **Access the Running Container**  
    ```bash
    docker exec -it ahoum sh
    ```

6. **Start the Application Services**  
    Inside the container, run:
    ```bash
    python app.py & python crm_service.py & wait
    ```

7. **Access the Application**  
    Once the services are running, access the application via the provided URL (check your `docker-compose.yml` for port details).