import pytest

from calculator.commands import LastCommand
from calculator.factory import CalculationFactory
from calculator.operations import Operations
from calculator.session import CalculatorSession


def test_adjust_defaults():
    assert Operations.adjust(7) == 7


def test_adjust_adds_before_multiplying():
    assert Operations.adjust(5, offset=3, scale=2) == 16


def test_adjust_negative_settings():
    assert Operations.adjust(4, offset=-6, scale=-3) == 6


def test_adjust_zero_scale():
    assert Operations.adjust(9, offset=5, scale=0) == 0


def test_span_negative_values_and_duplicates():
    assert Operations.span(-9, -9, -2, -5) == 7


def test_span_identical_values():
    assert Operations.span(4, 4) == 0


@pytest.mark.parametrize("values", [(), (5,)])
def test_span_requires_two_values(values):
    with pytest.raises(ValueError):
        Operations.span(*values)


def test_factory_converts_adjust_inputs():
    calculation = CalculationFactory.create(
        " ADJUST ", "5", offset="3", scale="2"
    )
    assert calculation.get_result() == 16


def test_factory_rejects_extra_adjust_operands():
    with pytest.raises(ValueError):
        CalculationFactory.create("adjust", 2, 3)


def test_factory_rejects_span_options():
    with pytest.raises(ValueError):
        CalculationFactory.create("span", 2, 8, offset=1)


def test_span_validation_is_deferred():
    calculation = CalculationFactory.create("span", 5)

    with pytest.raises(ValueError):
        calculation.get_result()


def test_failed_calculation_preserves_history():
    session = CalculatorSession()
    successful = CalculationFactory.create("adjust", 6, scale=2)
    session.calculate(successful)
    previous_history = session.get_history()

    unsuccessful = CalculationFactory.create("span", 3)

    with pytest.raises(ValueError):
        session.calculate(unsuccessful)

    assert session.get_history() == previous_history
    assert session.get_history()[0][1] == 12


def test_last_with_empty_history():
    session = CalculatorSession()
    assert LastCommand(session).execute() == "History is empty."


def test_last_displays_newest_result():
    session = CalculatorSession()
    session.calculate(CalculationFactory.create("add", 1, 2))
    session.calculate(CalculationFactory.create("span", -6, 4))

    assert LastCommand(session).execute() == "span -6.0 4.0 = 10.0000"


def test_calculation_executes_once_and_last_does_not_repeat_it():
    calls = []

    def tracked_operation(value):
        calls.append(value)
        return value * 2

    from calculator.calculation import Calculation

    calculation = Calculation((7,), tracked_operation)
    session = CalculatorSession()

    assert session.calculate(calculation) == 14
    assert session.get_history()[0][1] == 14
    assert LastCommand(session).execute() == (
        "tracked_operation 7.0 = 14.0000"
    )
    assert LastCommand(session).execute() == (
        "tracked_operation 7.0 = 14.0000"
    )
    assert calls == [7.0]


def test_returned_history_list_is_a_copy():
    session = CalculatorSession()
    session.calculate(CalculationFactory.create("add", 4, 5))

    returned_history = session.get_history()
    returned_history.clear()

    assert len(session.get_history()) == 1
    assert session.get_history()[0][1] == 9