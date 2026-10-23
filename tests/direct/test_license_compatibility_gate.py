import json


PACKAGE_ID = "acme/payments-kit"
RELEASE_URL = "https://registry.example.com/acme/payments-kit/1.4.0"
LICENSE_URL = "https://legal.example.com/acme/payments-kit/LICENSE"

COMMERCIAL = 1
PATENT = 2
NO_ATTRIBUTION = 4


def _mock_evidence(vm, payload):
    vm.mock_web(
        r".*registry\.example\.com/acme/payments-kit/1\.4\.0.*",
        {"status": 200, "body": "Package metadata declares the project license."},
    )
    vm.mock_web(
        r".*legal\.example\.com/acme/payments-kit/LICENSE.*",
        {"status": 200, "body": "Official license text."},
    )
    vm.mock_llm(
        r".*LICENSE COMPATIBILITY SCREEN.*",
        json.dumps(payload),
    )


def _evidence(license_id="Apache-2.0", consistency="consistent", summary="Matches."):
    return {
        "license_id": license_id,
        "source_consistency": consistency,
        "summary": summary,
    }


def _register(contract, vm, publisher, max_copyleft=0, policy_flags=COMMERCIAL | PATENT):
    vm.sender = publisher
    contract.register_package(
        PACKAGE_ID,
        RELEASE_URL,
        LICENSE_URL,
        max_copyleft,
        policy_flags,
    )


def test_approves_apache_with_commercial_and_patent_rights(
    direct_vm, direct_deploy, direct_alice
):
    contract = direct_deploy("contracts/license_compatibility_gate.py")
    _register(contract, direct_vm, direct_alice)
    _mock_evidence(direct_vm, _evidence())

    contract.screen(PACKAGE_ID)

    result = contract.get_screening(PACKAGE_ID)
    assert result["state"] == 1
    assert result["decision"] == 1
    assert result["license_id"] == "Apache-2.0"
    assert result["license_recognized"] is True
    assert result["copyleft_level"] == 0
    assert result["commercial_use"] is True
    assert result["patent_grant"] is True
    assert result["round"] == 1
    assert contract.is_clear(PACKAGE_ID) is True


def test_normalizes_common_license_alias(direct_vm, direct_deploy, direct_alice):
    contract = direct_deploy("contracts/license_compatibility_gate.py")
    _register(contract, direct_vm, direct_alice)
    _mock_evidence(direct_vm, _evidence("Apache License 2.0"))

    contract.screen(PACKAGE_ID)

    assert contract.get_screening(PACKAGE_ID)["license_id"] == "Apache-2.0"


def test_rejects_mit_when_patent_grant_is_required(
    direct_vm, direct_deploy, direct_alice
):
    contract = direct_deploy("contracts/license_compatibility_gate.py")
    _register(contract, direct_vm, direct_alice)
    _mock_evidence(direct_vm, _evidence("MIT"))

    contract.screen(PACKAGE_ID)

    result = contract.get_screening(PACKAGE_ID)
    assert result["decision"] == 3
    assert result["patent_grant"] is False
    assert contract.is_clear(PACKAGE_ID) is False


def test_rejects_copyleft_above_policy(direct_vm, direct_deploy, direct_alice):
    contract = direct_deploy("contracts/license_compatibility_gate.py")
    _register(contract, direct_vm, direct_alice, max_copyleft=1)
    _mock_evidence(direct_vm, _evidence("GPL-3.0-only"))

    contract.screen(PACKAGE_ID)

    result = contract.get_screening(PACKAGE_ID)
    assert result["decision"] == 3
    assert result["copyleft_level"] == 2


def test_allows_weak_copyleft_within_policy(
    direct_vm, direct_deploy, direct_alice
):
    contract = direct_deploy("contracts/license_compatibility_gate.py")
    _register(contract, direct_vm, direct_alice, max_copyleft=1)
    _mock_evidence(direct_vm, _evidence("MPL-2.0"))

    contract.screen(PACKAGE_ID)

    result = contract.get_screening(PACKAGE_ID)
    assert result["decision"] == 1
    assert result["copyleft_level"] == 1


def test_rejects_attribution_when_policy_disallows_it(
    direct_vm, direct_deploy, direct_alice
):
    contract = direct_deploy("contracts/license_compatibility_gate.py")
    _register(
        contract,
        direct_vm,
        direct_alice,
        policy_flags=COMMERCIAL | NO_ATTRIBUTION,
    )
    _mock_evidence(direct_vm, _evidence("MIT"))

    contract.screen(PACKAGE_ID)

    result = contract.get_screening(PACKAGE_ID)
    assert result["decision"] == 3
    assert result["attribution_required"] is True


