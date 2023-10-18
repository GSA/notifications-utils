import uuid

import pytest
from flask import g
from freezegun import freeze_time

from notifications_utils.celery import NotifyCelery
from notifications_utils.request_helper import TRACE_ID_HEADER


@pytest.fixture
def notify_celery(celery_app):
    celery = NotifyCelery()
    celery.init_app(celery_app)
    return celery


@pytest.fixture
def celery_task(notify_celery):
    @notify_celery.task(name=uuid.uuid4(), base=notify_celery.task_cls)
    def test_task(delivery_info=None):
        pass

    return test_task


@pytest.fixture
def async_task(celery_task):
    celery_task.push_request(delivery_info={"routing_key": "test-queue"})
    yield celery_task
    celery_task.pop_request()


@pytest.fixture
def request_id_task(celery_task):
    # Note that each header is a direct attribute of the
    # task context (aka "request").
    celery_task.push_request(notify_request_id="1234")
    yield celery_task
    celery_task.pop_request()


def test_success_should_log(mocker, celery_app, async_task):
    logger_mock = mocker.patch.object(celery_app.logger, "info")

    with freeze_time() as frozen:
        async_task()
        frozen.tick(5)

        async_task.on_success(retval=None, task_id=1234, args=[], kwargs={})

    logger_mock.assert_called_once_with(
        f"Celery task {async_task.name} (queue: test-queue) took 5.0000"
    )


def test_success_queue_when_applied_synchronously(mocker, celery_app, celery_task):
    logger_mock = mocker.patch.object(celery_app.logger, "info")

    with freeze_time() as frozen:
        celery_task()
        frozen.tick(5)

        celery_task.on_success(retval=None, task_id=1234, args=[], kwargs={})

    logger_mock.assert_called_once_with(
        f"Celery task {celery_task.name} (queue: none) took 5.0000"
    )


def test_failure_should_log(mocker, celery_app, async_task):
    logger_mock = mocker.patch.object(celery_app.logger, "error")

    async_task.on_failure(exc=Exception, task_id=1234, args=[], kwargs={}, einfo=None)

    logger_mock.assert_called_once_with(
        f"Celery task {async_task.name} (queue: test-queue) failed", exc_info=True
    )


def test_failure_queue_when_applied_synchronously(mocker, celery_app, celery_task):
    logger_mock = mocker.patch.object(celery_app.logger, "error")

    celery_task.on_failure(exc=Exception, task_id=1234, args=[], kwargs={}, einfo=None)

    logger_mock.assert_called_once_with(
        f"Celery task {celery_task.name} (queue: none) failed", exc_info=True
    )


def test_call_exports_request_id_from_headers(mocker, request_id_task):
    g = mocker.patch("notifications_utils.celery.g")
    request_id_task()
    assert g.request_id == "1234"


def test_call_copes_if_request_id_not_in_headers(mocker, celery_task):
    g = mocker.patch("notifications_utils.celery.g")
    celery_task()
    assert g.request_id is None


def test_send_task_injects_global_request_id_into_headers(
    mocker,
    notify_celery,
):
    super_apply = mocker.patch("celery.Celery.send_task")
    g.request_id = "1234"
    notify_celery.send_task("some-task")

    super_apply.assert_called_with(
        "some-task",  # name
        None,  # args
        None,  # kwargs
        headers={"notify_request_id": "1234"},  # other kwargs
    )


def test_send_task_injects_request_id_with_existing_headers(
    mocker,
    notify_celery,
):
    super_apply = mocker.patch("celery.Celery.send_task")
    g.request_id = "1234"

    notify_celery.send_task(
        "some-task",
        None,  # args
        None,  # kwargs
        headers={"something": "else"},  # other kwargs
    )

    super_apply.assert_called_with(
        "some-task",  # name
        None,  # args
        None,  # kwargs
        headers={"notify_request_id": "1234", "something": "else"},  # other kwargs
    )


def test_send_task_injects_request_id_with_none_headers(
    mocker,
    notify_celery,
):
    super_apply = mocker.patch("celery.Celery.send_task")
    g.request_id = "1234"

    notify_celery.send_task(
        "some-task",
        None,  # args
        None,  # kwargs
        headers=None,  # other kwargs (task retry set headers to "None")
    )

    super_apply.assert_called_with(
        "some-task",  # name
        None,  # args
        None,  # kwargs
        headers={"notify_request_id": "1234"},  # other kwargs
    )


def test_send_task_injects_id_from_request(
    mocker,
    notify_celery,
    celery_app,
):
    super_apply = mocker.patch("celery.Celery.send_task")
    request_id_header = TRACE_ID_HEADER
    request_headers = {request_id_header: "1234"}

    with celery_app.test_request_context(headers=request_headers):
        notify_celery.send_task("some-task")

    super_apply.assert_called_with(
        "some-task",  # name
        None,  # args
        None,  # kwargs
        headers={"notify_request_id": "1234"},  # other kwargs
    )
