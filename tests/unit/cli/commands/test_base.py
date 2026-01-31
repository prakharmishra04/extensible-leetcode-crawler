"""
Unit tests for the base Command interface and CommandResult dataclass.

Tests cover:
- CommandResult validation and invariants
- Command abstract interface
- Success and failure scenarios
- Edge cases and error handling
"""

import pytest

from src.crawler.cli.commands.base import Command, CommandResult


class TestCommandResult:
    """Test suite for CommandResult dataclass."""

    def test_successful_result_creation(self):
        """Test creating a successful CommandResult."""
        result = CommandResult(
            success=True, message="Operation completed successfully", data={"count": 5}
        )

        assert result.success is True
        assert result.message == "Operation completed successfully"
        assert result.data == {"count": 5}
        assert result.error is None

    def test_failed_result_creation(self):
        """Test creating a failed CommandResult."""
        error = ValueError("Invalid input")
        result = CommandResult(success=False, message="Operation failed", error=error)

        assert result.success is False
        assert result.message == "Operation failed"
        assert result.data is None
        assert result.error is error

    def test_successful_result_without_data(self):
        """Test creating a successful result without data."""
        result = CommandResult(success=True, message="Success")

        assert result.success is True
        assert result.message == "Success"
        assert result.data is None
        assert result.error is None

    def test_successful_result_with_none_data(self):
        """Test creating a successful result with explicit None data."""
        result = CommandResult(success=True, message="Success", data=None)

        assert result.success is True
        assert result.data is None
        assert result.error is None

    def test_failed_result_with_data(self):
        """Test that failed results can include data (e.g., partial results)."""
        error = RuntimeError("Partial failure")
        result = CommandResult(
            success=False,
            message="Partial failure occurred",
            data={"processed": 3, "failed": 2},
            error=error,
        )

        assert result.success is False
        assert result.data == {"processed": 3, "failed": 2}
        assert result.error is error

    def test_successful_result_cannot_have_error(self):
        """Test that successful results cannot have an error."""
        with pytest.raises(ValueError, match="Successful result cannot have an error"):
            CommandResult(
                success=True, message="Success", error=ValueError("This should not be allowed")
            )

    def test_failed_result_must_have_error(self):
        """Test that failed results must have an error."""
        with pytest.raises(ValueError, match="Failed result must have an error"):
            CommandResult(success=False, message="Failed")

    def test_failed_result_with_none_error_raises(self):
        """Test that failed results with explicit None error raises."""
        with pytest.raises(ValueError, match="Failed result must have an error"):
            CommandResult(success=False, message="Failed", error=None)

    def test_result_with_empty_message(self):
        """Test creating a result with an empty message."""
        result = CommandResult(success=True, message="")

        assert result.success is True
        assert result.message == ""

    def test_result_with_complex_data(self):
        """Test creating a result with complex data structures."""
        complex_data = {
            "problems": [{"id": "1", "title": "Two Sum"}, {"id": "2", "title": "Add Two Numbers"}],
            "stats": {"total": 2, "downloaded": 2, "failed": 0},
        }

        result = CommandResult(success=True, message="Downloaded 2 problems", data=complex_data)

        assert result.success is True
        assert result.data == complex_data
        assert len(result.data["problems"]) == 2

    def test_result_with_different_exception_types(self):
        """Test creating results with different exception types."""
        exceptions = [
            ValueError("Value error"),
            RuntimeError("Runtime error"),
            IOError("IO error"),
            Exception("Generic exception"),
        ]

        for exc in exceptions:
            result = CommandResult(
                success=False, message=f"Failed with {type(exc).__name__}", error=exc
            )

            assert result.success is False
            assert result.error is exc
            assert type(result.error).__name__ in result.message


