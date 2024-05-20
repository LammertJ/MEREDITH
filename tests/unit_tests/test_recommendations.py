from meredith.recommendations import Config, _read_config


def test_read_config() -> None:
    config = _read_config("./meredith/config.json")
    assert isinstance(config, Config)
    assert len(config.literature_prompt) > 20
