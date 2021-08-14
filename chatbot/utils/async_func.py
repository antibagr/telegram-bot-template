import asyncio
import logging

from typing import Sequence, List, Awaitable, Optional, Any, Union


def async_task(*coroutines: Sequence[Awaitable], loop: Optional[asyncio.AbstractEventLoop] = None) -> Union[asyncio.Task, List[asyncio.Task]]:
    """
    Wrapper to asyncio.Task with logging exception

    :param Sequence[Awaitable] *coroutines: Single object or list of objects that can be converted to asyncio.Task
    :param Optional[asyncio.AbstractEventLoop] loop: Custom loop in which tasks should run

    :raises: ValueError: If no coroutines were provided

    :returns: List of asyncio.Task if multiple coroutines were provided / Single asyncio.Task from single coroutine
    """

    # if not len(coroutines):
    #     raise ValueError("create_task_with_logging got empty list of coroutines")
        # return None

    loop = asyncio.get_event_loop() or loop
    tasks = []
    for coro in coroutines:

        task = loop.create_task(coro, name=coro.__name__)
        task.add_done_callback(execute_async_task)
        tasks.append(task)

    # print(tasks)

    return tasks if len(tasks) > 1 else tasks[0]


def execute_async_task(task: asyncio.Task) -> Any:
    """
    Return task result and send exception details if one was raised

    :param asyncio.Task task: Task to be executed

    """

    from handlers.errors.send_exception import send_exception


    try:
        return task.result()
    except asyncio.CancelledError:

        logging.info(f"task {task.get_name()} was cancelled")
        return None

    # except Exception as e:
    #
    #     logging.exception(e, exc_info=True)
    #     asyncio.create_task(send_exception(e, f"Exception in {task.get_name()}"))


# async def send_pack_of_exceptions(ExceptionList: List[Exception], header: Optional[str] = "Exceptions List Received") -> None:
#     ExceptionStringify = "\n".join([GetExceptionDetails(e) for e in ExceptionList])
#     await bot.send_message(MAGIC_ID, tag(header, 'b'))
#     for err in safe_split_text(ExceptionStringify):
#
#         # sleep between 0 to 1 second
#         await asyncio.sleep(random.random())
#         await bot.send_message(MAGIC_ID, err)

# async def user_errors_handler(exception: Exception, chat_id: int, verbose_message: str = None, header: str = None, do_log: bool = True) -> None:
#
#     if do_log:
#
#         # For some reason the traceback is losing when we pass exception
#         # to errors_handler. So we need to log it now to save exc information
#
#         # traceback_str = ''.join(traceback.format_tb(exception.__traceback__))
#         # print(traceback_str)
#         logging.exception(exception, exc_info=True)
#
#     await asyncio.gather(
#         bot.send_message(chat_id, verbose_message or msg.err.err),
#         errors_handler("User errors handler" or header, exception, do_log = False)
#     )
