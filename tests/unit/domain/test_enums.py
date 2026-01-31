"""Unit tests for domain enumerations"""

import pytest

from src.crawler.domain.entities import SubmissionStatus, UpdateMode


class TestSubmissionStatus:
    """Test suite for SubmissionStatus enumeration"""

    def test_accepted_status(self):
        """Test ACCEPTED status has correct value"""
        assert SubmissionStatus.ACCEPTED.value == "Accepted"

    def test_wrong_answer_status(self):
        """Test WRONG_ANSWER status has correct value"""
        assert SubmissionStatus.WRONG_ANSWER.value == "Wrong Answer"

    def test_time_limit_exceeded_status(self):
        """Test TIME_LIMIT_EXCEEDED status has correct value"""
        assert SubmissionStatus.TIME_LIMIT_EXCEEDED.value == "Time Limit Exceeded"

    def test_memory_limit_exceeded_status(self):
        """Test MEMORY_LIMIT_EXCEEDED status has correct value"""
        assert SubmissionStatus.MEMORY_LIMIT_EXCEEDED.value == "Memory Limit Exceeded"

    def test_runtime_error_status(self):
        """Test RUNTIME_ERROR status has correct value"""
        assert SubmissionStatus.RUNTIME_ERROR.value == "Runtime Error"

    def test_compile_error_status(self):
        """Test COMPILE_ERROR status has correct value"""
        assert SubmissionStatus.COMPILE_ERROR.value == "Compile Error"

    def test_all_statuses_are_unique(self):
        """Test that all status values are unique"""
        values = [status.value for status in SubmissionStatus]
        assert len(values) == len(set(values))

    def test_status_count(self):
        """Test that we have exactly 6 submission statuses"""
        assert len(SubmissionStatus) == 6

    def test_status_equality(self):
        """Test that enum members can be compared"""
        status1 = SubmissionStatus.ACCEPTED
        status2 = SubmissionStatus.ACCEPTED
        status3 = SubmissionStatus.WRONG_ANSWER

        assert status1 == status2
        assert status1 != status3

    def test_status_can_be_used_in_sets(self):
        """Test that SubmissionStatus can be used in sets"""
        status_set = {
            SubmissionStatus.ACCEPTED,
            SubmissionStatus.WRONG_ANSWER,
            SubmissionStatus.ACCEPTED,  # Duplicate
        }
        assert len(status_set) == 2

    def test_status_can_be_used_in_dicts(self):
        """Test that SubmissionStatus can be used as dict keys"""
        status_dict = {
            SubmissionStatus.ACCEPTED: "success",
            SubmissionStatus.WRONG_ANSWER: "failure",
        }
        assert status_dict[SubmissionStatus.ACCEPTED] == "success"
        assert status_dict[SubmissionStatus.WRONG_ANSWER] == "failure"

    def test_status_string_representation(self):
        """Test that status has proper string representation"""
        status = SubmissionStatus.ACCEPTED
        assert "ACCEPTED" in str(status)

    def test_status_iteration(self):
        """Test that we can iterate over all statuses"""
        statuses = list(SubmissionStatus)
        assert len(statuses) == 6
        assert SubmissionStatus.ACCEPTED in statuses
        assert SubmissionStatus.COMPILE_ERROR in statuses


class TestUpdateMode:
    """Test suite for UpdateMode enumeration"""

    def test_skip_mode(self):
        """Test SKIP mode has correct value"""
        assert UpdateMode.SKIP.value == "skip"

    def test_update_mode(self):
        """Test UPDATE mode has correct value"""
        assert UpdateMode.UPDATE.value == "update"

    def test_force_mode(self):
        """Test FORCE mode has correct value"""
        assert UpdateMode.FORCE.value == "force"

    def test_all_modes_are_unique(self):
        """Test that all mode values are unique"""
        values = [mode.value for mode in UpdateMode]
        assert len(values) == len(set(values))

    def test_mode_count(self):
        """Test that we have exactly 3 update modes"""
        assert len(UpdateMode) == 3

    def test_mode_equality(self):
        """Test that enum members can be compared"""
        mode1 = UpdateMode.SKIP
        mode2 = UpdateMode.SKIP
        mode3 = UpdateMode.UPDATE

        assert mode1 == mode2
        assert mode1 != mode3

    def test_mode_can_be_used_in_sets(self):
        """Test that UpdateMode can be used in sets"""
        mode_set = {UpdateMode.SKIP, UpdateMode.UPDATE, UpdateMode.SKIP}  # Duplicate
        assert len(mode_set) == 2

    def test_mode_can_be_used_in_dicts(self):
        """Test that UpdateMode can be used as dict keys"""
        mode_dict = {
            UpdateMode.SKIP: "skip existing",
            UpdateMode.UPDATE: "update if newer",
            UpdateMode.FORCE: "always overwrite",
        }
        assert mode_dict[UpdateMode.SKIP] == "skip existing"
        assert mode_dict[UpdateMode.UPDATE] == "update if newer"
        assert mode_dict[UpdateMode.FORCE] == "always overwrite"

    def test_mode_string_representation(self):
        """Test that mode has proper string representation"""
        mode = UpdateMode.SKIP
        assert "SKIP" in str(mode)

    def test_mode_iteration(self):
        """Test that we can iterate over all modes"""
        modes = list(UpdateMode)
        assert len(modes) == 3
        assert UpdateMode.SKIP in modes
        assert UpdateMode.UPDATE in modes
        assert UpdateMode.FORCE in modes

    def test_mode_values_are_lowercase(self):
        """Test that all mode values are lowercase strings"""
        for mode in UpdateMode:
            assert mode.value.islower()
            assert isinstance(mode.value, str)


class TestEnumInteraction:
    """Test suite for interactions between enumerations"""

    def test_enums_are_different_types(self):
        """Test that SubmissionStatus and UpdateMode are different types"""
        status = SubmissionStatus.ACCEPTED
        mode = UpdateMode.SKIP

        assert type(status) != type(mode)
        assert isinstance(status, SubmissionStatus)
        assert isinstance(mode, UpdateMode)

    def test_enums_cannot_be_compared_across_types(self):
        """Test that different enum types cannot be equal"""
        status = SubmissionStatus.ACCEPTED
        mode = UpdateMode.SKIP

        assert status != mode

    def test_both_enums_can_coexist_in_same_dict(self):
        """Test that both enum types can be used in the same dictionary"""
        mixed_dict = {SubmissionStatus.ACCEPTED: "status", UpdateMode.SKIP: "mode"}
        assert len(mixed_dict) == 2
        assert mixed_dict[SubmissionStatus.ACCEPTED] == "status"
        assert mixed_dict[UpdateMode.SKIP] == "mode"
