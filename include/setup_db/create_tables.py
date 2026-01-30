import psycopg
import os
from include.utilis.utilis import loader

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CONFIG_PATH = os.path.join(BASE_DIR, 'config.yaml')

def create_tables():
    # Load config
    postgres_config = loader(config_path=CONFIG_PATH, type="posgres")
    
    # Connect directly using psycopg to handle DDL (autocommit recommended for some DDLs, but inside transaction is fine usually)
    # Using our infra wrapper to get connection
    connect_str = postgres_config['connect_str']
    
    ddl_staging = """
    CREATE SCHEMA IF NOT EXISTS staging;
    
    CREATE TABLE IF NOT EXISTS staging.job_company (
        jobId TEXT,
        jobTitle TEXT,
        jobUrl TEXT,
        jobDescription TEXT,
        jobRequirement TEXT,
        jobLevel TEXT,
        jobLevelVI TEXT,
        salary TEXT,
        salaryMin NUMERIC,
        salaryMax NUMERIC,
        salaryCurrency TEXT,
        skills TEXT,
        benefits TEXT,
        createdOn TIMESTAMP,
        expiredOn TIMESTAMP,
        companyName TEXT,
        companyUrl TEXT,
        companyId TEXT,
        processed_date DATE,
        working_locations JSONB,
        industries JSONB
    );
    """
    
    ddl_warehouse = """
    CREATE SCHEMA IF NOT EXISTS warehouse;
    
    CREATE TABLE IF NOT EXISTS warehouse.company (
        company_id TEXT PRIMARY KEY,
        company_name TEXT,
        company_url TEXT,
        processed_date DATE
    );
    
    CREATE TABLE IF NOT EXISTS warehouse.job (
        job_id TEXT PRIMARY KEY,
        job_title TEXT,
        job_url TEXT,
        job_description TEXT,
        job_requirement TEXT,
        job_level TEXT,
        job_level_vi TEXT,
        salary_min NUMERIC,
        salary_max NUMERIC,
        salary_currency TEXT,
        working_locations JSONB,
        created_on TIMESTAMP,
        expired_on TIMESTAMP,
        company_id TEXT,
        industries JSONB,
        processed_date DATE
    );
    """
    
    try:
        with psycopg.connect(connect_str) as conn:
            with conn.cursor() as cur:
                print("🚀 Creating Staging Schema & Table...")
                cur.execute(ddl_staging)
                
                print("🚀 Creating Warehouse Schema & Tables...")
                cur.execute(ddl_warehouse)
                
            conn.commit()
            print("✅ Database Setup Completed Successfully!")
        
    except Exception as e:
        conn.rollback()
        print(f"❌ Error creating tables: {e}")
    finally:
        conn.close()

create_tables()
