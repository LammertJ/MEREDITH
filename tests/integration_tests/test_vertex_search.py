import os

from meredith.vertex_search import VertexSearchAgent


def test_literature() -> None:
    agent = VertexSearchAgent(project_id=os.environ["PROJECT_ID"], location="global")
    result = agent.search_with_vertex(
        "What are potential treatments for lung adenocarcinoma?",
        datastore_id=os.environ["TEST_DATASTORE_ID"],
    )
    assert len(result) > 0
    assert isinstance(result[0], str)
    assert len(result[0]) > 50
