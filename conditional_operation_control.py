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
    def set_condition(self, outcome_op: HasPauliEigenvalueOutcome, outcome_for_evaluation: int):
        self.outcome_op = outcome_op
        self.outcome_for_evaluation = outcome_for_evaluation

    def does_evaluate(self) -> bool:
        """Note: Operations conditioned on outcomes that diddn't execute also won't execute"""
        if not self.is_conditional():
            return True

        reference_outcome = self.outcome_op.get_outcome()
        if reference_outcome is not None:
            return reference_outcome == self.outcome_for_evaluation
        return False

    def is_conditional(self):
        return hasattr(self,'outcome_op')

