​## Service Monitoring Pro

Service Monitoring Pro is a web application designed to monitor the availability and performance of websites and servers. Users can register, log in, and add URLs to monitor, selecting specific intervals and monitoring types. The application checks the status of the specified services at the chosen intervals and notifies users via email if any service becomes unavailable. An alert dashboard provides a centralized view of all alerts.

## Features

- **User Authentication**: Secure user registration and login functionality.
- **Service Monitoring**:
  - **Website Monitoring**: Regular checks to ensure websites are accessible.
  - **Server Monitoring**: Verification that servers are operational.
  - **Combined Monitoring**: Simultaneous monitoring of both websites and servers.
- **Customizable Intervals**: Users can select monitoring intervals of 30 seconds, 1 minute, 2 minutes, or 5 minutes.
- **Alert Notifications**: Immediate email notifications when a monitored service becomes unavailable.
- **Alert Dashboard**: A comprehensive dashboard displaying all alerts for user review.

## Tech Stack

- **Backend**:
  - [Django](https://www.djangoproject.com/): Web framework for the backend logic.
  - [Celery](https://docs.celeryproject.org/en/stable/): Distributed task queue for handling periodic monitoring tasks.
  - [Redis](https://redis.io/): In-memory data structure store used as the message broker for Celery.
- **Networking**:
  - [ping3](https://pypi.org/project/ping3/): Library for performing ping operations to check server availability.
  - [Sockets](https://docs.python.org/3/library/socket.html): Used for port checking to verify server responsiveness.
- **Containerization**:
  - [Docker](https://www.docker.com/): Used to containerize the Redis service, ensuring compatibility across environments.

## Prerequisites

- **Python**: Ensure Python is installed on your system. You can download it from the [official website](https://www.python.org/).
- **Docker**: Required to run the Redis service, especially on Windows systems. Install Docker from the [Docker website](https://www.docker.com/get-started).

## Installation

1. **Clone the Repository**:

   ```bash
   git clone https://github.com/Husnain-Ali-24/servicemonitoringpro.git
   cd servicemonitoringpro
   ```

2. **Set Up a Virtual Environment**:

   It's recommended to use a virtual environment to manage dependencies.

   ```bash
   python -m venv env
   source env/bin/activate  # On Windows, use 'env\Scripts\activate'
   ```

3. **Install Dependencies**:

   Install the required Python packages using the provided `requirements.txt` file.

   ```bash
   pip install -r requirements.txt
   ```

4. **Configure Docker for Redis**:

   Since Windows does not natively support Redis, Docker is used to run the Redis service.

   - **Build and Run Redis Container**:

     Ensure Docker is running on your system. Navigate to the project directory and execute:

     ```bash
     docker-compose up -d
     ```

     This command uses the `docker-compose.yml` file to set up the Redis service.

5. **Apply Database Migrations**:

   Set up the database schema using Django migrations.

   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```

6. **Create a Superuser**:

   For accessing the Django admin interface, create a superuser account.

   ```bash
   python manage.py createsuperuser
   ```

7. **Start the Development Server**:

   Launch the Django development server.

   ```bash
   python manage.py runserver
   ```

8. **Start Celery Workers and Beat Scheduler**:

   Open two separate terminal windows to run the following commands:

   - **Celery Worker**:

     ```bash
     celery -A process_monitoring worker -l info -P eventlet
     ```

   - **Celery Beat Scheduler**:

     ```bash
     celery -A process_monitoring beat --scheduler django_celery_beat.schedulers:DatabaseScheduler --loglevel=info
     ```

   These commands initiate the Celery worker and the scheduler for periodic tasks.

## Usage

1. **Access the Application**:

   Open your web browser and navigate to `http://127.0.0.1:8000/`.

2. **Register or Log In**:

   - **New Users**: Click on the "Sign Up" link to create a new account.
   - **Existing Users**: Use your credentials to log in.

3. **Add a Service to Monitor**:

   - Navigate to the monitoring section.
   - Enter the URL of the website or server you wish to monitor.
   - Select the desired monitoring interval (30 seconds, 1 minute, 2 minutes, or 5 minutes).
   - Choose the type of monitoring: Website, Server, or Both.
   - Save your settings.

4. **View Alerts**:

   Access the alert dashboard to view any alerts generated for your monitored services.

## Docker Configuration

The application uses Docker to manage the Redis service, ensuring compatibility across different environments, especially on Windows systems where Redis is not natively supported.

- **Docker Compose**:

  The `docker-compose.yml` file defines the services required for the application. To start the services, use:

  ```bash
  docker-compose up -d
  ```

  This command sets up the Redis service in a Docker container.

## Contributing

We welcome contributions to enhance the functionality and reliability of Service Monitoring Pro. To contribute:

1. Fork the repository.
2. Create a new branch for your feature or bug fix.
3. Implement your changes.
4. Submit a pull request with a detailed description of your changes.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for more details.

## Acknowledgments

We extend our gratitude to the developers and maintainers of the open-source tools and libraries utilized in this project, including Django, Celery, Redis, Docker, ping3, and others. Their contributions have been invaluable in the development of Service Monitoring Pro.

---

*Note: This README provides a comprehensive overview of the Service Monitoring Pro application, including setup instructions, usage guidelines, and technical details.* 
