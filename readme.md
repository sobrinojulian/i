# DB2 FastAPI

Minimal FastAPI app that connects to a DB2 database on IBM i (AS400) and returns table data as JSON.

## Prerequisites

The `pyodbc` Python package requires an **ODBC driver manager** and the **IBM i Access ODBC Driver**.

### Install the ODBC driver manager

#### Ubuntu / Debian
```bash
sudo apt-get install unixodbc unixodbc-dev
```

#### RHEL / CentOS / Fedora
```bash
sudo dnf install unixODBC unixODBC-devel
```

#### Arch Linux
```bash
sudo pacman -S --needed unixodbc
```

#### macOS
```bash
brew install unixodbc
```

### Install the IBM i Access ODBC Driver

#### Ubuntu / Debian
```bash
# Add IBM repository
wget https://public.dhe.ibm.com/ibmi/products/accessclient/prereq/ibm-iaccess-apt.list -O /etc/apt/sources.list.d/ibm-iaccess.list
sudo apt-get update
sudo apt-get install ibm-iaccess
```

#### RHEL / CentOS / Fedora
```bash
# Add IBM repository
sudo wget https://public.dhe.ibm.com/ibmi/products/accessclient/prereq/ibm-iaccess-yum.repo -O /etc/yum.repos.d/ibm-iaccess.repo
sudo dnf install ibm-iaccess
```

#### Arch Linux (AUR)
```bash
yay -S ibm-iaccess
```

After installing, register the driver in `/etc/odbcinst.ini`:
```bash
echo -e '[IBM i Access ODBC Driver]\nDriver=/opt/ibm/iaccess/lib64/libcwbodbc.so\nSetup=/opt/ibm/iaccess/lib64/libcwbodbcs.so' | sudo tee /etc/odbcinst.ini
```

Verify the driver is registered:
```bash
odbcinst -q -d
```
You should see `IBM i Access ODBC Driver` in the output.

## IBM i Notes

On IBM i (AS400), there is **no database name** in the connection string. You connect directly to the system and access **libraries** (schemas) in your SQL queries. Tables are referenced as `LIBRARY.TABLE` (e.g., `MYSCH.MYTABLE`).

To list tables in a library:
```sql
SELECT TABLE_SCHEMA, TABLE_NAME FROM QSYS2.SYSTABLES WHERE TABLE_SCHEMA = 'YOURLIB'
```

## Setup

1. Copy the example env file and fill in your real IBM i credentials:
   ```bash
   cp .env.example .env
   # Edit .env with your actual values
   ```

   The app loads `.env` automatically. Environment variables already set in the shell take precedence.

2. Edit `src/fastapi_db2/__init__.py` and replace `JULI1.FCUSTOMER` with your actual library and table name.

## Run

```bash
uv run uvicorn src.fastapi_db2:app --reload
```

The API will be available at **http://localhost:8000**.

## Endpoints

| Method | Path   | Description                          |
|--------|--------|--------------------------------------|
| GET    | /data  | Returns up to 100 rows from the DB2 table as JSON |

### Example response
```json
{
  "table": "MYSCH.MYTABLE",
  "count": 5,
  "columns": ["ID", "NAME", "CREATED"],
  "rows": [
    {"ID": "1", "NAME": "Alice", "CREATED": "2024-01-01"},
    ...
  ]
}
```

## Troubleshooting

### "Driver not found" error
Make sure the IBM i Access ODBC driver is installed and registered in `/etc/odbcinst.ini`. Run `odbcinst -q -d` to verify.

### "Connection refused" error
Check that:
- The hostname is correct (e.g., `pub400.com`)
- Port 446 is open and accessible
- Your IBM i user has network access permissions

### "Column or global variable X not found" error
On IBM i, system table column names may differ from standard SQL. Use `QSYS2.SYSTABLES` instead of `QSYS2.TABLES`, and check column names with `TABLE_SCHEMA` instead of `SYSTEM_TABLE_SCHEMA`.

See [agent.md](agent.md) for coding conventions and agent guidelines.
