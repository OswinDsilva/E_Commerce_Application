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

## 3. Set up PostgreSQL

1. Install PostgreSQL.
2. Create a PostgreSQL user.
3. Create your database (for example, one for development and optionally one for testing).
4. Update the database values in `.env` with your PostgreSQL credentials.

## 4. Apply the schema

Run the schema script from the project root:

```bash
psql -U your_user -d your_database_name -f sql/schema.sql
```

Or paste the entire `sql/schema.sql` file into your PostgreSQL terminal.

If you are using both development and test databases, run the same command for each database name.

## 5. Install dependencies

If you use pip:

```bash
pip install -r requirements.txt
```

If you use uv:

```bash
uv sync
```

## 6. Continue with project-specific work

Once setup is complete, continue with the remaining backend and frontend tasks.



