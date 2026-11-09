import copy
import time
import pytest

from adega98.backend.core import utils
from adega98.backend.models.logs_model import Logs
from adega98.backend.core.exceptions import Adega98Exceptions


@pytest.fixture
def logs_instance() -> Logs:
    exc: Adega98Exceptions
    try: raise Adega98Exceptions(
        cause="testing_logs_model", 
        message="testing Logs model",
        log_level="CRITICAL",
        content={"user_id": 1},
        status_code=404
    )
    except Adega98Exceptions as e: exc = e

    return Logs(
        level="CRITICAL",
        logger_name=__name__,
        message="testing Logs model",
        timestamp=utils.get_datetime(time.time()).isoformat(),
        user_id=1,
        http_method="POST",
        http_path="/product/update",
        http_code=404,
        exc=exc
    )


@pytest.mark.asyncio
async def test_logs_model_add(restart_database, logs_instance):
    assert await Logs.count() == 0

    logs = await logs_instance.add()

    assert await Logs.count() == 1
    assert logs.log_id == 1


@pytest.mark.asyncio
async def test_logs_model_get_by_id(restart_database, logs_instance: Logs):
    log = await Logs.get_by_id(1)

    assert log is None

    await logs_instance.add()

    log = await Logs.get_by_id(1)

    assert log.logger_name == __name__


@pytest.mark.asyncio
async def test_logs_model_get_by_user(restart_database, logs_instance: Logs):
    logs = await Logs.get_by_user(1)

    assert len(logs) == 0

    await logs_instance.add()

    logs = await Logs.get_by_user(1)
    
    assert len(logs) == 1
    assert logs[0].logger_name == __name__


@pytest.mark.asyncio
async def test_logs_model_get_all(restart_database, logs_instance: Logs):
    logs = await Logs.get_all()

    assert len(logs) == 0

    for i in range(10):
        await copy.deepcopy(logs_instance).add()
    
    logs = await Logs.get_all()

    assert len(logs) == 10


@pytest.mark.asyncio
async def test_logs_model_count(restart_database, logs_instance: Logs):
    assert await Logs.count() == 0

    for i in range(10):
        await copy.deepcopy(logs_instance).add()

    assert await Logs.count() == 10