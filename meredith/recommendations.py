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
#
# This class creates three agents with distinct prompts.
# Agent 1 parses literature and help oncologists identify matching therapy
# options from literature
#
# Agent 2 parses currently recruiting studies from a discovery engine to
# identify studies that recruit similar to the patients' profile
#
# Agent 3 parses currently valid oncological guidelines to identify therapies
# approved by guidelines
#
# Agent 4 summarizes the findings of the other three agents and makes an
# authoritative final recommendation
#
import json
from dataclasses import dataclass
from typing import Optional

from google.oauth2 import service_account
from vertexai.generative_models import (
    GenerationConfig,
    GenerativeModel,
)
from vertexai.language_models import TextGenerationModel

from meredith import prompts
from meredith.vertex_search import VertexSearchAgent


@dataclass
class Config:
    literature_datastore_id: str
    guidlines_datastore_id: str
    studies_datastore_id: str
    literature_prompt: str
    guidelines_prompt: str
    studies_prompt: str
    summary_prompt: str
    project_id: str
    vs_location: str = "global"
    vertexai_locaiton: str = "us-central1"
    model_name: str = "gemini-1.5-pro-preview-0514"
    gemini_temperature: float = 0.2
    gemini_top_p: float = 1.0
    gemini_top_k: int = 32
    gemini_candidate_count: int = 1
    gemini_max_output_tokens: int = 8192
    text_temperature: float = 0.2
    text_top_p: float = 0.8
    text_top_k: int = 40
    text_candidate_count: int = 1
    text_max_output_tokens: int = 1024


def _read_config(config_path: str, version: str = "v0") -> Config:
    with open(config_path, "r", encoding="utf-8") as read_file:
        config_values = json.load(read_file)
    key_prompts = [
        "literature_prompt",
        "guidelines_prompt",
        "studies_prompt",
        "summary_prompt",
    ]
    config = config_values["versions"][version]
    for key in key_prompts:
        if key in config:
            config[key] = getattr(prompts, config[key])
    return Config(**config)


class Recommender:
    def __init__(
        self,
        config: Config,
        credentials: Optional[service_account.Credentials] = None,
    ):
        self._config = config
        self._llm = GenerativeModel(config.model_name)
        self._llm_text = TextGenerationModel.from_pretrained("text-unicorn")
        llm_args = [
            "temperature",
            "top_p",
            "top_k",
            "candidate_count",
            "max_output_tokens",
        ]
        self._text_llm_args = {k: getattr(config, "text_" + k) for k in llm_args}
        self._gemini_args = {k: getattr(config, "gemini_" + k) for k in llm_args}
        self._vertex_search_agent = VertexSearchAgent(
            project_id=config.project_id,
            location=config.vs_location,
            credentials=credentials,
        )

    def get_recommendations(
        self,
        diagnosis: str,
        biomarkers: str,
    ) -> str:
        """Prepares a recommendation."""
        literature = self._vertex_search_agent.search_with_vertex(
            search_query=f"Therapy for {diagnosis} with {biomarkers}",
            datastore_id=self._config.literature_datastore_id,
        )
        clinical_guidelines = self._vertex_search_agent.search_with_vertex(
            search_query=f"Therapy for {diagnosis} with {biomarkers}",
            datastore_id=self._config.guidlines_datastore_id,
        )
        clinical_studies = self._vertex_search_agent.search_with_vertex(
            search_query=f"Eligibility criteria for {diagnosis} with {biomarkers}",
            datastore_id=self._config.studies_datastore_id,
        )

        # We can choose between vertex_llm_generative and vertex_llm_text here
        prompt = self._config.literature_prompt.format(
            diagnosis=diagnosis, biomarkers=biomarkers, literature=literature
        )
        literature_outcome = self._llm_text.predict(
            prompt,
            **self._text_llm_args,
        )
        guidelines_outcome = self._llm_text.predict(
            self._config.guidelines_prompt.format(
                diagnosis=diagnosis,
                biomarkers=biomarkers,
                clinical_guidelines=clinical_guidelines,
            ),
            **self._text_llm_args,
        )
        clinical_studies_outcome = self._llm_text.predict(
            self._config.studies_prompt.format(
                diagnosis=diagnosis,
                biomarkers=biomarkers,
                clinical_studies=clinical_studies,
            ),
            **self._text_llm_args,
        )

        treatment_options = "********************************************************************************\n"
        treatment_options = treatment_options + f"Biomarker {biomarkers}\n"
        treatment_options = treatment_options + literature_outcome.text + "\n\n"
        treatment_options = treatment_options + guidelines_outcome.text + "\n\n"
        treatment_options = treatment_options + clinical_studies_outcome.text + "\n\n"

        response = self._llm.generate_content(
            self._config.summary_prompt.format(
                diagnosis=diagnosis,
                biomarkers=biomarkers,
                treatment_options=treatment_options,
            ),
            generation_config=GenerationConfig(**self._gemini_args),
        ).text

        return response
