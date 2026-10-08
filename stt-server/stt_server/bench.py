"""Ukur kecepatan STT (gerbang G0): RTF = waktu inferensi / durasi audio.

    uv run python -m stt_server.bench --samples tests/fixtures/id-*.wav [--model medium]
Lulus bila RTF maksimum ≤ 1,0 (lebih cepat dari realtime).
"""

from __future__ import annotations

import argparse
import statistics
import sys
from dataclasses import dataclass
from pathlib import Path

from stt_server.transcriber import Transcriber, WhisperTranscriber, parse_wav

RTF_LIMIT = 1.0


@dataclass(frozen=True)
class Sample:
    name: str
    duration_s: float
    infer_ms: int
    text: str

    @property
    def rtf(self) -> float:
        return (self.infer_ms / 1000) / self.duration_s if self.duration_s else float("inf")


def run(transcriber: Transcriber, paths: list[Path], prompt: str | None) -> list[Sample]:
    transcriber.load()
    samples = []
    for path in paths:
        pcm = parse_wav(path.read_bytes())
        transcriber.transcribe(pcm, prompt, "id")  # pemanasan: buang hasil pertama per berkas
        result = transcriber.transcribe(pcm, prompt, "id")
        samples.append(Sample(path.name, pcm.duration_s, result.infer_ms, result.text))
    return samples


def summarize(model: str, samples: list[Sample]) -> tuple[bool, list[str]]:
    if not samples:
        return False, ["samples=0", "result=FAIL"]
    rtfs = [sample.rtf for sample in samples]
    lines = [
        f"{s.name}: audio={s.duration_s:.2f}s infer={s.infer_ms}ms rtf={s.rtf:.2f} text={s.text!r}"
        for s in samples
    ]
    ok = max(rtfs) <= RTF_LIMIT
    lines += [
        f"model={model}",
        f"samples={len(samples)}",
        f"rtf_p50={statistics.median(rtfs):.2f}",
        f"rtf_max={max(rtfs):.2f}",
        f"result={'PASS' if ok else 'FAIL'}",
    ]
    return ok, lines


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="python -m stt_server.bench")
    parser.add_argument("--samples", nargs="+", type=Path, required=True)
    parser.add_argument("--model", default="large-v3-turbo")
    parser.add_argument("--compute-type", default="int8")
    parser.add_argument("--prompt", default=None, help="initial prompt kosakata proyek")
    args = parser.parse_args(argv)
    samples = run(WhisperTranscriber(args.model, args.compute_type), args.samples, args.prompt)
    ok, lines = summarize(args.model, samples)
    print("\n".join(lines))
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
