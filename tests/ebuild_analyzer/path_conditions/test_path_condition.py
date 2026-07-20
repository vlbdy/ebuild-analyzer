from ebuild_analyzer.package_atoms.package_atom import PackageAtom
from ebuild_analyzer.path_conditions.path_condition import PathCondition


def test_iadd():
    pc = PathCondition(
        enabled_use_flags={'a'},
        disabled_use_flags={'b'},
    )

    pc += PathCondition(
        enabled_use_flags={'c'},
        installed_packages={PackageAtom("atom")}
    )

    assert pc == PathCondition(
        enabled_use_flags={'a', 'c'},
        disabled_use_flags={'b'},
        installed_packages={PackageAtom("atom")}
    )


def test_add():
    pc = PathCondition(
        enabled_use_flags={'a'},
        disabled_use_flags={'b'},
    )

    pc2 = PathCondition(
        enabled_use_flags={'c'},
        installed_packages={PackageAtom("atom")}
    )

    new_pc = pc + pc2

    assert pc == PathCondition(
        enabled_use_flags={'a'},
        disabled_use_flags={'b'},
    )
    assert pc2 == PathCondition(
        enabled_use_flags={'c'},
        installed_packages={PackageAtom("atom")}
    )
    assert new_pc == PathCondition(
        enabled_use_flags={'a', 'c'},
        disabled_use_flags={'b'},
        installed_packages={PackageAtom("atom")}
    )


def test_bool():
    assert bool(PathCondition()) == False
    assert bool(PathCondition(disabled_use_flags={'a'})) == True


def test_negated_add():
    pc = PathCondition(
        enabled_use_flags={'a'},
        disabled_use_flags={'b'},
    )

    pc2 = PathCondition(
        enabled_use_flags={'c'},
        installed_packages={PackageAtom("atom")}
    )

    pc.negated_add(pc2)

    assert pc == PathCondition(
        enabled_use_flags={'a'},
        disabled_use_flags={'b', 'c'},
        uninstalled_packages={PackageAtom("atom")}
    )


def test_negate():
    pc = PathCondition(
        enabled_use_flags={'a'},
        disabled_use_flags={'b'},
        installed_packages={PackageAtom("atom1")},
        uninstalled_packages={PackageAtom("atom2")}
    )

    expected_path_conditions = [
        PathCondition(disabled_use_flags={'a'}),
        PathCondition(enabled_use_flags={'b'}),
        PathCondition(uninstalled_packages={PackageAtom("atom1")}),
        PathCondition(installed_packages={PackageAtom("atom2")})
    ]

    negated_path_conditions = pc.negate()

    assert len(negated_path_conditions) == len(expected_path_conditions)
    for negated_pc in negated_path_conditions:
        assert negated_pc in expected_path_conditions
