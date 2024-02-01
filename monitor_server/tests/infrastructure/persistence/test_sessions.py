import datetime

import pytest

from monitor_server.domain.entities.sessions import Session as SessionEntity
from monitor_server.infrastructure.persistence.exceptions import EntityAlreadyExists, EntityNotFound
from monitor_server.infrastructure.persistence.sessions import SessionInMemRepository, SessionSQLRepository


@pytest.mark.int()
class TestSessionSQLRepository:
    def setup_method(self):
        self.a_test_session = SessionEntity(
            uid='abcd',
            scm_revision='scm_revision',
            start_date=datetime.datetime(2024, 1, 31, 18, 24, 54, 123456, tzinfo=datetime.UTC),
            tags={'description': 'a description', 'extras': 'information'},
        )

    def test_it_creates_a_new_session_from_unknown_uid(self, session_sql_repo: SessionSQLRepository):
        assert session_sql_repo.create(self.a_test_session)

    def test_it_raises_entity_already_exists_when_creating_twice_a_session_with_the_same_uid(
        self, session_sql_repo: SessionSQLRepository
    ):
        session_sql_repo.create(self.a_test_session)
        with pytest.raises(EntityAlreadyExists, match='abcd'):
            session_sql_repo.create(self.a_test_session)

    def test_it_returns_a_session_when_querying_a_known_uid(self, session_sql_repo: SessionSQLRepository):
        session_sql_repo.create(self.a_test_session)
        assert session_sql_repo.get(self.a_test_session.uid).uid == self.a_test_session.uid

    def test_it_raises_entity_not_found_when_querying_a_unknown_uid(self, session_sql_repo: SessionSQLRepository):
        with pytest.raises(EntityNotFound, match=self.a_test_session.uid):
            session_sql_repo.get(self.a_test_session.uid)

    def test_update_on_tags_updates_the_entity(self, session_sql_repo: SessionSQLRepository):
        session_sql_repo.create(self.a_test_session)
        self.a_test_session.tags['in_test'] = True
        session_sql_repo.update(self.a_test_session)
        assert sorted(session_sql_repo.get(self.a_test_session.uid).tags) == ['description', 'extras', 'in_test']


class TestSessionInMemoryRepository:
    def setup_method(self):
        self.a_test_session = SessionEntity(
            uid='abcd',
            scm_revision='scm_revision',
            start_date=datetime.datetime(2024, 1, 31, 18, 24, 54, 123456, tzinfo=datetime.UTC),
            tags={'description': 'a description', 'extras': 'information'},
        )

    def test_it_creates_a_new_session_from_unknown_uid(self, session_in_mem_repo: SessionInMemRepository):
        assert session_in_mem_repo.create(self.a_test_session)

    def test_it_raises_entity_already_exists_when_creating_twice_a_session_with_the_same_uid(
        self, session_in_mem_repo: SessionInMemRepository
    ):
        session_in_mem_repo.create(self.a_test_session)
        with pytest.raises(EntityAlreadyExists, match='abcd'):
            session_in_mem_repo.create(self.a_test_session)

    def test_it_returns_a_session_when_querying_a_known_uid(self, session_in_mem_repo: SessionInMemRepository):
        session_in_mem_repo.create(self.a_test_session)
        assert session_in_mem_repo.get(self.a_test_session.uid).uid == self.a_test_session.uid

    def test_it_raises_entity_not_found_when_querying_a_unknown_uid(self, session_in_mem_repo: SessionInMemRepository):
        with pytest.raises(EntityNotFound, match=self.a_test_session.uid):
            session_in_mem_repo.get(self.a_test_session.uid)

    def test_update_on_tags_updates_the_entity(self, session_in_mem_repo: SessionInMemRepository):
        session_in_mem_repo.create(self.a_test_session)
        self.a_test_session.tags['in_test'] = True
        session_in_mem_repo.update(self.a_test_session)
        assert sorted(session_in_mem_repo.get(self.a_test_session.uid).tags) == ['description', 'extras', 'in_test']
