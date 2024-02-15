from datetime import UTC, datetime

import pytest

from monitor_server.domain.dto.abc import PageableRequest
from monitor_server.domain.dto.sessions import CreateSession, NewSessionCreated, SessionListing
from monitor_server.domain.use_cases.exceptions import SessionAlreadyExists
from monitor_server.domain.use_cases.sessions.crud import AddSession, ListSession
from monitor_server.infrastructure.persistence.sessions import SessionRepository
from monitor_server.tests.sdk.persistence.generators import MonitorSessionGenerator


@pytest.mark.int()
class TestAddSessionDB:
    def test_it_return_ok_when_the_session_is_valid(self, session_sql_repo: SessionRepository):
        use_case = AddSession(session_sql_repo)
        assert use_case.execute(
            CreateSession(
                uid='abcd',
                scm_revision='scm_revision',
                start_date=datetime(2024, 1, 31, 18, 24, 54, 123456, tzinfo=UTC),
                tags={'description': 'a description', 'extras': 'information'},
            )
        ) == NewSessionCreated(uid='abcd')

    def test_it_raises_session_already_exists_when_the_session_already_exists(
        self, session_sql_repo: SessionRepository
    ):
        use_case = AddSession(session_sql_repo)
        use_case.execute(
            CreateSession(
                uid='abcd',
                scm_revision='scm_revision',
                start_date=datetime(2024, 1, 31, 18, 24, 54, 123456, tzinfo=UTC),
                tags={'description': 'a description', 'extras': 'information'},
            )
        )
        with pytest.raises(SessionAlreadyExists, match='Session "abcd" already exists'):
            use_case.execute(
                CreateSession(
                    uid='abcd',
                    scm_revision='scm_revision',
                    start_date=datetime(2024, 1, 31, 18, 24, 54, 123456, tzinfo=UTC),
                    tags={'description': 'a description', 'extras': 'information'},
                )
            )


class TestAddSessionInMem:
    def test_it_return_ok_when_the_session_is_valid(self, session_in_mem_repo: SessionRepository):
        use_case = AddSession(session_in_mem_repo)
        assert use_case.execute(
            CreateSession(
                uid='abcd',
                scm_revision='scm_revision',
                start_date=datetime(2024, 1, 31, 18, 24, 54, 123456, tzinfo=UTC),
                tags={'description': 'a description', 'extras': 'information'},
            )
        ) == NewSessionCreated(uid='abcd')

    def test_it_raises_session_already_exists_when_the_session_already_exists(
        self, session_in_mem_repo: SessionRepository
    ):
        use_case = AddSession(session_in_mem_repo)
        use_case.execute(
            CreateSession(
                uid='abcd',
                scm_revision='scm_revision',
                start_date=datetime(2024, 1, 31, 18, 24, 54, 123456, tzinfo=UTC),
                tags={'description': 'a description', 'extras': 'information'},
            )
        )
        with pytest.raises(SessionAlreadyExists, match='Session "abcd" already exists'):
            use_case.execute(
                CreateSession(
                    uid='abcd',
                    scm_revision='scm_revision',
                    start_date=datetime(2024, 1, 31, 18, 24, 54, 123456, tzinfo=UTC),
                    tags={'description': 'a description', 'extras': 'information'},
                )
            )


@pytest.mark.int()
class TestListSessionsDB:
    def setup_method(self) -> None:
        session_generator: MonitorSessionGenerator = MonitorSessionGenerator()
        self.sessions = []
        for session in (session_generator() for _ in range(30)):
            self.sessions.append(session)
        self.sessions = sorted(self.sessions, key=lambda m: m.uid)

    def test_it_returns_all_elements_when_no_page_info(self, session_sql_repo: SessionRepository):
        use_case = ListSession(session_sql_repo)
        for session in self.sessions:
            session_sql_repo.create(session)
        result = use_case.execute(PageableRequest())
        assert result == SessionListing(data=self.sessions, next_page=None)

    def test_it_returns_no_elements_when_out_of_bounds(self, session_sql_repo: SessionRepository):
        use_case = ListSession(session_sql_repo)
        for session in self.sessions:
            session_sql_repo.create(session)
        result = use_case.execute(PageableRequest(page_no=15, page_size=5))
        assert result == SessionListing(data=[], next_page=None)

    def test_it_returns_elements_with_next_page_when_listing_is_not_complete(self, session_sql_repo: SessionRepository):
        use_case = ListSession(session_sql_repo)
        for session in self.sessions:
            session_sql_repo.create(session)
        result = use_case.execute(PageableRequest(page_no=1, page_size=5))
        assert result == SessionListing(data=self.sessions[5:10], next_page=2)


class TestListSessionInMem:
    def setup_method(self) -> None:
        session_generator: MonitorSessionGenerator = MonitorSessionGenerator()
        self.sessions = []
        for session in (session_generator() for _ in range(30)):
            self.sessions.append(session)
        self.sessions = sorted(self.sessions, key=lambda m: m.uid)

    def test_it_returns_all_elements_when_no_page_info(self, session_in_mem_repo: SessionRepository):
        use_case = ListSession(session_in_mem_repo)
        for session in self.sessions:
            session_in_mem_repo.create(session)
        result = use_case.execute(PageableRequest())
        assert result == SessionListing(data=self.sessions, next_page=None)

    def test_it_returns_no_elements_when_out_of_bounds(self, session_in_mem_repo: SessionRepository):
        use_case = ListSession(session_in_mem_repo)
        for session in self.sessions:
            session_in_mem_repo.create(session)
        result = use_case.execute(PageableRequest(page_no=15, page_size=5))
        assert result == SessionListing(data=[], next_page=None)

    def test_it_returns_elements_with_next_page_when_listing_is_not_complete(
        self, session_in_mem_repo: SessionRepository
    ):
        use_case = ListSession(session_in_mem_repo)
        for session in self.sessions:
            session_in_mem_repo.create(session)
        result = use_case.execute(PageableRequest(page_no=1, page_size=5))
        assert result == SessionListing(data=self.sessions[5:10], next_page=2)
