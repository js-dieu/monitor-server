import typing as t

import pytest

from monitor_server.domain.entities.sessions import MonitorSession
from monitor_server.infrastructure.orm.pageable import PageableStatement, PaginatedResponse
from monitor_server.infrastructure.persistence.exceptions import EntityAlreadyExists, EntityNotFound
from monitor_server.infrastructure.persistence.sessions import SessionRepository
from monitor_server.tests.sdk.persistence.generators import MonitorSessionGenerator


@pytest.mark.int()
class TestSessionSQLRepository:
    def test_it_creates_a_new_session_from_unknown_uid(
        self, session_sql_repo: SessionRepository, a_session: MonitorSession
    ):
        assert session_sql_repo.create(a_session)

    def test_it_raises_entity_already_exists_when_creating_twice_a_session_with_the_same_uid(
        self, session_sql_repo: SessionRepository, a_session: MonitorSession
    ):
        session_sql_repo.create(a_session)
        with pytest.raises(EntityAlreadyExists, match='abcd'):
            session_sql_repo.create(a_session)

    def test_it_returns_a_session_when_querying_a_known_uid(
        self, session_sql_repo: SessionRepository, a_session: MonitorSession
    ):
        session_sql_repo.create(a_session)
        assert session_sql_repo.get(a_session.uid)

    def test_it_raises_entity_not_found_when_querying_a_unknown_uid(
        self, session_sql_repo: SessionRepository, a_session: MonitorSession
    ):
        with pytest.raises(EntityNotFound, match=f'Session "{a_session.uid}" cannot be found'):
            session_sql_repo.get(a_session.uid)

    def test_update_on_tags_updates_the_entity(self, session_sql_repo: SessionRepository, a_session: MonitorSession):
        session_sql_repo.create(a_session)
        a_session.tags['in_test'] = True
        session_sql_repo.update(a_session)
        assert sorted(session_sql_repo.get(a_session.uid).tags) == sorted(a_session.tags)

    def test_it_lists_all_sessions_when_no_page_info_is_given(
        self,
        session_sql_repo: SessionRepository,
    ):
        session_generator: MonitorSessionGenerator = MonitorSessionGenerator()
        expected = []
        for session in (session_generator() for _ in range(30)):
            session_sql_repo.create(session)
            expected.append(session)
        assert session_sql_repo.list() == PaginatedResponse[t.List[MonitorSession]](
            data=sorted(expected, key=lambda m: m.uid), page_no=None, next_page=None
        )

    def test_it_lists_all_sessions_in_the_given_page(
        self,
        session_sql_repo: SessionRepository,
    ):
        session_generator: MonitorSessionGenerator = MonitorSessionGenerator()
        sessions = []
        for session in (session_generator() for _ in range(30)):
            session_sql_repo.create(session)
            sessions.append(session)
        sessions = sorted(sessions, key=lambda m: m.uid)[25:30]

        expected = PaginatedResponse[t.List[MonitorSession]](data=sessions, page_no=5, next_page=None)
        assert session_sql_repo.list(PageableStatement(page_no=5, page_size=5)) == expected

    def test_it_lists_all_sessions_in_the_given_page_and_provide_next_page_info(
        self,
        session_sql_repo: SessionRepository,
    ):
        session_generator: MonitorSessionGenerator = MonitorSessionGenerator()
        sessions = []
        for session in (session_generator() for _ in range(30)):
            session_sql_repo.create(session)
            sessions.append(session)
        expected = PaginatedResponse[t.List[MonitorSession]](
            data=list(sorted(sessions, key=lambda m: m.uid)[20:25]), page_no=4, next_page=5
        )
        assert session_sql_repo.list(PageableStatement(page_no=4, page_size=5)) == expected

    def test_it_lists_no_element_when_out_of_bounds(
        self,
        session_sql_repo: SessionRepository,
    ):
        session_generator: MonitorSessionGenerator = MonitorSessionGenerator()
        expected = []
        for session in (session_generator() for _ in range(30)):
            session_sql_repo.create(session)
            expected.append(session)
        assert session_sql_repo.list(PageableStatement(page_no=10, page_size=5)) == PaginatedResponse[
            t.List[MonitorSession]
        ](data=[], page_no=10, next_page=None)


