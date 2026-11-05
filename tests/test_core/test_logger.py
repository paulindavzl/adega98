import os
import pytest
import logging

from adega98.backend.core.logger import Logger
from adega98.backend.models.logs_model import Logs
from adega98.backend.core.constants import LOGS_PATH
from adega98.backend.core.exceptions import Adega98Exceptions


DEBUG = "testing"
INFO = "test log info"
WARNING = "test log warning"
ERROR = "test log error"
CRITICAL = "test log critical"


@pytest.fixture
def logs_path() -> str:
    return os.path.join(LOGS_PATH, "tests")


@pytest.fixture
def log_path(logs_path: str) -> str:
    return os.path.join(logs_path, "adega98.log")


def test_logger(logs_path: str, log_path: str, delete_logs):
    assert not os.path.exists(log_path)

    logger = Logger(__name__, logging.DEBUG)
    logger.debug(DEBUG)
    logger.info(INFO)
    logger.warning(WARNING)
    logger.error(ERROR)
    logger.critical(CRITICAL)
    logger.info("finish this tests")

    assert os.path.exists(logs_path)
    assert os.path.exists(log_path)

    logs: list
    with open(log_path, "r") as file:
        logs = file.readlines()

    assert len(logs) == 6
    assert DEBUG in logs[0]
    assert INFO in logs[1]
    assert WARNING in logs[2]
    assert ERROR in logs[3]
    assert CRITICAL in logs[4]
    assert "finish this tests" in logs[5]


@pytest.mark.asyncio
async def test_logger_new_exception_logger_info_warning(log_path: str, restart_database, delete_logs):
    exc_info = Adega98Exceptions(
        cause="testing_log_info_error",
        message=INFO,
        status_code=500,
        log_level="INFO"
    )
    exc_warn = Adega98Exceptions(
        cause="testing_log_warning_error",
        message=WARNING,
        status_code=500,
        log_level="WARNING"
    )

    logger = Logger(__name__)
    await logger.new_exception_log(exc_info)
    await logger.new_exception_log(exc_warn)

    logs_line: list
    with open(log_path, "r") as file:
        logs_line = file.readlines()
    
    assert INFO in logs_line[0]
    assert WARNING in logs_line[2]
    assert await Logs.count() == 0


@pytest.mark.asyncio
async def test_logger_new_exception_logger_error_critical(log_path: str, restart_database, delete_logs):
    exc_error = Adega98Exceptions(
        cause="testing_log_error_error",
        message=ERROR,
        status_code=500,
        log_level="ERROR"
    )
    exc_critical = Adega98Exceptions(
        cause="testing_log_critical_error",
        message=CRITICAL,
        status_code=500,
        log_level="CRITICAL"
    )

    logger = Logger(__name__)
    error_log = await logger.new_exception_log(exc_error)
    critical_log = await logger.new_exception_log(exc_critical)

    logs_line: list
    with open(log_path, "r") as file:
        logs_line = file.readlines()

    assert await Logs.count() == 2
    assert error_log.message == ERROR
    assert error_log.level == "ERROR"
    assert critical_log.message == CRITICAL
    assert critical_log.level == "CRITICAL"
    assert len(logs_line) == 4
