from typing import *


class HasPauliEigenvalueOutcome():
    def get_outcome(self) -> Optional[int]:
        if hasattr(self,'outcome'):
            return self.outcome

    def set_outcome(self, v:int):
        if v not in {-1,1}:
            raise Exception("Pauli outcome must be -1 or +1, got: "+str(v))
        self.outcome = v





class EvaluationCondition:
    def __init__(self, required_outcomes : List[Tuple[HasPauliEigenvalueOutcome,int]]):
        self.required_outcomes = required_outcomes

    def does_evaluate(self):

        for op_with_outcome, required_outcome in self.required_outcomes:
            reference_outcome = op_with_outcome.get_outcome()
            if reference_outcome is None or reference_outcome != required_outcome:
                return False
        return True



class EvaluationConditionManager:

    def set_condition(self, condition: EvaluationCondition):
        self.condition = condition

    def get_condition(self) -> EvaluationCondition:
        if self.is_conditional():
            return self.condition

    def does_evaluate(self) -> bool:
        """Note: Operations conditioned on outcomes that diddn't execute also won't execute"""
        if not self.is_conditional():
            return True

        return self.condition.does_evaluate()

    def is_conditional(self):
        return hasattr(self,'condition') and self.condition is not None

