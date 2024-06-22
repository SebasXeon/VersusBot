import schedule
import time 
import datetime
import json
import os

from versusbot.logger import logger


class Scheduler:
    def __init__(self) -> None:
        # Load tasks from json file
        with open('./data/schedule.json', 'r') as f:
            data = json.load(f)
            self.tasks = data['tasks']

    def start(self):
        schedule.every().minute.do(self.run_tasks)
        logger.info('Started scheduler')
        while True:
            schedule.run_pending()
            time.sleep(1)
    
    def run_tasks(self):
        now = datetime.datetime.now()
        for task in self.tasks:
            if now.weekday() in task['days'] and now.hour in task['hours']:
                if now.minute == task['minute']:
                    logger.info(f'Running task {task["name"]}')
                    os.system(f"python versusbot/versusbot.py {task['command']}")
                else:
                    logger.debug(f'Skipping task {task["name"]}')

