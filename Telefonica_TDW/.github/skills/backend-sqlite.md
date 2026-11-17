# Backend, Architecture & Data Persistence
- **Frameworks:** Python with FastAPI and Pydantic for strict data validation.
- **Architecture Pattern:** Strictly implement the MVC (Model-View-Controller) design pattern through directory structure and code organization.
  - **Models:** Use Pydantic schemas for validation and encapsulate all SQLite database operations/queries here.
  - **Controllers:** FastAPI route handlers and core business logic. Do not write direct database queries inside the routes.
  - **Views:** Streamlit frontend dashboard rendering. NEVER mix business logic or database queries inside the Streamlit UI code.
- **Database:** SQLite (local file, e.g., `prepago.db`) for data persistence during the demonstration.
- **Initialization:** Initialize the SQLite database and tables on startup if they do not exist.
- **Data Access:** Use parameterized queries or an ORM/query builder to interact with SQLite safely.