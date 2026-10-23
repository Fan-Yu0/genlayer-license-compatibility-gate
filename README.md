# License Compatibility Gate

A reusable GenLayer Intelligent Contract for evidence-backed open-source
license screening in DeFi, software procurement, and on-chain package
registries.

Repository: <https://github.com/Fan-Yu0/genlayer-license-compatibility-gate>

## Problem

A release page can claim one license while the repository ships another. Even
when the identifier is correct, the buyer still needs to know whether the
license permits commercial use, includes a patent grant, requires attribution,
or carries copyleft obligations.

Ordinary smart contracts cannot read that evidence. A naive LLM integration can
read it, but then asks the model to make an unauditable legal decision. This
contract separates those jobs.

## How it works

1. A publisher registers a package with an official release page, a canonical
   license text URL, a maximum acceptable copyleft level, and a policy bitmask.
2. Anyone calls `screen(package_id)`.
3. Validators independently fetch both sources.
4. The LLM extracts only a single SPDX identifier and whether the two sources
   agree.
5. Deterministic contract code looks up license rights and applies the buyer's
   policy.

The model never decides compatibility. It only identifies evidence. An
unrecognized license returns `REVIEW_REQUIRED`; it never silently passes.

| Condition | Decision |
| --- | --- |
| Sources conflict or are insufficient | `INCOMPATIBLE` |
| License is not in the deterministic catalog | `REVIEW_REQUIRED` |
| Copyleft level exceeds the buyer ceiling | `INCOMPATIBLE` |
| Required commercial or patent right is absent | `INCOMPATIBLE` |
| Attribution is disallowed but required | `INCOMPATIBLE` |
| All policy checks pass | `COMPATIBLE` |

Other contracts can query `is_clear(package_id)`.

## Why this is a GenLayer primitive

- License declarations are public web evidence, not on-chain facts.
- The evidence changes over time, so a fresh assessment is permissionless.
- The LLM is limited to source extraction; policy remains deterministic.
- Validators independently re-fetch and compare the decision-bearing fields.
- Unknown or conflicting evidence fails closed into review or rejection.
- The contract works without a frontend and can be composed by package
  registries, procurement contracts, DAOs, and dependency firewalls.

## State machine

```text
DRAFT --screen--> SCREENED --screen--> SCREENED
  |                   |
  +------withdraw-----+--> WITHDRAWN
```

`register_package` and `withdraw` are restricted to the publisher. `screen` is
permissionless because the sources and policy are public.

## Consensus design

The non-deterministic block performs two web reads and one structured LLM
extraction:

```json
{
  "license_id": "Apache-2.0",
  "source_consistency": "consistent",
  "summary": "short evidence summary"
}
```

The validator independently repeats the extraction and compares `license_id`
and `source_consistency`, the two values that affect the deterministic
decision. Summary wording and prose are not compared.

License metadata lives in `KNOWN_LICENSES` inside the contract. The catalog is
intentionally small and explicit. New licenses require a contract upgrade
rather than accepting arbitrary model-generated rights.

## Policy

Call `policy_bits()` on the deployed contract for authoritative values.

| Flag | Value | Meaning |
| --- | --- | --- |
| `REQUIRE_COMMERCIAL_USE` | 1 | Reject licenses that do not permit commercial use |
| `REQUIRE_PATENT_GRANT` | 2 | Reject licenses without an explicit patent grant |
| `DISALLOW_ATTRIBUTION` | 4 | Reject licenses that require attribution |

Copyleft levels:

| Level | Meaning |
| --- | --- |
| 0 | Permissive or public domain |
| 1 | Weak or file-level copyleft |
| 2 | Strong project-level copyleft |
| 3 | Network copyleft |

## Repository layout

```text
contracts/license_compatibility_gate.py
tests/direct/test_license_compatibility_gate.py
deploy/deployScript.ts
gltest.config.yaml
evidence/deployment.json
evidence/studio-screening.png
SUBMISSION.md
```

## Local verification

```shell
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
genvm-lint check contracts/license_compatibility_gate.py
pytest tests/direct/ -v
```

On Windows, `tests/direct/conftest.py` contains a cleanup shim for a
`gltest-direct` temporary-file issue. It does not affect contract behavior.

## Deploy

### Studio

1. Open <https://studio.genlayer.com/>.
2. Select the current GenLayer testnet shown in Studio.
3. Create a contract, paste
   `contracts/license_compatibility_gate.py`, and deploy with no constructor
   arguments.
4. Register a real package using public release and license URLs.
5. Call `screen(package_id)` and save the contract address and both transaction
   hashes.

### CLI

```shell
npm install
genlayer network
genlayer deploy
```

## Current deployment

- Contract: `0x2Df63f0a2AE4532f8D2CD726B3919585E79110fa`
- Network: GenLayer Studio stable (`studionet`)
- Deployment status: `FINALIZED`
- Explorer:
  https://explorer-studio.genlayer.com/address/0x2Df63f0a2AE4532f8D2CD726B3919585E79110fa
- Deployment transaction:
  https://explorer-studio.genlayer.com/tx/0x728b1ca1cb050e2fd20b1453a81522df384c28eb70a52ae245647b157dc7e65c
- Live package: `pallets/flask`
- Registration transaction:
  https://explorer-studio.genlayer.com/tx/0xc228193e8639c0d093e12b9ca0b617d4ac232f18db9e527c09f1efb4cf2f3f18
- Screening transaction:
  https://explorer-studio.genlayer.com/tx/0xb77ec1f1b5d380861b03e5fbf66bfb81124ea7e8ff396f14801b67dd43079b41
- Screening result: `BSD-3-Clause`, consistent evidence, round 1, decision
  `COMPATIBLE` (`decision = 1`)

## Live example

Use a public release with a machine-readable declaration and canonical license
text. The deployed example uses Flask's BSD-3-Clause license with a
commercial-use requirement:

```text
package_id: pallets/flask
release_url: https://pypi.org/project/Flask/
license_url: https://raw.githubusercontent.com/pallets/flask/main/LICENSE.txt
max_copyleft: 0
policy_flags: 1
```

Call `screen("pallets/flask")` to refresh the evidence. Query
`get_screening("pallets/flask")` for the current result.

## Security notes

- Only HTTPS evidence URLs are accepted.
- The two evidence URLs must differ.
- Source text is treated as untrusted evidence, not instructions.
- The LLM cannot supply rights, copyleft levels, or the final decision.
- Unknown licenses require review and never auto-approve.
- This contract records a software procurement signal. It is not legal advice
  or a substitute for counsel.
