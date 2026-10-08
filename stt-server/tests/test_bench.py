from pathlib import Path

from stt_server.bench import Sample, run, summarize
from tests.conftest import FakeTranscriber, make_wav


def test_summarize_pass_and_fail() -> None:
    fast = [Sample("a.wav", 4.0, 1200, "halo"), Sample("b.wav", 2.0, 1000, "dua")]
    ok, lines = summarize("large-v3-turbo", fast)
    assert ok
    assert "rtf_max=0.50" in lines
    assert lines[-1] == "result=PASS"
    ok, lines = summarize("large-v3-turbo", [Sample("c.wav", 2.0, 2500, "lambat")])
    assert not ok
    assert "rtf_max=1.25" in lines


def test_summarize_empty_fails() -> None:
    assert summarize("m", []) == (False, ["samples=0", "result=FAIL"])


def test_run_warms_up_then_measures(tmp_path: Path) -> None:
    sample = tmp_path / "id-halo.wav"
    sample.write_bytes(make_wav(3))
    fake = FakeTranscriber()
    results = run(fake, [sample], "SIPADI")
    assert fake.loaded
    assert len(fake.calls) == 2
    assert results == [Sample("id-halo.wav", 3.0, 120, "periksa modul login")]
