# Kitchen Helper
[Kitchen helper](https://kitchenhelper.eognyanov.com/)

[Fron end repo]()
## Overview
Kitchen Helper is a project developed as part of the SoftUni Intern and Team Lead Academy initiative, led by Svetlin Nakov. The primary goal of this initiative is to provide freshly graduated SoftUni students with real-world development experience by pairing them with an experienced developer acting as a team leader.
## Project Description
The Kitchen Helper project is a tool designed to assist users in various kitchen-related tasks. It aims to streamline cooking processes, facilitate recipe management, and enhance the overall kitchen experience. Whether you're a novice in the kitchen or an experienced chef, Kitchen Helper is here to make your cooking journey more enjoyable and efficient.

## Features
- Recipe Management: Easily organize and manage your favorite recipes.
- Ingredient Tracking: Keep track of your pantry and shopping list for efficient meal planning.
- Cooking Timers: Set timers for different cooking stages to ensure perfectly cooked meals.
- User-Friendly Interface: Intuitive design for a seamless user experience.

## Getting Started
To get started with Kitchen Helper, follow these steps:

- Clone the repository to your local machine.
- Set up the required dependencies
  - create .env file with following structure
  ```
    POSTGRES_USER=''
    POSTGRES_PASSWORD=''
    RABBITMQ_USER=''
    RABBITMQ_PASSWORD=''
    CELERY_BROKER=pyamqp://
    CELERY_PORT=5672
    CELERY_BACKEND=rpc://
    ```

- Run the application locally using `docker-compose up`.

## Project structure

To structure the project following a vertical architecture, where each feature is organized into its own package, you can follow these guidelines:

### Project Layout

The project root directory should contain essential files like “README.md”, “requirements.txt” and the configuration “.env.*” files.
Common functionality such **configuration** and **logging** also should be on root level.

### Package Structure

Create a directory name “features” to hold all feature-related packages.

Each feature, such as “users”, “recipes”, “images” and etc should have it own sub package under  the “feature” directory.

### Feature Package Structure

Inside each feature package, organize your code into the following structure:

- “router”: Define API endpoints and request handling
- “models”: Define feature-specific data models.
- “operations”: Implement business logic for the feature
- “input_models”: Define input data validation and serialization
- “responses”: Define response data structures

### Testing

Create a separate directory for tests, with a similar structure to your source code.

For example, you can have “tests/features” mirroring the “features/” structure