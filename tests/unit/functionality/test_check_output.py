from iac_scan_runner.functionality.check_output import CheckOutput


class TestCheckOutput:
    # pylint: disable=no-self-use

    def test_to_dict(self):
        check_output = CheckOutput("output", 0)
        check_dict = check_output.to_dict()
        assert check_dict["output"] == "output"
        assert check_dict["rc"] == 0
        assert isinstance(check_dict, dict)

    def test_to_string(self):
        check_output = CheckOutput("output", 0)
        check_string = check_output.to_string()
        assert (
            check_string == f"Return code: {check_output.rc}\nOutput: {check_output.output}"
        )
        assert isinstance(check_string, str)
