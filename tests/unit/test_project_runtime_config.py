import json
from pathlib import Path


def test_project_runtime_uses_common_configuration_without_dev_prod_duplication():
    project = json.loads(Path("project.json").read_text(encoding="utf-8"))

    runtime = project["runtime"]

    assert "common" in runtime
    assert runtime["dev"] == {}
    assert runtime["prod"] == {}


def test_project_runtime_has_deterministic_downstream_urls():
    project = json.loads(Path("project.json").read_text(encoding="utf-8"))

    runtime_common = project["runtime"]["common"]

    assert runtime_common["AGE_DECISION_CORE_URL"] == "http://age-decision-core:8000"
    assert (
        runtime_common["AGE_DECISION_ANTISPOOF_URL"]
        == "http://age-decision-antispoof:8001"
    )


def test_project_runtime_does_not_allow_raw_downstream_exposure_flags():
    project = json.loads(Path("project.json").read_text(encoding="utf-8"))

    runtime_text = json.dumps(project["runtime"])

    assert "EXPOSE_RAW_DOWNSTREAM_RESPONSES" not in runtime_text
    assert "RAW_DOWNSTREAM_RESPONSES" not in runtime_text


def test_project_runtime_does_not_include_downstream_model_or_threshold_config():
    project = json.loads(Path("project.json").read_text(encoding="utf-8"))

    runtime_text = json.dumps(project["runtime"])

    assert "AGE_THRESHOLD" not in runtime_text
    assert "SPOOF_THRESHOLD" not in runtime_text
    assert "MODEL_PATH" not in runtime_text
    assert "AGE_MODEL_PATH" not in runtime_text
    assert "ANTISPOOF_MODEL_PATH" not in runtime_text
