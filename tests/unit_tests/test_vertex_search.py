from unittest.mock import patch

from google.cloud.discoveryengine_v1alpha.types import SearchResponse

from meredith.vertex_search import VertexSearchAgent


@patch("meredith.vertex_search.SearchServiceClient")
def test_init(mock_client):
    _ = VertexSearchAgent(project_id="test-project", location="moon-dark-1")
    mock_client.assert_called_once()
    _, call_kwargs = mock_client.call_args_list[0]
    assert (
        call_kwargs["client_options"].api_endpoint
        == "moon-dark-1-discoveryengine.googleapis.com"
    )


@patch("meredith.vertex_search.SearchServiceClient")
def test_parse(mock_client) -> None:
    response = SearchResponse.SearchResult(
        chunk={
            "name": "1",
            "id": "id1",
            "content": "test",
            "document_metadata": {
                "uri": "gs://test-bucket/test1.pfg",
                "title": "test-title",
            },
            "page_span": {
                "page_start": 2,
                "page_end": 3,
            },
        }
    )
    client = VertexSearchAgent(project_id="test-project", location="moon-dark-1")
    result = client._parse_results(response)
    expected = (
        "Pages 2-3 from the document test-title mentioned the following:\ntest\n\n"
    )
    assert result == expected
