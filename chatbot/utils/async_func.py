import asyncio
import logging

from handlers.errors.send_exception import send_exception

import typing


def async_task(
        *coroutines: typing.Sequence[typing.Awaitable],
        loop: typing.Optional[asyncio.AbstractEventLoop] = None,
) -> typing.Union[asyncio.Task, typing.List[asyncio.Task]]:
    '''
    Wrapper to asyncio.Task with logging exception

    :param Sequence[Awaitable] *coroutines:
        Single object or list of objects that can be converted to asyncio.Task
    :param Optional[asyncio.AbstractEventLoop] loop:
        Custom loop in which tasks should run

    :raises: ValueError: If no coroutines were provided

    :returns:
        List of asyncio.Task if multiple coroutines were provided /
        Single asyncio.Task from single coroutine
    '''
    loop = asyncio.get_event_loop() or loop
    tasks = []
    for coro in coroutines:
        task = loop.create_task(coro, name=coro.__name__)
        task.add_done_callback(execute_async_task)
        tasks.append(task)
    return tasks if len(tasks) > 1 else tasks[0]


def execute_async_task(
        task: asyncio.Task
) -> typing.Any:
    '''
    Return task result and send exception details if one was raised

    :param asyncio.Task task: Task to be executed

    '''
    try:
        return task.result()
    except asyncio.CancelledError:
        logging.info(f'task {task.get_name()} was cancelled')
    except Exception as exc:
        asyncio.create_task(
            send_exception(
                exc, f'Exception in {task.get_name()}'
            )
        )
