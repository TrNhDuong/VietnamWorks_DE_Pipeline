{{ config(
    materialized='incremental',
    unique_key='company_id'
) }}

SELECT * FROM {{ ref('gold_company') }}
    
{% if is_incremental() %}
    WHERE processed_date >= coalesce(
                                        (select max(processed_date) from {{ this }}),
                                        '1900-01-01'
                                    )
{% endif %}