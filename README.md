# Faceit Clone Backend

## Overview

This project is a backend clone of the popular gaming platform Faceit. It provides a high-performance REST API along with real-time communication features to support competitive gaming sessions, player matchmaking, and related functionalities.

## Technologies

- **FastAPI**  
  A high-performance web framework for building RESTful APIs. It simplifies endpoint creation and supports asynchronous programming, which is essential for handling concurrent requests.

- **MongoDB**  
  Used for storing lobby and match information, providing flexible and scalable NoSQL data storage.

- **Redis**  
  Employed for caching and storing user information, enhancing performance and ensuring fast data retrieval.

- **asyncpg**  
  An asynchronous PostgreSQL client that enables efficient, non-blocking database operations.

- **Websockets**  
  Provides bidirectional, real-time communication between the client and server, vital for live updates and notifications.

## Installation & Setup

1. **Clone the Repository:**

   ```bash
   git clone https://github.com/starzkeeper/p2play.git
   cd p2play
   ```

2. **Running the Application**

Build and run the application using Docker Compose:  

   ```bash
   docker compose up --build
   ```

3.	**Apply Database Migrations:**
Run Alembic to apply the latest migrations:

    ```bash
    alembic upgrade head
    ```
