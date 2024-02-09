import pytest

from monitor_server.domain.entities.sessions import MonitorSession
from monitor_server.infrastructure.persistence.exceptions import EntityAlreadyExists, EntityNotFound
from monitor_server.infrastructure.persistence.sessions import SessionInMemRepository, SessionSQLRepository


@pytest.mark.int()
class TestSessionSQLRepository:
    def test_it_creates_a_new_session_from_unknown_uid(
        self, session_sql_repo: SessionSQLRepository, a_session: MonitorSession
    ):
        assert session_sql_repo.create(a_session)

    def test_it_raises_entity_already_exists_when_creating_twice_a_session_with_the_same_uid(
        self, session_sql_repo: SessionSQLRepository, a_session: MonitorSession
    ):
        session_sql_repo.create(a_session)
        with pytest.raises(EntityAlreadyExists, match='abcd'):
            session_sql_repo.create(a_session)

    def test_it_returns_a_session_when_querying_a_known_uid(
        self, session_sql_repo: SessionSQLRepository, a_session: MonitorSession
    ):
        session_sql_repo.create(a_session)
        assert session_sql_repo.get(a_session.uid)

    def test_it_raises_entity_not_found_when_querying_a_unknown_uid(
        self, session_sql_repo: SessionSQLRepository, a_session: MonitorSession
    ):
        with pytest.raises(EntityNotFound, match=f'Session "{a_session.uid}" cannot be found'):
            session_sql_repo.get(a_session.uid)

    def test_update_on_tags_updates_the_entity(self, session_sql_repo: SessionSQLRepository, a_session: MonitorSession):
        session_sql_repo.create(a_session)
        a_session.tags['in_test'] = True
        session_sql_repo.update(a_session)
        assert sorted(session_sql_repo.get(a_session.uid).tags) == sorted(a_session.tags)


class TestSessionInMemoryRepository:
    def test_it_creates_a_new_session_from_unknown_uid(
        self, session_in_mem_repo: SessionInMemRepository, a_session: MonitorSession
    ):
        assert session_in_mem_repo.create(a_session)

    def test_it_raises_entity_already_exists_when_creating_twice_a_session_with_the_same_uid(
        self, session_in_mem_repo: SessionInMemRepository, a_session: MonitorSession
    ):
        session_in_mem_repo.create(a_session)
        with pytest.raises(EntityAlreadyExists, match=f'Session "{a_session.uid}" already exists'):
            session_in_mem_repo.create(a_session)

    def test_it_returns_a_session_when_querying_a_known_uid(
        self, session_in_mem_repo: SessionInMemRepository, a_session: MonitorSession
    ):
        session_in_mem_repo.create(a_session)
        assert session_in_mem_repo.get(a_session.uid).uid == a_session.uid

    def test_it_raises_entity_not_found_when_querying_a_unknown_uid(
        self, session_in_mem_repo: SessionInMemRepository, a_session: MonitorSession
    ):
        with pytest.raises(EntityNotFound, match=f'Session "{a_session.uid}" cannot be found'):
            session_in_mem_repo.get(a_session.uid)

    def test_update_on_tags_updates_the_entity(
        self, session_in_mem_repo: SessionInMemRepository, a_session: MonitorSession
    ):
        session_in_mem_repo.create(a_session)
        a_session.tags['in_test'] = True
        session_in_mem_repo.update(a_session)
        assert sorted(session_in_mem_repo.get(a_session.uid).tags) == sorted(a_session.tags)
