import os
from shutil import copytree, rmtree
from iac_scan_runner.functionality.compatibility import Compatibility


class TestCompatibility:
    # pylint: disable=no-self-use

    def test_get_check_list(self, conf_compatibility_matrix):
        compatibility = Compatibility()
        iac_types = list(compatibility.compatibility_matrix.keys())
        for i in iac_types:
            assert compatibility.get_check_list(i) == conf_compatibility_matrix[i]

    def test_check_iac_type_valid_file(self, compatibility_types):
        compatibility = Compatibility()
        if not os.path.exists("compatibility_test_data"):
            copytree("tests/data", "compatibility_test_data")

        types = compatibility.check_iac_type("compatibility_test_data")
        assert set(types) == set(compatibility_types)

        rmtree("compatibility_test_data")

    def test_check_iac_type_invalid_file(self, mocker):
        compatibility = Compatibility()
        mock_file = mocker.MagicMock()
        mock_file.name = "invalid_file"
        output = compatibility.check_iac_type(mock_file.name)

        assert output == ["common"]

    def test_get_all_compatible_checks(
        self,
        mocker,
        compatibility_checks,
        compatibility_types,
        conf_compatibility_matrix,
    ):
        compatibility = Compatibility()
        mocker.patch.object(Compatibility, "check_iac_type")

        compatibility.check_iac_type.return_value = compatibility_types
        compatibility.compatibility_matrix = conf_compatibility_matrix
        if not os.path.exists("compatibility_test_data"):
            copytree("tests/data", "compatibility_test_data")

        checks = compatibility.get_all_compatible_checks("compatibility_test_data")

        assert set(checks) == compatibility_checks

        rmtree("compatibility_test_data")

    def test_get_all_compatible_checks_no_dir(self, mocker):
        compatibility = Compatibility()
        mock_file = mocker.MagicMock()
        mock_file.name = "invalid_file"
        mocker.patch.object(Compatibility, "check_iac_type")
        compatibility.check_iac_type.return_value = ["common"]

        checks = compatibility.get_all_compatible_checks(mock_file.name)

        assert set(checks) == {"git-leaks", "git-secrets", "cloc"}
