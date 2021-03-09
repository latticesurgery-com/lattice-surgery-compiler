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
    def does_evaluate(self):
        raise NotImplemented()



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

