{{ config(materialized='view') }}

WITH jobs AS (
    SELECT 
        jobid AS job_id, jobtitle AS job_title, joburl AS job_url, jobdescription AS job_description,
        jobrequirement AS job_requirement, joblevel AS job_level, joblevelvi AS job_level_vi,
        salary AS salary, salarymin AS salary_min, salarymax AS salary_max, salarycurrency AS salary_currency,
        skills AS skills, benefits AS benefits, 
        createdon AS created_on, expiredon AS expired_on, companyid AS company_id,
        processed_date, working_locations, industries
    FROM {{ source('staging', 'job_company') }}
),

deduplicated AS (
    SELECT *,
        ROW_NUMBER() OVER (
            PARTITION BY job_id 
            ORDER BY processed_date DESC
        ) as rn
    FROM jobs
)

SELECT * FROM deduplicated WHERE rn = 1 AND processed_date = '{{ var("run_date") }}'