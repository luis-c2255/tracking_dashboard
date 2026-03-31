import json
from pathlib import Path
import pandas as pd
from datetime import datetime

SAVE_FILE = Path("saved_state.json")

def load_state():
    if SAVE_FILE.exists():
        data = json.loads(SAVE_FILE.read_text())
        df = pd.DataFrame(data["df"])
        start_date = datetime.strptime(data["start_date"], "%Y-%m-%d").date()
        return df, start_date
    return None, None

def save_state(df, start_date):
    data = {
        "df": df.to_dict(orient="list"),
        "start_date": start_date.strftime("%Y-%m-%d")
    }
    SAVE_FILE.write_text(json.dumps(data))
