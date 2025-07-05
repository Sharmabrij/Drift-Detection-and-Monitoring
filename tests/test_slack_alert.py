import pytest
import requests
from unittest import mock
from flows.slack_utils import send_slack_alert

def test_send_slack_alert_handles_http_error(caplog):
    with mock.patch("flows.slack_utils.requests.post") as mock_post:
        mock_post.return_value.status_code = 404
        mock_post.return_value.text = "no_service"

        send_slack_alert("Test message")

        assert "Slack error: 404 - no_service" in caplog.text
