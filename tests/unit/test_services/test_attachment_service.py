import pytest
from uuid import uuid4
from unittest.mock import MagicMock, patch

from app.services.attachment_service import (
    upload_attachment, get_attachment, get_attachments_by_task, delete_attachment
)
from app.core.exceptions import (
    AttachmentNotFoundException, AttachmentLimitExceededException,
    AttachmentFileTypeInvalidException
)
from app.schemas.response.attachment_response import AttachmentResponse


def test_upload_attachment_success(db_session, test_task, test_user):
    mock_file = MagicMock()
    mock_file.filename = "test.jpg"
    mock_file.file.read.return_value = b"test file content"

    with patch("app.repositories.attachment.count_attachments_by_task", return_value=0):
        with patch("app.services.attachment_service.validate_file"):
            with patch("app.services.attachment_service.save_file", return_value="/uploads/test_uuid.jpg"):
                with patch("app.repositories.attachment.create_attachment") as mock_create:
                    mock_create.return_value = MagicMock(
                        id=uuid4(),
                        file_name="test.jpg",
                        file_url="/uploads/test_uuid.jpg",
                        task_id=test_task.id,
                        author_id=test_user.id,
                    )

                    result = upload_attachment(db_session, test_task.id, mock_file, test_user.id)

    assert result is not None
    assert isinstance(result, AttachmentResponse)
    assert result.file_name == "test.jpg"
    assert result.file_url == "/uploads/test_uuid.jpg"
    assert str(result.task_id) == str(test_task.id)
    assert str(result.author_id) == str(test_user.id)


def test_upload_attachment_limit_exceeded(db_session, test_task, test_user):
    mock_file = MagicMock()
    mock_file.filename = "test.jpg"

    with patch("app.repositories.attachment.count_attachments_by_task", return_value=3):  # Max limit = 3
        with pytest.raises(AttachmentLimitExceededException):
            upload_attachment(db_session, test_task.id, mock_file, test_user.id)


def test_upload_attachment_invalid_file_type(db_session, test_task, test_user):
    mock_file = MagicMock()
    mock_file.filename = "test.exe"  # Executable not allowed

    with patch("app.repositories.attachment.count_attachments_by_task", return_value=0):
        with patch("app.services.attachment_service.validate_file", side_effect=AttachmentFileTypeInvalidException):
            with pytest.raises(AttachmentFileTypeInvalidException):
                upload_attachment(db_session, test_task.id, mock_file, test_user.id)


def test_get_attachment_success(db_session, test_attachment):
    with patch("app.repositories.attachment.get_attachment_by_id") as mock_get:
        mock_get.return_value = test_attachment

        result = get_attachment(db_session, test_attachment.id)

    assert result is not None
    assert isinstance(result, AttachmentResponse)
    assert str(result.id) == str(test_attachment.id)
    assert result.file_name == test_attachment.file_name
    assert result.file_url == test_attachment.file_url
    assert str(result.task_id) == str(test_attachment.task_id)
    assert str(result.author_id) == str(test_attachment.author_id)


def test_get_attachment_not_found(db_session):
    non_existent_id = uuid4()

    with patch("app.repositories.attachment.get_attachment_by_id", return_value=None):
        with pytest.raises(AttachmentNotFoundException):
            get_attachment(db_session, non_existent_id)


def test_get_attachments_by_task(db_session, test_task, test_attachment):
    mock_attachments = [test_attachment]

    with patch("app.repositories.attachment.get_attachments_by_task") as mock_get:
        mock_get.return_value = mock_attachments

        result = get_attachments_by_task(db_session, test_task.id)

    assert result is not None
    assert isinstance(result, list)
    assert len(result) == 1
    assert isinstance(result[0], AttachmentResponse)
    assert str(result[0].id) == str(test_attachment.id)
    assert str(result[0].task_id) == str(test_task.id)


def test_delete_attachment_success(db_session, test_attachment):
    with patch("app.repositories.attachment.get_attachment_by_id") as mock_get:
        mock_get.return_value = test_attachment

        with patch("app.repositories.attachment.delete_attachment", return_value=True):
            with patch("os.remove"):
                result = delete_attachment(db_session, test_attachment.id)

    assert result is True
