import portage

portage_db = portage.db[portage.root]["vartree"].dbapi


def __get_cpv_for_package(package: str) -> str:
    candidate_cpvs = portage_db.match(package)
    if len(candidate_cpvs) > 1:
        raise RuntimeError(f"Ambiguous package '{package}', candidates are: {candidate_cpvs}")
    elif not candidate_cpvs:
        raise RuntimeError(f"Package '{package}' not found")
    return candidate_cpvs[0]


def get_ebuild_path_for_installed_package(package: str) -> str:
    return portage_db.findname(__get_cpv_for_package(package))


def is_package_installed(package: str) -> bool:
    return bool(portage_db.match(package))


def is_use_flag_enabled(package: str, use_flag: str) -> bool:
    if not is_package_installed(package):
        return False

    cpv = __get_cpv_for_package(package)
    use_flags = set(portage_db.aux_get(cpv, ["USE"])[0].split())
    return use_flag in use_flags
