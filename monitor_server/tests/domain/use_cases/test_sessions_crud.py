from datetime import UTC, datetime

import pytest

from monitor_server.domain.models.abc import PageableRequest
from monitor_server.domain.models.sessions import MonitorSession, NewSessionCreated, SessionListing
from monitor_server.domain.use_cases.exceptions import SessionAlreadyExists
from monitor_server.domain.use_cases.sessions.crud import AddSession, ListSession
from monitor_server.infrastructure.persistence.sessions import SessionRepository
from monitor_server.tests.sdk.persistence.generators import MonitorSessionGenerator


class TestAddSession:
    def test_it_return_ok_when_the_session_is_valid(self, session_repository: SessionRepository):
        use_case = AddSession(session_repository)
        a_valid_session = MonitorSession(
            scm_revision='scm_revision',
            start_date=datetime(2024, 1, 31, 18, 24, 54, 123456, tzinfo=UTC),
            tags={'description': 'a description', 'extras': 'information'},
        )
        assert use_case.execute(a_valid_session) == NewSessionCreated(uid=a_valid_session.uid.hex)

    def test_it_raises_session_already_exists_when_adding_twice_the_same_session(
        self, session_repository: SessionRepository
    ):
        use_case = AddSession(session_repository)
        a_session = MonitorSession(
            scm_revision='scm_revision',
            start_date=datetime(2024, 1, 31, 18, 24, 54, 123456, tzinfo=UTC),
            tags={'description': 'a description', 'extras': 'information'},
        )
        use_case.execute(a_session)
        with pytest.raises(SessionAlreadyExists, match=f'Session "{a_session.uid.hex}" already exists'):
            use_case.execute(a_session)


class TestListSessions:
    def setup_method(self) -> None:
        session_generator: MonitorSessionGenerator = MonitorSessionGenerator()
        self.sessions = []
        for session in (session_generator() for _ in range(30)):
            self.sessions.append(session)
        self.sessions = sorted(self.sessions, key=lambda m: m.uid)

    def test_it_returns_all_elements_when_no_page_info(self, session_repository: SessionRepository):
        use_case = ListSession(session_repository)
        for session in self.sessions:
            session_repository.create(session)
        result = use_case.execute(PageableRequest())
        assert result == SessionListing(data=self.sessions, next_page=None)

    def test_it_returns_no_elements_when_out_of_bounds(self, session_repository: SessionRepository):
        use_case = ListSession(session_repository)
        for session in self.sessions:
            session_repository.create(session)
        result = use_case.execute(PageableRequest(page_no=15, page_size=5))
        assert result == SessionListing(data=[], next_page=None)

    def test_it_returns_elements_with_next_page_when_listing_is_not_complete(
        self, session_repository: SessionRepository
    ):
        use_case = ListSession(session_repository)
        for session in self.sessions:
            session_repository.create(session)
        result = use_case.execute(PageableRequest(page_no=1, page_size=5))
        assert result == SessionListing(data=self.sessions[5:10], next_page=2)
