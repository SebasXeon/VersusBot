#!/usr/bin/env python
# -*- coding: utf-8 -*-

# ---------------------------
# Import modules
# ---------------------------
from logger import logger
from config import Settings
from scheduler import scheduler

# ---------------------------
# settings
# ---------------------------
settings = Settings()

# ---------------------------
# main
# ---------------------------
def main():
    schedule = scheduler()
    schedule.start()

# ---------------------------
# run
# ---------------------------

if __name__ == "__main__":
    logger.info('Starting VersusBot')
    main()