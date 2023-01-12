# Microservices as Functions in BigQuery - Offline IP Address Lookup using SQL (Part 2)

Read original article [here](https://medium.com/geekculture/microservices-as-functions-in-bigquery-offline-ip-address-lookup-using-sql-part-2-7b0b91fa5700).

## How to reproduce

***Perform the following actions

Enable Google Cloud Functions. Read more [here](https://cloud.google.com/functions/docs/create-deploy-gcloud). \
Install and configure gcloud CLI. Read more [here](https://cloud.google.com/functions/docs/create-deploy-gcloud). \
Create a free account at [MaxMind](https://www.maxmind.com/) (OPTIONAL if you want to update the dataset).

***Replace the following with your own
1) \<your-project-id>
2) \<gcf-endpoint> (step 2)
3) \<gcf-conn> (step 3)

### 1. Clone the repository
    git clone https://github.com/justdataplease/bigquery-iplookup.git
    cd bigquery-iplookup

### 2. CLI : Deploy Cloud Function (gcf-endpoint)
    gcloud functions deploy bigquery-iplookup --gen2 --runtime python39 --trigger-http --project=<your-project-id> --entry-point=iplookup --source . --region=europe-west3 --memory=128Mi --max-instances=3 --allow-unauthenticated

From the output note the uri  <gcf-endpoint> (i.e https://bigquery-iplookup-xxxxxx.a.run.app) 
or visit Google [Cloud Console Functions](https://console.cloud.google.com/functions/list?project=).

### 3. CLI : Create a connection between BigQuery and Cloud Functions (gcf-conn).

    gcloud components update
    bq mk --connection --display_name='my_gcf_conn' --connection_type=CLOUD_RESOURCE --project_id=<your-project-id> --location=EU gcf-conn
    bq show --project_id=<your-project-id> --location=EU --connection gcf-conn

From the output of the last command, note the name <gcf-conn-name> (i.e. xxxxxx.eu.gcf-conn)

### 4. CLI : Create a toy dataset

    bq mk --dataset_id=<your-project-id>:iplookup --location=EU

### 5. BIGQUERY : Create an example TABLE

    CREATE OR REPLACE TABLE `<your-project-id>.iplookup.example_dataset` (
      ip_address STRING,
    );
    
    INSERT INTO `<your-project-id>.iplookup.example_dataset`(ip_address)
    VALUES ('190.61.88.147'),
           ('139.99.237.62'),
           ('20.111.54.16'),
           ('185.143.146.171'),
           ('121.126.20.41');

### 6. BIGQUERY : Create a Remote Function 
    CREATE OR REPLACE FUNCTION `<your-project-id>.iplookup.lookup`(ip_address STRING)
    RETURNS STRING
    REMOTE WITH CONNECTION `<gcf-conn>`
        OPTIONS (
            -- change this to reflect the Trigger URL of your cloud function (look for the TRIGGER tab)
            endpoint = '<gcf-endpoint>'
        );

### 7. BIGQUERY : Test Remote Function
    WITH A AS (SELECT `<your-project-id>.iplookup.lookup`(ip_address) ip_address_location,ip_address FROM `<your-project-id>.iplookup.example_dataset`)
    
    SELECT
      ip_address,
      json_value(ip_address_location, '$.country') country,
      json_value(ip_address_location, '$.state') state,
      json_value(ip_address_location, '$.city') city,
      json_value(ip_address_location, '$.postal_code') postal_code,
      json_value(ip_address_location, '$.latitude') latitude,
      json_value(ip_address_location, '$.longitude') longitude
    FROM A;

Output
    
    1	
    ip_address : 139.99.237.62
    country : Australia
    state : New South Wales
    city : Sydney
    postal_code : 2000
    latitude : -33.8715
    longitude : 151.2006

    2	
    ip_address : 20.111.54.16
    country : France
    state : Paris
    city : Paris
    postal_code : 75001
    latitude : 48.8323
    longitude : 2.4075

    3	
    ip_address : 190.61.88.147
    country : Guatemala
    state : Departamento de Guatemala
    city : Guatemala City
    postal_code : 01010
    latitude : 14.6343
    longitude : -90.5155

    4	
    ip_address : 185.143.146.171
    country : Ukraine
    state : Kyiv City
    city : Kyiv
    postal_code : 03187
    latitude : 50.458
    longitude : 30.5303

    5	
    ip_address : 121.126.20.41
    country : South Korea
    state : Seoul
    city : Guro-gu
    postal_code : 083
    latitude : 37.4975
    longitude : 126.8501


### 8. CLI : Remove everything
    # Remove Cloud Function (gcf)
    gcloud functions delete bigquery-iplookup --region=europe-west3 --project=<your-project-id> --gen2

    # Remove DATASET
    bq rm -r -f -d <your-project-id>:iplookup

    # Remove connection between BigQuery and Cloud Functions (gcf-conn)
    bq rm --connection --location=EU <gcf-conn>