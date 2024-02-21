import pytest

from monitor_server.domain.models.machines import Machine


class TestMachineEntity:
    def setup_method(self):
        self.ref_machine = Machine(
            cpu_frequency=1024,
            cpu_vendor='cpu_vendor',
            cpu_count=32,
            cpu_type='cpu_type',
            total_ram=2048,
            hostname='hostname',
            machine_type='type',
            machine_arch='arch',
            system_info='system info',
            python_info='python info',
        )

    def test_equality_returns_false_when_comparing_with_a_non_machine_object(self):
        result = self.ref_machine == object()
        assert not result

    def test_equality_returns_true_when_comparing_two_objects_with_same_value(self):
        other_machine = Machine.from_dict(self.ref_machine.to_dict())
        assert self.ref_machine == other_machine

    @pytest.mark.parametrize('field_name', list(set(Machine.model_fields) - {'uid'}))
    def test_equality_returns_false_when_two_objects_differs_only_by(self, field_name):
        data = self.ref_machine.to_dict()
        data[field_name] = data[field_name] * 2
        other_machine = Machine.from_dict(data)
        result = bool(self.ref_machine == other_machine)
        assert not result
