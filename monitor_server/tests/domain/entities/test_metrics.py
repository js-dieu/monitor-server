import datetime
import pathlib
import uuid

import pytest

from monitor_server.domain.entities.metrics import Metric


class TestMetricEntity:
    def setup_method(self):
        self.a_metric = Metric(
            session_id='session_id',
            node_id='node_id',
            item_start_time=datetime.datetime.now(tz=datetime.UTC),
            item_path='item.path',
            item='item',
            variant='variant',
            item_path_fs=pathlib.Path('item/path.py'),
            item_type='function',
            component='component',
            wall_time=1.314,
            user_time=0.8766,
            kernel_time=0.254,
            memory_usage=56,
            cpu_usage=1.24,
        )

    def test_equality_returns_false_when_comparing_with_a_non_metric_object(self):
        result = self.a_metric == object()
        assert not result

    def test_equality_returns_true_when_comparing_two_objects_with_same_value(self):
        other_metric = Metric.from_dict(self.a_metric.as_dict())
        assert self.a_metric == other_metric

    @pytest.mark.parametrize('field_name', Metric.model_fields)
    def test_equality_returns_false_when_two_objects_differs_only_by(self, field_name):
        data = self.a_metric.as_dict()
        match field_name:
            case 'uid':
                data[field_name] = uuid.uuid4()
            case 'item_path_fs':
                data[field_name] = pathlib.Path('item/path.other.py')
            case 'item_type':
                data[field_name] = 'package'
            case 'item_start_time':
                data[field_name] = data[field_name] + datetime.timedelta(seconds=1)
            case _:
                data[field_name] = data[field_name] * 2
        other_machine = Metric.from_dict(data)
        result = bool(self.a_metric == other_machine)
        assert not result
