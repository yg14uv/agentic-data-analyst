import json
from datetime import datetime, timezone
from pathlib import Path
from uuid import uuid4


LOG_PATH = Path("backend/logs/agent_runs.jsonl")


def log_agent_run(data: dict):
    LOG_PATH.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    log_record = {
        "run_id": str(uuid4()),
        "timestamp": datetime.now(
            timezone.utc
        ).isoformat(),
        **data
    }

    with open(
        LOG_PATH,
        "a",
        encoding="utf-8"
    ) as file:
        file.write(
            json.dumps(
                log_record,
                ensure_ascii=False
            )
            + "\n"
        )

    return log_record