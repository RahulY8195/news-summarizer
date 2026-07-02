from unittest.mock import Mock, patch

from app import summarizer


def _mock_response(text: str) -> Mock:
    resp = Mock()
    resp.json.return_value = {"response": text}
    resp.raise_for_status.return_value = None
    return resp


@patch("app.summarizer.requests.post")
def test_summarize_returns_model_response(mock_post):
    mock_post.return_value = _mock_response("A concise summary.")
    result = summarizer.summarize("Some article content.")
    assert result == "A concise summary."


@patch("app.summarizer.requests.post")
def test_summarize_retries_once_on_refusal(mock_post):
    mock_post.side_effect = [
        _mock_response("I'm sorry, I can't help with that."),
        _mock_response("A valid summary on retry."),
    ]
    result = summarizer.summarize("Some article content.")
    assert result == "A valid summary on retry."
    assert mock_post.call_count == 2


@patch("app.summarizer.requests.post")
def test_summarize_falls_back_to_original_text_after_two_refusals(mock_post):
    mock_post.return_value = _mock_response("I cannot do that.")
    result = summarizer.summarize("Original content.")
    assert result == "Original content."
    assert mock_post.call_count == 2


@patch("app.summarizer.requests.post")
def test_summarize_story_with_single_source_uses_plain_summarize(mock_post):
    mock_post.return_value = _mock_response("Single-source summary.")
    result = summarizer.summarize_story(["Article text"], ["Source A"])
    assert result == "Single-source summary."
    prompt_sent = mock_post.call_args.kwargs["json"]["prompt"]
    assert "Synthesized" not in prompt_sent


@patch("app.summarizer.requests.post")
def test_summarize_story_with_multiple_sources_builds_synthesis_prompt(mock_post):
    mock_post.return_value = _mock_response("Synthesized cross-source summary.")
    result = summarizer.summarize_story(
        ["Text from A", "Text from B"], ["Source A", "Source B"]
    )
    assert result == "Synthesized cross-source summary."
    prompt_sent = mock_post.call_args.kwargs["json"]["prompt"]
    assert "Source 1 (Source A)" in prompt_sent
    assert "Source 2 (Source B)" in prompt_sent
