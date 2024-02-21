import datetime
import uuid

import pytest

from monitor_server.domain.models.sessions import MonitorSession


class TestSessionEntity:
    def setup_method(self):
        self.ref_session = MonitorSession(
            uid=uuid.uuid4(),
            scm_revision='e55dd4c2cee55e22c1e7388bf889b',
            start_date=datetime.datetime(2024, 1, 31, 0, 20, 56, 1345, tzinfo=datetime.UTC),
            tags={'description': 'a test session'},
        )

    def test_equality_returns_false_when_comparing_with_a_non_session_object(self):
        result = self.ref_session == object()
        assert not result

    def test_equality_returns_true_when_comparing_two_objects_with_same_value(self):
        other_session = MonitorSession.from_dict(self.ref_session.to_dict())
        assert self.ref_session == other_session

    @pytest.mark.parametrize('field_name', list(set(MonitorSession.model_fields) - {'tags'}))
    def test_equality_returns_false_when_two_objects_differs_only_by(self, field_name):
        data = self.ref_session.to_dict()
        match field_name:
            case 'start_date':
                data[field_name] = data[field_name] + datetime.timedelta(seconds=2)
            case 'uid':
                data[field_name] = uuid.uuid4()
            case _:
                data[field_name] = data[field_name] * 2
        other_session = MonitorSession.from_dict(data)
        result = bool(self.ref_session == other_session)
        assert not result

    def test_equality_returns_false_when_two_session_only_differs_by_their_description(self):
        data = self.ref_session.to_dict()
        data['tags']['description'] = 'Another description'
        other_session = MonitorSession.from_dict(data)
        result = bool(self.ref_session == other_session)
        assert not result
