import pandas as pd

from ai_manager import AIManager
from fakeprovider import FakeProvider
from moderationpipeline import ModerationPipeline

GOOD_REPLY = '{"harmful": true, "category": "harassment", "severity": 2, "target": "individual", "confidence": 0.9, "reason": "Test reply."}'
RECORD = {"User ID": 1, "username": "ben", "processed_comments": "u r a l0ser"}


def test_pipeline_saves_moderated_report(tmp_path):
    pipeline = ModerationPipeline(AIManager(FakeProvider([GOOD_REPLY])), delay_seconds=0)
    df = pipeline.process(pd.DataFrame([RECORD]), tmp_path / "out.csv")
    assert df.loc[0, "priority"] == "P3"
    assert (tmp_path / "out.csv").exists()


def test_pipeline_sends_failed_ai_record_to_manual_review(tmp_path):
    pipeline = ModerationPipeline(AIManager(FakeProvider([None, None])), delay_seconds=0)
    df = pipeline.process(pd.DataFrame([RECORD]), tmp_path / "out.csv")
    assert df.loc[0, "recommended_action"] == "Manual review required"