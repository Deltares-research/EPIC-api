from typing import Callable

import pytest

from epic_app.externals.external_wrapper_status import ExternalWrapperStatus


class TestExternalWrapperStatusType:
    @pytest.mark.parametrize(
        "action, as_str",
        [
            pytest.param(lambda x: x.to_ready("something"), "Ready", id="Ready"),
            pytest.param(
                lambda x: x.to_initialized("something"),
                "Initialized",
                id="To Initialized",
            ),
            pytest.param(
                lambda x: x.to_succeeded("something"), "Succeeded", id="To Succeeded"
            ),
            pytest.param(
                lambda x: x.to_failed("something"), "Failed: something", id="To Failed"
            ),
        ],
    )
    def test_init_and_set_status(self, action: Callable, as_str: str):
        _external_wrapper_status = ExternalWrapperStatus()
        action(_external_wrapper_status)
        assert str(_external_wrapper_status) == as_str
