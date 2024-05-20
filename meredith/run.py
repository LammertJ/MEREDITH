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
import argparse
import json
from typing import Any, Dict

from google.cloud import aiplatform

# For authenticating with Google AI Platform
# How to create credentials: https://cloud.google.com/iam/docs/keys-create-delete
from google.oauth2 import service_account

from meredith.cosine import cosine
from meredith.recommendations import Recommender, _read_config


def _parse_args() -> Dict[str, Any]:
    parser = argparse.ArgumentParser(description="Argument parser for MEREDITH.")
    parser.add_argument(
        "-config_path", help="path to config", default="./meredith/config.json"
    )
    parser.add_argument(
        "-data_path", help="path to config", default="./meredith/data/patients.json"
    )
    parser.add_argument("-version", default="v0", help="Description for bar argument")
    return vars(parser.parse_args())


def run():
    args = _parse_args()
    with open(args["data_path"], "r", encoding="utf-8") as read_file:
        patients = json.load(read_file)
    print(f"Loaded {len(patients)} patients")
    credentials = None
    try:
        credentials = service_account.Credentials.from_service_account_file(
            "credentials.json"
        )
    except FileNotFoundError:
        print("No credentials.json found in directory, attempting to use ADC...")

    config = _read_config(args["config_path"], version=args["version"])
    recommender = Recommender(config=config, credentials=credentials)
    aiplatform.init(
        project=config.project_id,
        location=config.vertexai_locaiton,
        credentials=credentials,
    )

    for patient in patients:
        for biomarker in patient["tumor_pathogenic"]:
            print(16 * "*")
            print(f"""Patient {patient["id"]}, Biomarker: {biomarker}""")
            recommendation = recommender.get_recommendations(
                patient["diagnosis"],
                biomarker,
            )
            print(recommendation)
            print(
                "Non-normalized Cosine Similarity: "
                + str(cosine(patient["mtb_recommendations"][biomarker], recommendation))
            )


if __name__ == "__main__":
    run()
