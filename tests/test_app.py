from pathlib import Path

from streamlit.testing.v1 import AppTest

APP = str(Path(__file__).resolve().parents[1] / "app.py")


def test_app_runs_with_samples():
    at = AppTest.from_file(APP, default_timeout=120).run()
    assert not at.exception and len(at.info) == 1       # prompt to paste texts
    at.sidebar.button[0].click().run()
    assert not at.exception
    assert len(at.tabs) == 5 and len(at.dataframe) >= 2
