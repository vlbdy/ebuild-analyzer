from typing import List

from ebuild_analyzer.path_conditions.path_condition import PathCondition


# This function computes the 'cartesian product' of the lists of path conditions.
# For example, if:
#   first  = [a,b]
#   second = [c,d]
# The result is: [ac,ad,bc,bd]
def combine_path_conditions(first: List[PathCondition], second: List[PathCondition]) -> List[PathCondition]:
    if not first:
        return second.copy()
    if not second:
        return first.copy()

    return [first_condition & second_condition for first_condition in first for second_condition in second]


def negate_and_combine_path_conditions(conditions: List[PathCondition]) -> List[PathCondition]:
    new_conditions: List[PathCondition] = []
    for condition in conditions:
        new_conditions = combine_path_conditions(condition.negate(), new_conditions)
    return new_conditions


def remove_empty_path_conditions(path_conditions: List[PathCondition]) -> List[PathCondition]:
    return [condition for condition in path_conditions if condition]


def remove_duplicate_path_conditions(path_conditions: List[PathCondition]) -> List[PathCondition]:
    deduplicated_conditions = []
    for condition in path_conditions:
        if condition not in deduplicated_conditions:
            deduplicated_conditions.append(condition)
    return deduplicated_conditions
