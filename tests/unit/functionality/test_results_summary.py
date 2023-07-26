import pytest
import os
from iac_scan_runner.functionality.results_summary import ResultsSummary
import iac_scan_runner.vars as env


class TestResultsSummary:
    # pylint: disable=no-self-use

    def test_get_check_outcome(self, mocker):
        mock_summary = mocker.MagicMock()
        mock_summary.outcomes = {
            "mock_check": {"log": "", "files": "[]", "status": "Passed"}
        }
        output = ResultsSummary.get_check_outcome(mock_summary, "mock_check")
        assert output == "Passed"

    def test_get_check_outcome_nonexistent_check(self, mocker):
        mock_summary = mocker.MagicMock()
        mock_summary.outcomes = {
            "mock_check": {"log": "", "files": "[]", "status": "Passed"}
        }
        with pytest.raises(KeyError):
            ResultsSummary.get_check_outcome(
                mock_summary, "nonexistent_mock_check"
            )

    def test_summarize_outcome_tfsec(
        self, mocker, conf_compatibility_matrix, tfsec_output, tfsec_edited
    ):
        mock_summary = mocker.MagicMock()
        mock_summary.outcomes = {}
        compatibility = {"terraform": conf_compatibility_matrix["terraform"]}

        output = ResultsSummary.summarize_outcome(
            mock_summary,
            "tfsec",
            tfsec_output,
            {"terraform": ["test.tf"]},
            compatibility,
        )
        assert (
            output == "Problems" and mock_summary.outcomes["tfsec"]["status"] == "Problems"
        )
        assert mock_summary.outcomes["tfsec"]["log"] == tfsec_edited

        output = ResultsSummary.summarize_outcome(
            mock_summary,
            "tfsec",
            "No problems detected!",
            {"terraform": ["test.tf"]},
            compatibility,
        )

        assert (
            output == "Passed" and mock_summary.outcomes["tfsec"]["status"] == "Passed"
        )
        assert mock_summary.outcomes["tfsec"]["log"] == "No problems detected!"

    def test_summarize_outcome_git_leaks(self, mocker, conf_compatibility_matrix):
        mock_summary = mocker.MagicMock()
        mock_summary.outcomes = {}
        compatibility = {"terraform": conf_compatibility_matrix["terraform"]}
        output = ResultsSummary.summarize_outcome(
            mock_summary, "git-leaks", "Bad", {"terraform": ["test.tf"]}, compatibility
        )
        assert (
            output == "Problems" and mock_summary.outcomes["git-leaks"]["status"] == "Problems"
        )
        assert mock_summary.outcomes["git-leaks"]["log"] == "Bad"

        output = ResultsSummary.summarize_outcome(
            mock_summary,
            "git-leaks",
            "No leaks found",
            {"terraform": ["test.tf"]},
            compatibility,
        )

        assert (
            output == "Passed" and mock_summary.outcomes["git-leaks"]["status"] == "Passed"
        )
        assert mock_summary.outcomes["git-leaks"]["log"] == "No leaks found"

    def test_summarize_outcome_git_secrets(self, mocker, conf_compatibility_matrix):
        mock_summary = mocker.MagicMock()
        mock_summary.outcomes = {}
        compatibility = {"terraform": conf_compatibility_matrix["terraform"]}
        output = ResultsSummary.summarize_outcome(
            mock_summary,
            "git-secrets",
            "Bad",
            {"terraform": ["test.tf"]},
            compatibility,
        )
        assert (
            output == "Problems" and mock_summary.outcomes["git-secrets"]["status"] == "Problems"
        )
        assert mock_summary.outcomes["git-secrets"]["log"] == "Bad"

        output = ResultsSummary.summarize_outcome(
            mock_summary, "git-secrets", "", {"terraform": ["test.tf"]}, compatibility
        )

        assert (
            output == "Passed" and mock_summary.outcomes["git-secrets"]["status"] == "Passed"
        )
        assert mock_summary.outcomes["git-secrets"]["log"] == ""

    def test_summarize_outcome_terrascan(self, mocker, conf_compatibility_matrix):
        mock_summary = mocker.MagicMock()
        mock_summary.outcomes = {}
        compatibility = {"terraform": conf_compatibility_matrix["terraform"]}
        output = ResultsSummary.summarize_outcome(
            mock_summary, "terrascan", "Bad", {"terraform": ["test.tf"]}, compatibility
        )
        assert (
            output == "Problems" and mock_summary.outcomes["terrascan"]["status"] == "Problems"
        )
        assert mock_summary.outcomes["terrascan"]["log"] == "Bad"

        output = ResultsSummary.summarize_outcome(
            mock_summary, "terrascan", "", {"terraform": ["test.tf"]}, compatibility
        )

        assert (
            output == "Passed" and mock_summary.outcomes["terrascan"]["status"] == "Passed"
        )
        assert mock_summary.outcomes["terrascan"]["log"] == ""

    def test_summarize_no_files(self, mocker):
        mock_summary = mocker.MagicMock()
        mock_summary.outcomes = {}
        ResultsSummary.summarize_no_files(mock_summary, "mock_check")
        assert mock_summary.outcomes["mock_check"] == {
            "status": "No files",
            "log": "",
            "files": "",
        }

    def test_dump_outcomes(self, mocker):
        mock_summary = mocker.MagicMock()
        mock_summary.outcomes = {"out": "come"}

        ResultsSummary.dump_outcomes(mock_summary, "dump_outcomes")
        assert os.path.isfile(f"{env.ROOT_DIR}/outputs/json_dumps/dump_outcomes.json")
        os.remove(f"{env.ROOT_DIR}/outputs/json_dumps/dump_outcomes.json")

    def evaluate_verdict_passed(self, mocker, is_check):
        mock_summary = mocker.MagicMock()
        mock_summary.is_check = is_check
        mock_summary.outcomes = {
            "mock_check_A": {"status": "Passed"},
            "mock_check_B": {"status": "Passed"},
        }
        output = ResultsSummary.evaluate_verdict(mock_summary)
        assert output == "Passed"

    def evaluate_verdict_problems(self, mocker, is_check):
        mock_summary = mocker.MagicMock()
        mock_summary.is_check = is_check
        mock_summary.outcomes = {
            "mock_check_A": {"status": "Passed"},
            "mock_check_B": {"status": "Problems"},
        }
        output = ResultsSummary.evaluate_verdict(mock_summary)
        assert output == "Problems"

    def test_generate_html_prioritized_passed(
        self, mocker, load_response, results_summary_generate_html_outcomes
    ):
        mock_summary = mocker.MagicMock()
        mock_summary.outcomes = results_summary_generate_html_outcomes(True)

        ResultsSummary.generate_html_prioritized(mock_summary, "test_html")
        with open(f"{env.ROOT_DIR}/outputs/generated_html/test_html.html") as f:
            content = f.read()
        os.remove(f"{env.ROOT_DIR}/outputs/generated_html/test_html.html")

        response = load_response("results_summary_passed", "html")
        assert response in content

    def test_generate_html_prioritized_problems(
        self, mocker, results_summary_generate_html_outcomes, load_response
    ):
        mock_summary = mocker.MagicMock()
        mock_summary.outcomes = results_summary_generate_html_outcomes(False)

        ResultsSummary.generate_html_prioritized(mock_summary, "test_html")
        with open(f"{env.ROOT_DIR}/outputs/generated_html/test_html.html") as f:
            content = f.read()
        os.remove(f"{env.ROOT_DIR}/outputs/generated_html/test_html.html")

        response = load_response("results_summary_problems", "html")
        assert response in content
