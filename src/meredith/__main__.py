#
# Copyright [May 5, 2024] [Jacqueline Lammert, Maximilian Tschochohei]
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
# 
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#

# Main class for MEREDITH
# MEREDITH (Medical Evidence Retrieval and Data Integration for Tailored Healthcare)
# is a novel LLM system to support treatment recommendations in precision oncology

# Import required packages
from google.cloud import aiplatform
import json


# For access to Gemini model
from google.cloud import aiplatform

# Local required tools
from recommendations import recommendations
from set_variable import set_variable
from cosine import cosine

# Begin by defining global variables

# For authenticating with Google AI Platform
# How to create credentials: https://cloud.google.com/iam/docs/keys-create-delete
from google.oauth2 import service_account
try:
    CREDENTIALS = service_account.Credentials.from_service_account_file('credentials.json')
except:
   print("Error: No credentials.json found in directory. Please create Google Cloud service account credentials (https://cloud.google.com/iam/docs/keys-create-delete).")
   exit()

PROJECT_ID = set_variable("Google Cloud Project ID")
REGION = set_variable("Google Cloud Region", "us-central1") 
LOCATION = set_variable("Discovery Engine Location", "global")

LITERATURE_TOOL = set_variable("Discovery Engine ID of your Literature Repository")
GUIDELINES_TOOL = set_variable("Discovery Engine ID of your Guidelines Repository")
TRIALS_TOOL = set_variable("Discovery Engine ID of your Trials Repository")



# Initialize the Google Cloud AI Platform
aiplatform.init(
    # your Google Cloud Project ID or number
    # environment default used is not set
    project=PROJECT_ID,

    # the Vertex AI region you will use
    # defaults to us-central1
    location=REGION,

    # Your Service Account Credentials
    credentials=CREDENTIALS,
)


print(f"Authenticated with AI Platform {PROJECT_ID}")

import json
with open('patients.json','r') as file:
  patients = json.load(file)

print(f"Loaded {len(patients)} patients")

for patient in patients:
  for biomarker in patient["tumor_pathogenic"]:
      print(16*"*")
      print(f"""Patient {patient["id"]}, Biomarker: {biomarker}""")
      recommendation = recommendations(patient["diagnosis"],biomarker, LITERATURE_TOOL, 
                                       GUIDELINES_TOOL, TRIALS_TOOL, PROJECT_ID, REGION, 
                                       LOCATION, CREDENTIALS)
      print(recommendation)
      print("Non-normalized Cosine Similarity: " + str(cosine(patient["mtb_recommendations"][biomarker],recommendation)))

