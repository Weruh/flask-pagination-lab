#!/usr/bin/env python3

import os

from config import create_app, db

env = os.getenv("FLASK_ENV", "dev")
app = create_app(env)

if __name__ == '__main__':
    app.run(port=5555)
