import os
from azure.storage.blob import BlobServiceClient
import json
import logging

# Retrieve the connection string and container name from environment variables
storage_account_link = os.environ.get("SecondaryStorage", None)
storage_account_location = os.environ.get("storage_name", None)
import random

# Initial JSON data
initial_json = {
    "first": {
        "Oslo Storo": 0,
        "Oslo City": 0,
        "Oslo Torggata": 0,
        "Karl Johan": 0,
        "Fredrikstad": 0,
        "Oslo Lokka": 0,
		"Sandnes": 0
    },
    "second": {
        "Trondheim": 0,
        "Bergen": 0,
        "Stavanger": 0,
        "Oslo Steen_Strom": 0,
        "Oslo Smestad": 0,
        "Bjørvika":0,
        "Alexander Kielland":0
    },
    "first_run_count": 0,
    "second_run_count": 0
}


def fetch_or_initialize_json():
    try:
        # Initialize the BlobServiceClient
        blob_service_client = BlobServiceClient.from_connection_string(
            storage_account_link
        )
        

        # Create the container client
        container_client = blob_service_client.get_container_client(
            storage_account_location
        )

        # Define the blob name (filename in the container)
        blob_name = "execution_counts_type.json"

        # Create the blob client
        blob_client = container_client.get_blob_client(blob_name)

        try:
            # Attempt to read the blob content
            blob_data = blob_client.download_blob().readall()
            data = json.loads(blob_data)
            logging.info(f"Fetched existing JSON from blob: {blob_name}")
        except Exception as e:
            # If the blob does not exist, use the initial JSON data
            if "BlobNotFound" in str(e):
                data = initial_json
                logging.info(f"Blob not found. Initializing with initial JSON data.")
            else:
                raise

    except Exception as e:
        logging.info(f"Error fetching or initializing JSON: {e}")
        data = initial_json

    return data


def update_execution_count(group, restaurant, data):
    if group in data and restaurant in data[group]:
        data[group][restaurant] += 1
        
    return data

def group_run_count(data,run_count_group):
    data[run_count_group] += 1
    return data

def save_json_file(data):
    try:
        # Initialize the BlobServiceClient
        blob_service_client = BlobServiceClient.from_connection_string(
            storage_account_link
        )

        # Create the container client
        container_client = blob_service_client.get_container_client(
            storage_account_location
        )

        # Create the container if it does not exist
        try:
            container_client.create_container()
        except Exception as e:
            # Handle the error if the container already exists
            if "ContainerAlreadyExists" not in str(e):
                raise

        # Convert the dictionary to a JSON string
        data_json = json.dumps(data, indent=4)

        # Define the blob name (filename in the container)
        blob_name = "execution_counts_type.json"

        # Create the blob client
        blob_client = container_client.get_blob_client(blob_name)

        # Upload the JSON file
        blob_client.upload_blob(data_json, overwrite=True)

        logging.info(f"File {blob_name} uploaded successfully.")

    except Exception as e:
        logging.info(f"Error: {e}")


def select_minimum_restaurant(data):
    # Extract run counts
    first_group_run_count = data.get("first_run_count", 0)
    second_group_run_count = data.get("second_run_count", 0)


    # Select the group with the lower run count
    if first_group_run_count < second_group_run_count:
        group_choice = "first"
    elif second_group_run_count < first_group_run_count:
        group_choice = "second"
    else:
        # If both groups have the same run count, select the group with the minimum count value
        first_min_count = min(data["first"].values())
        second_min_count = min(data["second"].values())
        if first_min_count < second_min_count:
            group_choice = "first"
        elif second_min_count < first_min_count:
            group_choice = "second"
        else:
            # If both groups have the same minimum count value, choose randomly
            group_choice = random.choice(["first", "second"])

    # Find the minimum count in the chosen group
    chosen_group = data.get(group_choice, {})
    min_count = min(chosen_group.values())

    # Collect all restaurants with the minimum count in the chosen group
    candidates = list(chosen_group.keys())

    return group_choice, candidates
