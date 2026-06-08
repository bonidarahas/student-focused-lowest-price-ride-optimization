from agents.planner_agent import PlannerAgent
from evaluation.eval_cases import EVAL_CASES


class AgentEvaluator:
    """
    Evaluates whether the Planner Agent routes questions correctly.
    """

    def __init__(self):
        self.planner_agent = PlannerAgent()

    def run_evaluation(self) -> dict:
        results = []

        passed = 0
        failed = 0

        for case in EVAL_CASES:
            question = case["question"]
            expected_route = case["expected_route"]

            result = self.planner_agent.handle_message(question)
            actual_route = result["route"]

            is_passed = actual_route == expected_route

            if is_passed:
                passed += 1
            else:
                failed += 1

            results.append({
                "id": case["id"],
                "question": question,
                "expected_route": expected_route,
                "actual_route": actual_route,
                "passed": is_passed,
                "answer": result["answer"]
            })

        total_tests = len(EVAL_CASES)
        accuracy = (passed / total_tests) * 100 if total_tests > 0 else 0

        return {
            "total_tests": total_tests,
            "passed": passed,
            "failed": failed,
            "accuracy": f"{accuracy:.1f}%",
            "results": results
        }