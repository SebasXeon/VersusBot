#!/usr/bin/env python
# -*- coding: utf-8 -*-

# ---------------------------
# Import modules
# ---------------------------
from logger import logger
from config import Settings

import typer

# ---------------------------
# setup
# ---------------------------
app = typer.Typer()
settings = Settings()

# ---------------------------
# Commands
# ---------------------------
@app.command()
def versus():
    print(f"Versus")

@app.command()
def tournament():
    print(f"Tournament")

# ---------------------------
# run
# ---------------------------

if __name__ == "__main__":
    app()