def test_requires_review_for_unknown_license(
    direct_vm, direct_deploy, direct_alice
):
    contract = direct_deploy("contracts/license_compatibility_gate.py")
    _register(contract, direct_vm, direct_alice)
    _mock_evidence(direct_vm, _evidence("Acme-Proprietary-1.0"))

    contract.screen(PACKAGE_ID)

    result = contract.get_screening(PACKAGE_ID)
    assert result["decision"] == 2
    assert result["license_recognized"] is False
    assert contract.is_clear(PACKAGE_ID) is False


def test_rejects_conflicting_evidence(direct_vm, direct_deploy, direct_alice):
    contract = direct_deploy("contracts/license_compatibility_gate.py")
    _register(contract, direct_vm, direct_alice)
    _mock_evidence(direct_vm, _evidence("MIT", "conflicting"))

    contract.screen(PACKAGE_ID)

    result = contract.get_screening(PACKAGE_ID)
    assert result["decision"] == 3
    assert result["source_consistency"] == "conflicting"


def test_only_publisher_can_withdraw(
    direct_vm, direct_deploy, direct_alice, direct_bob
):
    contract = direct_deploy("contracts/license_compatibility_gate.py")
    _register(contract, direct_vm, direct_alice)

    direct_vm.sender = direct_bob
    with direct_vm.expect_revert("only the publisher can withdraw"):
        contract.withdraw(PACKAGE_ID)

    direct_vm.sender = direct_alice
    contract.withdraw(PACKAGE_ID)
    assert contract.get_screening(PACKAGE_ID)["state"] == 2
    assert contract.is_clear(PACKAGE_ID) is False


def test_rejects_duplicate_package_id(direct_vm, direct_deploy, direct_alice):
    contract = direct_deploy("contracts/license_compatibility_gate.py")
    _register(contract, direct_vm, direct_alice)

    with direct_vm.expect_revert("package_id already registered"):
        contract.register_package(
            PACKAGE_ID,
            RELEASE_URL,
            LICENSE_URL,
            0,
            COMMERCIAL,
        )


def test_rejects_non_https_evidence(direct_vm, direct_deploy, direct_alice):
    contract = direct_deploy("contracts/license_compatibility_gate.py")
    direct_vm.sender = direct_alice

    with direct_vm.expect_revert("release_url must be an https URL"):
        contract.register_package(
            PACKAGE_ID,
            "http://registry.example.com/acme/payments-kit",
            LICENSE_URL,
            0,
            COMMERCIAL,
        )


def test_unknown_package_is_not_clear(direct_deploy):
    contract = direct_deploy("contracts/license_compatibility_gate.py")
    assert contract.is_clear("unknown/package") is False
    assert contract.get_screening("unknown/package") == {}


def test_validator_accepts_matching_evidence(
    direct_vm, direct_deploy, direct_alice
):
    contract = direct_deploy("contracts/license_compatibility_gate.py")
    _register(contract, direct_vm, direct_alice)
    _mock_evidence(direct_vm, _evidence())

    contract.screen(PACKAGE_ID)

    assert direct_vm.run_validator() is True


def test_validator_rejects_changed_license(
    direct_vm, direct_deploy, direct_alice
):
    contract = direct_deploy("contracts/license_compatibility_gate.py")
    _register(contract, direct_vm, direct_alice)
    _mock_evidence(direct_vm, _evidence("Apache-2.0"))
    contract.screen(PACKAGE_ID)

    direct_vm.clear_mocks()
    _mock_evidence(direct_vm, _evidence("GPL-3.0-only"))

    assert direct_vm.run_validator() is False


def test_validator_ignores_summary_wording(
    direct_vm, direct_deploy, direct_alice
):
    contract = direct_deploy("contracts/license_compatibility_gate.py")
    _register(contract, direct_vm, direct_alice)
    _mock_evidence(direct_vm, _evidence(summary="Leader wording."))
    contract.screen(PACKAGE_ID)

    direct_vm.clear_mocks()
    _mock_evidence(direct_vm, _evidence(summary="Different validator wording."))

    assert direct_vm.run_validator() is True


def test_license_info_exposes_deterministic_policy(direct_deploy):
    contract = direct_deploy("contracts/license_compatibility_gate.py")

    info = contract.license_info("Apache License 2.0")
    assert info["license_id"] == "Apache-2.0"
    assert info["patent_grant"] is True
    assert contract.license_info("Acme-Proprietary-1.0") == {}
