import pytest

from reportstore import ReportStore


def test_report_store_cannot_be_instantiated():
    with pytest.raises(TypeError):
        ReportStore()


def test_store_missing_a_method_cannot_be_instantiated():
    class IncompleteStore(ReportStore):
        def load(self, name):
            return None

    with pytest.raises(TypeError):
        IncompleteStore()
