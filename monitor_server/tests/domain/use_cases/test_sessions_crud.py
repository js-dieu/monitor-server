from datetime import UTC, datetime

import pytest

from monitor_server.domain.dto.sessions import CreateSession, NewSessionCreated
from monitor_server.domain.use_cases.exceptions import SessionAlreadyExists
from monitor_server.domain.use_cases.sessions.crud import AddSession
from monitor_server.infrastructure.persistence.sessions import SessionRepository


@pytest.mark.int()
class TestAddMachineDB:
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
