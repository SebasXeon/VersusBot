import schedule, time, datetime, json
from logger import logger


class scheduler:
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
                    print("a")
                    logger.info(f'Running task {task["name"]}')
                else:
                    print("e")