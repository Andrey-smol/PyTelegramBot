from controller.bot_controller import BotController
from exception.exception import MyException
from log.logger import OperationLogger
from repository.repository import Repository
from service.service import Service

if __name__ == '__main__':
    print('bot running')
    logger = OperationLogger()
    logger.log("Запуск телеграмм бота")
    repository = Repository()
    service = Service(repository)
    controller = BotController(service)
    try:
        controller.start_bot()
    except MyException as me:
        logger.log(me.message)
        print(me.message)
    except BaseException as e:
        logger.log(f'Исключение BaseException - {e}')
        print(e)
    finally:
        logger.flush_log()
        controller.stop_bot_()