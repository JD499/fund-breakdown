# Fund Breakdown

Fund Breakdown is a web application that allows users to analyze their investment portfolios. It provides detailed insights into the composition of investment funds, including the underlying stocks that make up each fund.

## Repository Structure

The repository is divided into two main sections: `backend` and `frontend`.

### Backend

The backend is written in Python and is responsible for the core logic of the application. It includes the following main components:

- `app.py`: The main application file and the entry point for running the backend server.
- `constants.py`: Contains constant values used across the backend.
- `fund.py` and `fund_factory.py`: These files handle the creation and management of fund objects.
- `portfolio.py`: Handles the creation and management of portfolio objects.
- `request_cache.py`: Caches requests to improve performance.
- `run.py`: This file provides the functionality of app.py but within offline console input
- `scraper.py`: Scrapes data from external sources.
- `stock.py` and `stock_factory.py`: These files handle the creation and management of stock objects.

### Frontend

The frontend is written in TypeScript and React. It provides the user interface for the application. The main components include:

- `App.tsx`: The main application file.
- `AppBarComponent.tsx`, `DrawerComponent.tsx`, `HoldingsDisplay.tsx`, `MainContent.tsx`, `PortfolioForm.tsx`: These are the main React components used in the application.
- `constants.ts`: Contains constant values used across the frontend.
- `main.tsx`: The entry point for the frontend application.
- `Holdings.tsx`, `Portfolio.tsx`: These files represent different pages in the application.

## Getting Started

To get started with the project, clone the repository and install the dependencies for both the backend and frontend.

For the backend, navigate to the `backend` directory and install the necessary dependencies. Then, to start the backend server, run:

```
python app.py
```

For the frontend, navigate to the `frontend` directory and run:

```
npm install
```

Then, to start the frontend server in development mode, run:

```
npm run dev
```

To build the frontend for production, run:

```
npm run build
```

Now, you should be able to access the application at `localhost:4173`.
