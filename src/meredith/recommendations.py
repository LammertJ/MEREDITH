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

from tool import tool
from vertexai.generative_models import (
    GenerationConfig,
    GenerativeModel,
)
from vertexai.language_models import TextGenerationModel


from google.oauth2 import service_account

def recommendations(
    diagnosis: str,
    biomarkers: str,
    LITERATURE_TOOL: str,
    GUIDELINES_TOOL: str,
    TRIALS_TOOL: str,
    PROJECT_ID: str,
    REGION: str,
    LOCATION: str,
    CREDENTIALS: service_account.Credentials
) -> str:
    
    # Set the required models
    # We use a TextGenerationModel due to better text matching
    # And a GenerativeModel for summarization
    TEXT_MODEL = "text-unicorn"
    GENERATIVE_MODEL = "gemini-1.5-pro-preview-0409"

    vertex_llm_text = TextGenerationModel.from_pretrained(TEXT_MODEL)
    vertex_llm_generative = GenerativeModel(GENERATIVE_MODEL)
    
    #Set hyperparameters for the models
    generation_config = GenerationConfig(
        temperature=0.2,
        top_p=1.0,
        top_k=32,
        candidate_count=1,
        max_output_tokens=8192,
    )
    parameters = {
        "temperature": 0.2,
        "max_output_tokens": 1024,
        "top_p": 0.8,
        "top_k": 40
    }


    # Prompt for literature agent
    literature_agent = """You are an intelligent assistant helping oncologists find targeted therapies.
    You search relevant scientific literature for suitable therapies based on patient diagnosis and biomarkers.
    You identify and list suitable targeted therapies.
    You then prioritize targeted therapies based on the most suitable option.

    You then list: All possible therapy options for the exact biomarker found in the patient with reasons for your recommendation and the source document pdf

    Use ONLY the information in the literature to answer the question. Do not make up an answer. Pay careful attention to the spelling of biomarkers.

    Patient Diagnosis:
    {diagnosis}

    Patient Biomarkers:
    {biomarkers}

    Relevant Literature:
    {literature}

    Your response:
    ***Treatment options from literature:***
    1/ Treatment option: Reasoning (Source.pdf)
    2/ Treatment option: Reasoning (Source.pdf)
    n/ etc.
    """

    # Prompt for guidelines agent
    guidelines_agent = """You are an intelligent assistant helping oncologists find targeted therapies.
    You search relevant oncological guidelines for suitable therapies based on patient diagnosis and biomarkers.
    You identify and list suitable targeted therapies based on patient diagnosis and biomarkers.

    You then list: All possible therapy options for the exact biomarker found in the patient with reasons for your recommendation and the source document pdf

    Use ONLY the information in the literature to answer the question. Do not make up an answer.
    Ensure that the spelling of biomarkers in the guidelines exactly matches the spelling of the patients biomarkers.
    If you cannot find a suitable therapy option, say: "No suitable therapy options found in guidelines."

    Patient Diagnosis:
    {diagnosis}

    Patient Biomarkers:
    {biomarkers}

    Oncological guidelines:
    {clinical_guidelines}

    Your response:
    ***Treatment options from guidelines:***
    1/ Treatment option: Reasoning (Source.pdf)
    2/ Treatment option: Reasoning (Source.pdf)
    n/ etc.
    """

    # Prompt for studies agent
    studies_agent = """You are an intelligent assistant helping oncologists find currently recruiting studies
    that might benefit their patients based on their diagnosis and biomarkers.

    You list: Currently recruiting clinical studies that might benefit the patient based on their diagnosis and biomarker
    with reasons for your recommendation and the source document pdf

    Use ONLY the information in the literature to answer the question. Do not make up an answer.
    Ensure that the spelling of biomarkers in the study exactly matches the spelling of the patients biomarkers.
    If you cannot find a suitable clincial study option, say: "No suitable clinical study options found."

    Patient Diagnosis:
    {diagnosis}

    Patient Biomarkers:
    {biomarkers}

    Recruiting clinical study:
    {clinical_studies}

    Your response:
    ***Clinical studies options:***
    1/ Study: Reasoning (Source.pdf)
    2/ Study: Reasoning (Source.pdf)
    n/ etc.
    """

    # Prompt for summary agent
    summary_agent = """You are an intelligent assistant helping oncologists find suitable therapies for their patients based on their diagnosis and biomarkers.

    Your sources are treatment options from recently published literature, currently recruiting scientific studies and valid oncological guidelines. Based on the input data and your knowledge, prioritize and choose the most suitable treatment option.

    Use ONLY the information in the prepared context to answer the question. Do not make up an answer.
    If you cannot find a suitable clincial study option, say: "No suitable clinical study options found."

    Patient Diagnosis:
    {diagnosis}

    Patient Biomarkers:
    {biomarkers}

    Prepared treatment options:
    {treatment_options}

    Your response:
    ***Prioritized treatment options:***
    1/ Treatment option: Reasoning (Source.pdf)
    2/ Treatment option: Reasoning (Source.pdf)
    n/ etc.
    """
    
    # Extract source data from tools
    literature = tool(f"Therapy for {diagnosis} with {biomarkers}",LITERATURE_TOOL,PROJECT_ID,REGION,LOCATION, CREDENTIALS)
    clinical_guidelines = tool(f"Therapy for {diagnosis} with {biomarkers}",GUIDELINES_TOOL,PROJECT_ID,REGION,LOCATION, CREDENTIALS)
    clinical_studies = tool(f"Eligibility criteria for {diagnosis} with {biomarkers}",TRIALS_TOOL,PROJECT_ID,REGION,LOCATION, CREDENTIALS)
    
    # We can choose between vertex_llm_generative and vertex_llm_text here
    literature_outcome = vertex_llm_text.predict(
      literature_agent.format(diagnosis=diagnosis, biomarkers=biomarkers, literature=literature),**parameters
    )
    guidelines_outcome = vertex_llm_text.predict(
      guidelines_agent.format(diagnosis=diagnosis, biomarkers=biomarkers, clinical_guidelines=clinical_guidelines),**parameters
    )
    clinical_studies_outcome = vertex_llm_text.predict(
      studies_agent.format(diagnosis=diagnosis, biomarkers=biomarkers, clinical_studies=clinical_studies),**parameters
    )

    # Create the long list of treatment options
    treatment_options = "********************************************************************************\n"
    treatment_options = treatment_options + f"Biomarker {biomarkers}\n"
    treatment_options = treatment_options + literature_outcome.text + "\n\n"
    treatment_options = treatment_options + guidelines_outcome.text + "\n\n"
    treatment_options = treatment_options + clinical_studies_outcome.text + "\n\n"

    response = vertex_llm_generative.generate_content(
        summary_agent.format(diagnosis=diagnosis, biomarkers=biomarkers, treatment_options=treatment_options),
        generation_config=generation_config,
        stream=False,
    ).text

    return response