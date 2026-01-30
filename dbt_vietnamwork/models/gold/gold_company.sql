{{ config(materialized='view') }}

WITH companies AS (
    SELECT companyname AS company_name, companyurl AS company_url, companyid AS company_id,
        processed_date
    FROM {{ source('staging', 'job_company') }}
),

deduplicated AS (
    SELECT *, 
        ROW_NUMBER() OVER (
            PARTITION BY company_id 
            ORDER BY processed_date DESC
        ) as rn
    FROM companies
)

SELECT * FROM deduplicated WHERE rn = 1 AND processed_date = '{{ var("run_date") }}'