from pathlib import Path

from setlist_placeholder.main import create_app

app = create_app(Path("/tmp"))
