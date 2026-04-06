# Setup Steps

## 1. Clone the repository

Use either HTTPS or SSH:

```bash
git clone https://github.com/OswinDsilva/E_Commerce_Application.git
# or
git clone git@github.com:OswinDsilva/E_Commerce_Application.git
```

Move into the project directory:

```bash
cd E_Commerce_Application
```

## 2. Create your environment file

Create a `.env` file and copy the contents from `.env.example` into it.

## 3. Set up MySQL

1. Install MySQL.
2. Create a MySQL user.
3. Create your database (for example, one for development and optionally one for testing).
4. Update the database values in `.env` with your MySQL credentials.

## 4. Apply the schema and database routines

Run the schema script from the project root:

```bash
mysql -u your_user -p your_database_name < sql/schema.sql
```

Then apply the Person 1 stored procedures:

```bash
mysql -u your_user -p your_database_name < sql/procedures.sql
```

And finally apply the trigger definitions:

```bash
mysql -u your_user -p your_database_name < sql/triggers.sql
```

Or paste the SQL files into your MySQL terminal in this order:

1. `sql/schema.sql`
2. `sql/procedures.sql`
3. `sql/triggers.sql`

If you are using both development and test databases, run the same command for each database name.

## 5. Create a virtual environment

From the project root, create and activate a Python virtual environment:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

## 6. Install dependencies

If you use pip:

```bash
pip install -r requirements.txt
```

If you use uv:

```bash
uv sync
```

The backend uses FastAPI and Uvicorn in addition to the MySQL dependencies already configured in the project.

## 7. Run the backend

From the project root, start the FastAPI app:

```bash
uvicorn backend.main:app --reload
```

The backend reads its database settings from `.env`, so make sure the database is configured before starting the server.

If you want to see the SQL executed by the backend while using the frontend or `curl`, add this to `.env` and restart Uvicorn:

```env
SQL_DEBUG=true
```

When enabled, the backend terminal will print `SQL DEBUG:` lines for each executed query.

## 8. Run the frontend

From the project root, move into the frontend directory and start the Vite development server:

```bash
cd frontend
npm run dev
```

The frontend and backend run separately during development.

## 9. Continue with project-specific work

Once setup is complete, continue with the remaining backend and frontend tasks.



