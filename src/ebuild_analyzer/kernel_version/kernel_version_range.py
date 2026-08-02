from dataclasses import dataclass
from typing import Optional, Set

from ebuild_analyzer.kernel_version.kernel_version import KernelVersion


@dataclass
class KernelVersionRange:
    _min: Optional[KernelVersion] = None
    _max: Optional[KernelVersion] = None
    _min_inclusive: bool = True
    _max_inclusive: bool = False
    _is_empty: bool = False

    @staticmethod
    def unlimited() -> KernelVersionRange:
        return KernelVersionRange(_min=None, _max=None)

    @staticmethod
    def empty() -> KernelVersionRange:
        return KernelVersionRange(_is_empty=True)

    @staticmethod
    def at_least(kernel_version: KernelVersion) -> KernelVersionRange:
        return KernelVersionRange(_min=kernel_version, _min_inclusive=True)

    @staticmethod
    def greater_than(kernel_version: KernelVersion) -> KernelVersionRange:
        return KernelVersionRange(_min=kernel_version, _min_inclusive=False)

    @staticmethod
    def at_most(kernel_version: KernelVersion) -> KernelVersionRange:
        return KernelVersionRange(_max=kernel_version, _max_inclusive=True)

    @staticmethod
    def less_than(kernel_version: KernelVersion) -> KernelVersionRange:
        return KernelVersionRange(_max=kernel_version, _max_inclusive=False)

    @staticmethod
    def exactly(kernel_version: KernelVersion) -> KernelVersionRange:
        return KernelVersionRange(_min=kernel_version, _max=kernel_version,
                                  _min_inclusive=True, _max_inclusive=True)

    @staticmethod
    def between(minimum: KernelVersion, maximum: KernelVersion, min_inclusive: bool = True,
                max_inclusive: bool = False) -> KernelVersionRange:
        kernel_version_range = KernelVersionRange(_min=minimum, _max=maximum,
                                                  _min_inclusive=min_inclusive, _max_inclusive=max_inclusive)
        if kernel_version_range.is_empty():
            return KernelVersionRange.empty()
        else:
            return kernel_version_range

    @staticmethod
    def intersect(left: Optional[KernelVersionRange], right: Optional[KernelVersionRange]) \
            -> Optional[KernelVersionRange]:
        if left is None:
            return right
        if right is None:
            return left
        return left & right

    def is_unlimited(self) -> bool:
        if self.is_empty():
            return False
        return self._min is None and self._max is None

    def is_empty(self) -> bool:
        if self._is_empty:
            return True

        if self._min is None or self._max is None:
            return False

        if self._min > self._max:
            return True

        if self._min == self._max:
            return not (self._min_inclusive and self._max_inclusive)

        return False

    def contains(self, version: KernelVersion) -> bool:
        if self.is_empty():
            return False

        if self._min is not None:
            if self._min_inclusive:
                if version < self._min:
                    return False
            elif version <= self._min:
                return False

        if self._max is not None:
            if self._max_inclusive:
                if version > self._max:
                    return False
            elif version >= self._max:
                return False

        return True

    def negate(self) -> Set[KernelVersionRange]:
        ranges: Set[KernelVersionRange] = set()

        if self.is_empty():
            return {KernelVersionRange.unlimited()}
        if self._min is None and self._max is None:
            return {KernelVersionRange.empty()}

        if self._min is not None:
            ranges.add(KernelVersionRange(_max=self._min, _max_inclusive=not self._min_inclusive))
        if self._max is not None:
            ranges.add(KernelVersionRange(_min=self._max, _min_inclusive=not self._max_inclusive))

        return ranges

    def __iand__(self, other: KernelVersionRange) -> KernelVersionRange:
        if self.is_empty() or other.is_empty():
            self._is_empty = True
            return self

        if other._min is not None:
            if self._min is None or other._min > self._min:
                self._min = other._min
                self._min_inclusive = other._min_inclusive
        if other._max is not None:
            if self._max is None or other._max < self._max:
                self._max = other._max
                self._max_inclusive = other._max_inclusive
        return self

    def __and__(self, other: KernelVersionRange) -> KernelVersionRange:
        kernel_version_range = KernelVersionRange.unlimited()

        kernel_version_range &= self
        kernel_version_range &= other

        return kernel_version_range

    def __eq__(self, other: KernelVersionRange) -> bool:
        if self.is_empty() and other.is_empty():
            return True

        return (self._min == other._min and self._max == other._max
                and self._min_inclusive == other._min_inclusive
                and self._max_inclusive == other._max_inclusive
                and self._is_empty == other._is_empty)

    def __hash__(self):
        return hash((
            self._min,
            self._max,
            self._min_inclusive,
            self._max_inclusive,
            self._is_empty,
        ))

    def __str__(self) -> str:
        if self._is_empty:
            return "no kernel versions"
        if self._min == self._max and self._min_inclusive and self._max_inclusive:
            return f"kernel == {self._min}"
        if self._min is None and self._max is None:
            return "any kernel version"

        if self._min is None:
            op = "<=" if self._max_inclusive else "<"
            return f"kernel {op} {self._max}"
        if self._max is None:
            op = ">=" if self._min_inclusive else ">"
            return f"kernel {op} {self._min}"

        left = "<=" if self._min_inclusive else "<"
        right = "<=" if self._max_inclusive else "<"
        return f"{self._min} {left} kernel {right} {self._max}"
