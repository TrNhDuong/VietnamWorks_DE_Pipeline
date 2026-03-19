{{ config(
    materialized='incremental',
    unique_key='job_id'
) }}

SELECT * FROM {{ ref('gold_job') }}

{% if is_incremental() %}
    WHERE processed_date >= coalesce(
                                        (select max(processed_date) from {{ this }}),
                                        '1900-01-01'
                                    )
{% endif %}