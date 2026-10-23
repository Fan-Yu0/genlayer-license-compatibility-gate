# Portal submission draft

## Category

Builder -> Intelligent Contract

## Contribution date

Use the actual deployment date. Do not select a future date.

## Description (English, under 1,000 characters)

License Compatibility Gate is a reusable GenLayer primitive for evidence-backed
open-source license screening. A publisher registers an official release page,
canonical license text, maximum copyleft level, and policy flags. Anyone can
trigger a screening. Validators independently fetch both sources and an LLM
extracts only the SPDX identifier and whether the evidence agrees. Deterministic
contract code applies a fixed license catalog and buyer policy: conflicting or
insufficient evidence is rejected, unknown licenses require review, excessive
copyleft or missing commercial and patent rights are rejected, and compliant
licenses pass. The custom validator re-fetches the evidence and compares the
decision-bearing fields, so the model cannot invent favorable license terms.
Other contracts can consume `is_clear(package_id)`. The repository includes
source, tests, deployment instructions, and a clear state model for DeFi
dependency firewalls, procurement, DAOs, and package registries.

## Deployed evidence

- Public source repository:
  https://github.com/Fan-Yu0/genlayer-license-compatibility-gate
- Contract: `0x2Df63f0a2AE4532f8D2CD726B3919585E79110fa`
- Contract Explorer:
  https://explorer-studio.genlayer.com/address/0x2Df63f0a2AE4532f8D2CD726B3919585E79110fa
- Deployment transaction:
  `0x728b1ca1cb050e2fd20b1453a81522df384c28eb70a52ae245647b157dc7e65c`
- Deployment Explorer:
  https://explorer-studio.genlayer.com/tx/0x728b1ca1cb050e2fd20b1453a81522df384c28eb70a52ae245647b157dc7e65c
- Deployment status: `FINALIZED`
- Package registration transaction:
  `0xc228193e8639c0d093e12b9ca0b617d4ac232f18db9e527c09f1efb4cf2f3f18`
- Registration Explorer:
  https://explorer-studio.genlayer.com/tx/0xc228193e8639c0d093e12b9ca0b617d4ac232f18db9e527c09f1efb4cf2f3f18
- Successful screening transaction:
  `0xb77ec1f1b5d380861b03e5fbf66bfb81124ea7e8ff396f14801b67dd43079b41`
- Screening Explorer:
  https://explorer-studio.genlayer.com/tx/0xb77ec1f1b5d380861b03e5fbf66bfb81124ea7e8ff396f14801b67dd43079b41
- Screening result: `MAJORITY_AGREE`, `ACCEPTED`
- Final decision: `COMPATIBLE` (`decision = 1`)
- Detected license: `BSD-3-Clause`
- Source consistency: `consistent`
- Screening round: `1`

## First live example

```text
package_id: pallets/flask
release_url: https://pypi.org/project/Flask/
license_url: https://raw.githubusercontent.com/pallets/flask/main/LICENSE.txt
max_copyleft: 0
policy_flags: 1
```

Then call `screen("pallets/flask")`.

## Reviewer checklist

- Persistent on-chain state and a clear lifecycle.
- Publisher-only registration and withdrawal.
- Permissionless evidence refresh.
- Independent validator re-fetching.
- LLM restricted to extraction; all policy decisions are deterministic.
- Unknown and conflicting evidence fail closed.
- Source, tests, documentation, and deployment evidence are public.
