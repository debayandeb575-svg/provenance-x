import json
def save_report(report,path):
    from pathlib import Path
    Path(path).parent.mkdir(parents=True,exist_ok=True)
    Path(path).write_text(json.dumps(report,indent=2),encoding="utf-8")
