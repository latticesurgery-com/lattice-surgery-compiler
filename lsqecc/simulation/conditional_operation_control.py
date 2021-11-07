from typing import Optional


class HasPauliEigenvalueOutcome:
    """Mixin class to be implmented by things that have a +1 or -1 outcome, like measurements of pauli products"""

    def get_outcome(self) -> Optional[int]:
        if hasattr(self, "outcome"):
            return self.outcome
        else:
            return None

    def set_outcome(self, v: int):
        if v not in {-1, 1}:
            raise Exception("Pauli outcome must be -1 or +1, got: " + str(v))
        self.outcome = v


class EvaluationCondition:
    """Instances of this are used as functor to tell if something needs to be evaluated,
    mostly together with EvaluationConditionManager"""

    def does_evaluate(self):
        raise NotImplementedError


class ConditionalOperation:
    """Mixin for objects representing operations conditional on outcomes. Uses instances EvaluationCondition
    as functors to be called when checking if a condtional operation needs to execute or not"""

    def set_condition(self, condition: Optional[EvaluationCondition]):
        self.condition = condition

    def get_condition(self) -> Optional[EvaluationCondition]:
        if self.is_conditional():
            return self.condition
        else:
            return None

    def does_evaluate(self) -> bool:
        """Note: Operations conditioned on outcomes that didn't execute also won't execute"""
        if not self.is_conditional():
            return True
        assert self.condition is not None
        return self.condition.does_evaluate()

    def is_conditional(self):
        return hasattr(self, "condition") and self.condition is not None
