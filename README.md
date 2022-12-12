# Microservices as Functions in BigQuery - IP Address Lookup using SQL (Part 2)

## How to reproduce

***Replace the following with your own
1) \<your-project-id>
2) \<gcf-conn-name> (step 2)
3) \<gcf-endpoint> (step 4)

### 1. Clone the repository
    git clone https://github.com/justdataplease/bigquery-translation.git

### 2. CLI : Deploy Cloud Function (gcf)
    gcloud functions deploy bigquery-ip_lookup --gen2 --runtime python39 --trigger-http --project=<your-project-id> --entry-point=ip_lookup --source . --region=europe-west3 --memory=128Mi --max-instances=3 --allow-unauthenticated
Visit Google [Cloud Console Functions](https://console.cloud.google.com/functions/list?project=) to retrieve <gcf-endpoint> (i.e https://bigquery-iplookup-xxxxxx.a.run.app)

### 3. CLI : Create an example DATASET, in BigQuery.
    bq mk --dataset_id=<your-project-id>:ip_lookup --location=EU

### 4. CLI : Create a connection between BigQuery and Cloud Functions (gcf-conn). Make sure to note the first part of the last command (<gcf-conn-name>)
    gcloud components update
    bq mk --connection --display_name='my_gcf_conn' --connection_type=CLOUD_RESOURCE --project_id=<your-project-id> --location=EU gcf-conn
    bq show --project_id=<your-project-id> --location=EU --connection gcf-conn
From the output of the last command, note the name <gcf-conn-name> (i.e. xxxxxx.eu.gcf-conn) 

### 5. BIGQUERY : Create a Remote Function 
    CREATE OR REPLACE FUNCTION `<your-project-id>.ip_lookup.lookup`(ip_address STRING)
    RETURNS STRING
    REMOTE WITH CONNECTION `<gcf-conn-name>`
        OPTIONS (
            -- change this to reflect the Trigger URL of your cloud function (look for the TRIGGER tab)
            endpoint = '<gcf-endpoint>'
        );

### 6. BIGQUERY : Create an example TABLE
    CREATE OR REPLACE TABLE `<your-project-id>.ip_lookup.example_dataset` (
      ip_address STRING,
    );
    
    INSERT INTO `<your-project-id>.ip_lookup.example_dataset`(ip_address)
    VALUES ('190.61.88.147'),
           ('139.99.237.62'),
           ('20.111.54.16'),
           ('185.143.146.171'),
           ('121.126.20.41');

### 7. BIGQUERY : Test Remote Function
    WITH A AS (SELECT `<your-project-id>.ip_lookup.lookup`(ip_address) ip_address_location,ip_address FROM `<your-project-id>.ip_lookup.example_dataset`)
    
    select
      ip_address,
      json_value(ip_address_location, '$.country') country,
      json_value(ip_address_location, '$.state') state,
      json_value(ip_address_location, '$.city') city,
      json_value(ip_address_location, '$.postal_code') postal_code,
      json_value(ip_address_location, '$.latitude') latitude,
      json_value(ip_address_location, '$.longitude') longitude
    from a A;

### 8. CLI : Remove everything
    # Remove Cloud Function (gcf)
    gcloud functions delete bigquery-ip_lookup --region=europe-west3 --project=<your-project-id> --gen2

    # Remove DATASET
    bq rm -r -f -d <your-project-id>:ip_lookup

    # Remove connection between BigQuery and Cloud Functions (gcf-conn)
    bq rm --connection --location=EU <gcf-conn-name>