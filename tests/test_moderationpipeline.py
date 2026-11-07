import pandas as pd

from ai_manager import AIManager
from fakeprovider import FakeProvider
from moderationpipeline import ModerationPipeline
from logic_manager_oop import LogicManager
from moderation_policy import ModerationPolicy
from weightedriskscorer import WeightedRiskScorer

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


def test_pipeline_with_injected_oop_logic_manager(tmp_path):
    """
    Verify that ModerationPipeline works with an explicitly
    injected OOP LogicManager.
    """

    # Construct the OOP LogicManager with its dependencies.
    logic_manager = LogicManager(
        scorer=WeightedRiskScorer(),
        policy=ModerationPolicy()
    )

    # Inject LogicManager into the pipeline.
    pipeline = ModerationPipeline(
        ai_manager=AIManager(FakeProvider([GOOD_REPLY])),
        logic_manager_instance=logic_manager,
        delay_seconds=0
    )

    # Execute the complete moderation pipeline.
    csv_path = tmp_path / "oop_report.csv"

    df = pipeline.process(
        pd.DataFrame([RECORD]),
        csv_path
    )

    # Verify the moderation decision.
    assert df.loc[0, "priority"] == "P3"
    assert df.loc[0, "username"] == "ben"

    # Verify the report was saved.
    assert csv_path.exists()