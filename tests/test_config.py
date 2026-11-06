import pytest

from app.config import ConfigError, Settings, load_settings


def test_defaults_need_no_secrets():
    s = load_settings({})
    assert s.telegram_bot_token is None
    assert s.log_level == "INFO"
    assert s.max_input_length == 4096


def test_token_loaded_and_trimmed():
    s = load_settings({"TELEGRAM_BOT_TOKEN": "  123:abc  "})
    assert s.telegram_bot_token == "123:abc"


def test_token_never_appears_in_repr():
    s = load_settings({"TELEGRAM_BOT_TOKEN": "123:SECRETVALUE"})
    assert "SECRETVALUE" not in repr(s)
    assert "SECRETVALUE" not in str(s)


def test_token_required_when_asked():
    with pytest.raises(ConfigError) as info:
        load_settings({}, require_bot_token=True)
    assert "TELEGRAM_BOT_TOKEN" in str(info.value)
    with pytest.raises(ConfigError):
        load_settings({"TELEGRAM_BOT_TOKEN": "   "}, require_bot_token=True)


def test_log_level_validated_and_normalised():
    assert load_settings({"LOG_LEVEL": "debug"}).log_level == "DEBUG"
    with pytest.raises(ConfigError):
        load_settings({"LOG_LEVEL": "loud"})


@pytest.mark.parametrize("value", ["0", "-5", "abc", "4097", "1.5", "١"])
def test_max_input_length_rejects_bad_values(value):
    with pytest.raises(ConfigError):
        load_settings({"MAX_INPUT_LENGTH": value})


def test_max_input_length_accepts_valid_value():
    assert load_settings({"MAX_INPUT_LENGTH": "100"}).max_input_length == 100


def test_error_messages_do_not_contain_values():
    with pytest.raises(ConfigError) as info:
        load_settings({"MAX_INPUT_LENGTH": "SECRET-ish"})
    assert "SECRET-ish" not in str(info.value)


def test_settings_is_frozen():
    with pytest.raises(AttributeError):
        Settings().log_level = "DEBUG"  # type: ignore[misc]
