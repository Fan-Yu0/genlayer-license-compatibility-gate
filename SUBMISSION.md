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
dependency firewalls, software procurement, DAOs, and package registries.

## Deployed evidence

Complete after publishing and deploying:

- Public source repository: `REPOSITORY_URL_TO_ADD`
- Contract: `CONTRACT_ADDRESS_TO_ADD`
- Contract Explorer: `CONTRACT_EXPLORER_URL_TO_ADD`
- Deployment transaction: `DEPLOY_TX_TO_ADD`
- Deployment Explorer: `DEPLOY_EXPLORER_URL_TO_ADD`
- Deployment status: `FINALIZED`
- Successful screening transaction: `SCREEN_TX_TO_ADD`
- Screening Explorer: `SCREEN_EXPLORER_URL_TO_ADD`
- Screening result: `MAJORITY_AGREE`, `ACCEPTED`
- Final decision: `COMPATIBLE` (`decision = 1`)

## First live example

```text
package_id: pallets/flask
release_url: https://pypi.org/project/Flask/
license_url: https://raw.githubusercontent.com/pallets/flask/main/LICENSE.txt
max_copyleft: 0
policy_flags: 3
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
