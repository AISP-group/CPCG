from .Dataset import Dataset
from evaluations.evalute import contest_evaluate, contest_evaluate_public_tests
from constants.paths import *

def has_test_type(item, test_type="stdin"):
    """
    Check if any test in the test list has 'testtype' set to 'type'.
    """
    for test in item['sample_io']:
        if test.get("testtype") == test_type:
            return True
    return False

class LiveCodeBenchDataset(Dataset):
    def __init__(
        self,
        path: str = LCB_DATA_PATH,
    ):
        super().__init__(path)
        self.id_key = "id"

    def evaluate_sample_io(
        self,
        item: dict,
        cur_imp: str,
        language: str,
    ):
        if len(item["sample_io"]) == 0:
            return True, ""
        return contest_evaluate_public_tests(
            generated_code=cur_imp,
            id=item["id"],
            tests=item["sample_io"],
            lang=language
        )


    def evaluate(
        self,
        item: dict,
        cur_imp: str,
        language: str,
    ):
        return contest_evaluate(
            generated_code=cur_imp,
            id=item["id"],
            tests=item["test_list"],
            lang=language
        )

    @staticmethod
    def get_prompt(item):
        stdin_prog_prompt = "Generate an executable Python function generated from the given prompt. The function should take stdin as input and print the output. Simply call the function after the definition ."
        functional_prog_prompt = "Generate an executable Python function generated from the given prompt. Return the function body without invoking it at the final solution."
        if has_test_type(item):
            return f"Problem Description:\n{item['description']}\n{stdin_prog_prompt}\n"
        else:
            return f"Problem Description:\n{item['description']}\n{functional_prog_prompt}\n"