class TestSessionInMemoryRepository:
    def test_it_creates_a_new_session_from_unknown_uid(
        self, session_in_mem_repo: SessionRepository, a_session: MonitorSession
    ):
        assert session_in_mem_repo.create(a_session)

    def test_it_raises_entity_already_exists_when_creating_twice_a_session_with_the_same_uid(
        self, session_in_mem_repo: SessionRepository, a_session: MonitorSession
    ):
        session_in_mem_repo.create(a_session)
        with pytest.raises(EntityAlreadyExists, match=f'Session "{a_session.uid}" already exists'):
            session_in_mem_repo.create(a_session)

    def test_it_returns_a_session_when_querying_a_known_uid(
        self, session_in_mem_repo: SessionRepository, a_session: MonitorSession
    ):
        session_in_mem_repo.create(a_session)
        assert session_in_mem_repo.get(a_session.uid).uid == a_session.uid

    def test_it_raises_entity_not_found_when_querying_a_unknown_uid(
        self, session_in_mem_repo: SessionRepository, a_session: MonitorSession
    ):
        with pytest.raises(EntityNotFound, match=f'Session "{a_session.uid}" cannot be found'):
            session_in_mem_repo.get(a_session.uid)

    def test_update_on_tags_updates_the_entity(self, session_in_mem_repo: SessionRepository, a_session: MonitorSession):
        session_in_mem_repo.create(a_session)
        a_session.tags['in_test'] = True
        session_in_mem_repo.update(a_session)
        assert sorted(session_in_mem_repo.get(a_session.uid).tags) == sorted(a_session.tags)

    def test_it_lists_all_sessions_when_no_page_info_is_given(
        self,
        session_in_mem_repo: SessionRepository,
    ):
        session_generator: MonitorSessionGenerator = MonitorSessionGenerator()
        expected = []
        for session in (session_generator() for _ in range(30)):
            session_in_mem_repo.create(session)
            expected.append(session)
        assert session_in_mem_repo.list() == PaginatedResponse[t.List[MonitorSession]](
            data=sorted(expected, key=lambda m: m.uid), page_no=None, next_page=None
        )

    def test_it_lists_all_sessions_in_the_given_page(
        self,
        session_in_mem_repo: SessionRepository,
    ):
        session_generator: MonitorSessionGenerator = MonitorSessionGenerator()
        sessions = []
        for session in (session_generator() for _ in range(30)):
            session_in_mem_repo.create(session)
            sessions.append(session)
        sessions = sorted(sessions, key=lambda m: m.uid)[25:30]

        expected = PaginatedResponse[t.List[MonitorSession]](data=sessions, page_no=5, next_page=None)
        assert session_in_mem_repo.list(PageableStatement(page_no=5, page_size=5)) == expected

    def test_it_lists_all_sessions_in_the_given_page_and_provide_next_page_info(
        self,
        session_in_mem_repo: SessionRepository,
    ):
        session_generator: MonitorSessionGenerator = MonitorSessionGenerator()
        sessions = []
        for session in (session_generator() for _ in range(30)):
            session_in_mem_repo.create(session)
            sessions.append(session)
        expected = PaginatedResponse[t.List[MonitorSession]](
            data=list(sorted(sessions, key=lambda m: m.uid)[20:25]), page_no=4, next_page=5
        )
        assert session_in_mem_repo.list(PageableStatement(page_no=4, page_size=5)) == expected

    def test_it_lists_no_element_when_out_of_bounds(
        self,
        session_in_mem_repo: SessionRepository,
    ):
        session_generator: MonitorSessionGenerator = MonitorSessionGenerator()
        expected = []
        for session in (session_generator() for _ in range(30)):
            session_in_mem_repo.create(session)
            expected.append(session)
        assert session_in_mem_repo.list(PageableStatement(page_no=10, page_size=5)) == PaginatedResponse[
            t.List[MonitorSession]
        ](data=[], page_no=10, next_page=None)
