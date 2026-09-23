import json
from pathlib import Path

from app.domain.calibration.provenance import (
    CalibrationProvenanceEvent,
    provenance_event_to_dict,
)


class FileCalibrationProvenanceStore:
    def __init__(self, path: str | Path):
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)

    def append(self, event: CalibrationProvenanceEvent) -> None:
        with self.path.open("a", encoding="utf-8") as file:
            file.write(
                json.dumps(provenance_event_to_dict(event), sort_keys=True) + "\n"
            )

    def load_all(self) -> list[CalibrationProvenanceEvent]:
        if not self.path.is_file():
            return []

        events = []
        for line in self.path.read_text(encoding="utf-8").splitlines():
            if line.strip():
                events.append(CalibrationProvenanceEvent(**json.loads(line)))
        return events
