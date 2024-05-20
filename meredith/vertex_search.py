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

# This class initiates a "Tool" to connect to a Discovery Engine and retrieve
# snippets containing data for the LLM to process

from typing import Optional

from google.api_core.client_options import ClientOptions
from google.cloud.discoveryengine_v1alpha import SearchServiceClient
from google.cloud.discoveryengine_v1alpha.types import SearchRequest, SearchResponse
from google.oauth2 import service_account


class VertexSearchAgent:
    def __init__(
        self,
        project_id: str,
        location: str,
        credentials: Optional[service_account.Credentials] = None,
    ):
        # https://cloud.google.com/generative-ai-app-builder/docs/locations#specify_a_multi-region_for_your_data_store
        client_options = (
            ClientOptions(api_endpoint=f"{location}-discoveryengine.googleapis.com")
            if location != "global"
            else None
        )
        self._client = SearchServiceClient(
            client_options=client_options, credentials=credentials
        )
        self._project_id = project_id
        self._location = location

    def get_serving_config(self, datastore_id: str) -> str:
        return self._client.serving_config_path(
            project=self._project_id,
            location=self._location,
            data_store=datastore_id,
            serving_config="default_config",
        )

    def search_with_vertex(self, search_query: str, datastore_id: str) -> list[str]:
        """Returns a list of Vertex Search snippets for a given query."""
        request = SearchRequest(
            serving_config=self.get_serving_config(datastore_id=datastore_id),
            query=search_query,
            page_size=5,
            query_expansion_spec=SearchRequest.QueryExpansionSpec(
                condition=SearchRequest.QueryExpansionSpec.Condition.AUTO,
            ),
            spell_correction_spec=SearchRequest.SpellCorrectionSpec(
                mode=SearchRequest.SpellCorrectionSpec.Mode.AUTO
            ),
        )
        results = self._client.search(request).results
        return [self._parse_results(r) for r in results]

    def _parse_results(self, result: SearchResponse.SearchResult) -> str:
        chunk = result.chunk
        output = (
            f"Pages {chunk.page_span.page_start}-{chunk.page_span.page_end} "
            f"from the document {chunk.document_metadata.title} mentioned the "
            "following:\n"
            f"{chunk.content}\n\n"
        )
        return output
