import pytest
from uuid import uuid4

from app.models.comment import Comment
from tests.test_models import TestComment

def test_comment_creation():
    comment_id = uuid4()
    task_id = uuid4()
    author_id = uuid4()
    
    comment = Comment(
        id=comment_id,
        content="Test Comment Content",
        task_id=task_id,
        author_id=author_id
    )
    
    assert comment.id == comment_id
    assert comment.content == "Test Comment Content"
    assert comment.task_id == task_id
    assert comment.author_id == author_id

def test_comment_in_database(db_session, test_task, test_user):
    comment_id = str(uuid4())
    comment = TestComment(
        id=comment_id,
        content="Database Test Comment",
        task_id=test_task.id,
        author_id=test_user.id
    )
    
    db_session.add(comment)
    db_session.commit()
    
    saved_comment = db_session.query(TestComment).filter(TestComment.id == comment_id).first()
    
    assert saved_comment is not None
    assert saved_comment.id == comment_id
    assert saved_comment.content == "Database Test Comment"
    assert saved_comment.task_id == test_task.id
    assert saved_comment.author_id == test_user.id
