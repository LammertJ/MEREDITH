# Introduction
MEREDITH (Medical Evidence Retrieval and Data Integration for Tailored Healthcare) is a novel LLM system to support treatment recommendations in precision oncology. MEREDITH leverages Google Cloud AI Platform to generate predictions for recommended precision oncology treatment for patients based on their diagnosis (e.g., NSCLC) and molecular profile. MEREDITH was developed as part of a research project undertaken by a team of scientists at [MRI Klinikum rechts der Isar der Technischen Universtität München] (https://www.mri.tum.de/). As soon as the fulltext is published, it will be provided here for full context.

# Technical Design
MEREDITH leverages a combination of [Vertex AI Agents](https://cloud.google.com/dialogflow/vertex/docs/concept/agents), which are used as retrievers in a Retrieval Augmented Generation (RAG) architecture, and calls to [Vertex AI Text Generation Models](https://cloud.google.com/vertex-ai/generative-ai/docs/model-reference/text) to perform summarization tasks, followed by calls to [Vertex AI Generative Models](https://cloud.google.com/vertex-ai/generative-ai/docs/multimodal/overview) to perform synthesization tasks. 

# How-to
## Prerequisites
To execute Meredith, you will need:
- A Google Cloud project with the [Vertex AI API](https://cloud.google.com/vertex-ai/docs/reference/rest) enabled
- A `credentials.json` for a service account in your Google Cloud project with `Vertex AI user` and `Discovery Engine viewer` permissions
- Three [Vertex AI Agents](https://cloud.google.com/dialogflow/vertex/docs/concept/agents): 1/ agent with literature on precision oncology research (we used the query `targeted treatment for [biomarker]` on [PubMed](https://pubmed.ncbi.nlm.nih.gov/), 2/ agent with currently valid standards of care, we used [Deutsche Krebsgesellschaft](https://www.krebsgesellschaft.de/), 3/ agent with currently recruiting clinical trials, we used [QuickQueck](https://www.quickqueck.de/); all input documents are provided as .pdf; all agents must be configured as Layout Parsers and set to "Chunking" mode; unfortunately we cannot make our agents publicly available due to copyright concerns
- And that's it, you're good to go!

## Patient input data
- Patient input data is provided in [patient.json](https://github.com/LammertJ/MEREDITH/blob/main/src/meredith/patients.json). These patients are synthetic patients that were used in previous studies, e.g., [Benary et al., 2023](https://jamanetwork.com/journals/jamanetworkopen/fullarticle/2812097)
- Patient input data can be modified. We performed pre-screening on patient input data to identify and separate pathogenic mutations in `tumor_pathogenic` to optimize load on the system. Only pathogenic mutations will be processed
