from .Dataset import Dataset
from evaluations.func_evaluate import evaluate_functional_correctness, evaluate_io, run_generated_code, run_unittest_style_code
from constants.paths import *
import subprocess

class BigCodeGenDataset(Dataset):
    def __init__(
        self,
        path: str = BigCodeGen_DATA_DIR_PATH,

    ):
        super().__init__(path)
        self.id_key = "task_id"

    def evaluate(
        self,
        item: dict,
        cur_imp: str,
        language: str,
    ):
        result = run_unittest_style_code(
            generated_code=cur_imp,
            test_cases_code=item["test"]

        )
        return result == "passed"

    def evaluate_sample_io(
        self,
        item: dict,
        cur_imp: str,
        language: str,
    ):
        return run_generated_code(
            generated_code=cur_imp,
            test_cases_code=item["sample_io"],
        )




    @staticmethod
    def get_prompt(item):
        return item["instruct_prompt"]