class TestCommand:
    """Test suite for Command abstract base class."""

    def test_command_is_abstract(self):
        """Test that Command cannot be instantiated directly."""
        with pytest.raises(TypeError, match="Can't instantiate abstract class"):
            Command()

    def test_command_requires_execute_implementation(self):
        """Test that subclasses must implement execute()."""

        class IncompleteCommand(Command):
            pass

        with pytest.raises(TypeError, match="Can't instantiate abstract class"):
            IncompleteCommand()

    def test_concrete_command_can_be_instantiated(self):
        """Test that concrete commands can be instantiated."""

        class ConcreteCommand(Command):
            def execute(self) -> CommandResult:
                return CommandResult(success=True, message="Executed successfully")

        command = ConcreteCommand()
        assert isinstance(command, Command)

    def test_concrete_command_execute_returns_result(self):
        """Test that concrete command execute() returns CommandResult."""

        class ConcreteCommand(Command):
            def execute(self) -> CommandResult:
                return CommandResult(success=True, message="Executed successfully")

        command = ConcreteCommand()
        result = command.execute()

        assert isinstance(result, CommandResult)
        assert result.success is True
        assert result.message == "Executed successfully"

    def test_command_with_dependencies(self):
        """Test command with injected dependencies."""

        class ServiceCommand(Command):
            def __init__(self, service):
                self.service = service

            def execute(self) -> CommandResult:
                data = self.service.get_data()
                return CommandResult(success=True, message="Data retrieved", data=data)

        # Mock service
        class MockService:
            def get_data(self):
                return {"key": "value"}

        service = MockService()
        command = ServiceCommand(service)
        result = command.execute()

        assert result.success is True
        assert result.data == {"key": "value"}

    def test_command_handles_errors_gracefully(self):
        """Test that commands handle errors and return failed results."""

        class FailingCommand(Command):
            def execute(self) -> CommandResult:
                try:
                    raise ValueError("Something went wrong")
                except ValueError as e:
                    return CommandResult(
                        success=False, message=f"Command failed: {str(e)}", error=e
                    )

        command = FailingCommand()
        result = command.execute()

        assert result.success is False
        assert "Something went wrong" in result.message
        assert isinstance(result.error, ValueError)

    def test_command_with_state(self):
        """Test command that maintains state."""

        class StatefulCommand(Command):
            def __init__(self):
                self.execution_count = 0

            def execute(self) -> CommandResult:
                self.execution_count += 1
                return CommandResult(
                    success=True,
                    message=f"Executed {self.execution_count} times",
                    data={"count": self.execution_count},
                )

        command = StatefulCommand()

        result1 = command.execute()
        assert result1.data["count"] == 1

        result2 = command.execute()
        assert result2.data["count"] == 2

        result3 = command.execute()
        assert result3.data["count"] == 3

    def test_multiple_command_instances_are_independent(self):
        """Test that multiple command instances don't share state."""

        class CounterCommand(Command):
            def __init__(self):
                self.count = 0

            def execute(self) -> CommandResult:
                self.count += 1
                return CommandResult(success=True, message="Counted", data={"count": self.count})

        command1 = CounterCommand()
        command2 = CounterCommand()

        command1.execute()
        command1.execute()

        result1 = command1.execute()
        result2 = command2.execute()

        assert result1.data["count"] == 3
        assert result2.data["count"] == 1


class TestCommandIntegration:
    """Integration tests for Command pattern usage."""

    def test_command_chain_execution(self):
        """Test executing multiple commands in sequence."""

        class Command1(Command):
            def execute(self) -> CommandResult:
                return CommandResult(success=True, message="Command 1 executed", data={"step": 1})

        class Command2(Command):
            def __init__(self, previous_result):
                self.previous_result = previous_result

            def execute(self) -> CommandResult:
                if not self.previous_result.success:
                    return CommandResult(
                        success=False,
                        message="Previous command failed",
                        error=RuntimeError("Chain broken"),
                    )

                return CommandResult(
                    success=True,
                    message="Command 2 executed",
                    data={"step": 2, "previous": self.previous_result.data},
                )

        cmd1 = Command1()
        result1 = cmd1.execute()

        cmd2 = Command2(result1)
        result2 = cmd2.execute()

        assert result2.success is True
        assert result2.data["step"] == 2
        assert result2.data["previous"]["step"] == 1

    def test_command_with_validation(self):
        """Test command that validates input before execution."""

        class ValidatingCommand(Command):
            def __init__(self, value: int):
                self.value = value

            def execute(self) -> CommandResult:
                if self.value < 0:
                    return CommandResult(
                        success=False,
                        message="Value must be non-negative",
                        error=ValueError(f"Invalid value: {self.value}"),
                    )

                return CommandResult(
                    success=True,
                    message=f"Processed value: {self.value}",
                    data={"value": self.value},
                )

        # Valid input
        valid_cmd = ValidatingCommand(5)
        valid_result = valid_cmd.execute()
        assert valid_result.success is True

        # Invalid input
        invalid_cmd = ValidatingCommand(-1)
        invalid_result = invalid_cmd.execute()
        assert invalid_result.success is False
        assert isinstance(invalid_result.error, ValueError)
