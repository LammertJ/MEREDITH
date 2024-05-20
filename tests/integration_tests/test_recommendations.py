from meredith.recommendations import Recommender, _read_config


def test_recommender() -> None:
    config = _read_config("./meredith/config.json", version="v0")
    recommender = Recommender(config=config)
    result = recommender.get_recommendations(
        diagnosis="Urachal Carcinoma", biomarkers="MYC amplification (n>6)"
    )
    assert isinstance(result, str)
    assert len(result) > 50
    print(result)
