from tools.approve_tool import approve

def test_approve_tool_formatting():
    mock_sources = "Source 1:\nTitle: Test\nURL: http://example.com"
    res = approve.invoke({"sources": mock_sources})
    assert res == f"Sources approved for summary:\n\n{mock_sources}"
