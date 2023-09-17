from datetime import datetime, timedelta
from loguru import logger
class fakeclock():
    def __init__(self,start=datetime.now(),tick_step=15*60) -> None:
        self.clock = start
        self.tick_step = tick_step

    def tick(self):
        self.clock = self.clock + timedelta(seconds=self.tick_step)

    def now(self):
        return self.clock.__format__('%Y-%m-%d %H:%M:%S')


if __name__ == "__main__":
    f1 = fakeclock()
    logger.info()