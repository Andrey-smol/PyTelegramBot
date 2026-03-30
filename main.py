import sys

from controller.bot_controller import BotController
from exception.exception import MyException
from log.logger import OperationLogger
from repository.repository import Repository
from service.service import Service

if __name__ == '__main__':
    print('bot running')
    logger = OperationLogger()
    logger.log("Запуск телеграмм бота")
    controller = None
    try:
        BotController._check_telegram_token()
        service = Service(Repository())
        controller = BotController(service)
        controller.start_bot()
    except MyException as me:
        logger.log(me.message)
        print(me.message)
    except Exception as e:
        logger.log(f'Error: - {e}')
        print(e)
    finally:
        logger.flush_log()
        if controller:
            controller.stop_bot_()
    sys.exit(1)
