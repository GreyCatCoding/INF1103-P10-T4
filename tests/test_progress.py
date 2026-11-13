"""Tests for the threaded progress bar without AI API."""
import threading
import time

import pandas as pd

from ai_manager.ai_manager import AIManager
from fakeprovider import FakeProvider
from logic_manager.moderationpipeline import ModerationPipeline
from ai_manager.progresstracker import ProgressTracker

GOOD_REPLY = '{"harmful": true, "category": "harassment", "severity": 2, "target": "individual", "confidence": 0.9, "reason": "Test reply."}'


def make_df(count):
    # Fake cleaned file with `count` comments.
    return pd.DataFrame({"User ID": range(count), "username": "user", "processed_comments": "hello"})


def test_counter_is_correct_with_many_threads():
    tracker = ProgressTracker()
    tracker.start(100)
    threads = [threading.Thread(target=tracker.record_done) for _ in range(100)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()
    assert tracker.snapshot() == (100, 100)


def test_stop_sign_wakes_pause_early():
    tracker = ProgressTracker()
    tracker.request_stop()
    start = time.monotonic()
    tracker.pause(5)
    assert time.monotonic() - start < 1


def test_ctrl_c_keeps_finished_results(tmp_path):
    tracker = ProgressTracker()
    pipeline = ModerationPipeline(AIManager(FakeProvider([GOOD_REPLY] * 3)), delay_seconds=5)
    threading.Timer(0.2, tracker.request_stop).start()
    df = pipeline.process(make_df(3), tmp_path / "out.csv", tracker)
    assert len(df) == 1