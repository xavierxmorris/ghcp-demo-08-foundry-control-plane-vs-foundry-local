# Workshop: make an architecture answer falsifiable

**Audience:** architects, technical sellers, and developers doing research.
**Time:** 45 minutes. **Prerequisites:** a browser; Copilot is optional for the
research exercise. No Azure resources need to be created.
**Outcome:** a short decision record with claim-level evidence and explicit limits.

## 1. Define the question before searching - 7 minutes

The phrase "manage local agents" hides several different questions:

| Term | Possible meaning | Why the distinction matters |
| --- | --- | --- |
| Local | End-user device, on-premises cluster, or locally developed cloud app | Different connectivity and operating models |
| Agent | Inference runtime, application, or registered asset | Different things can be managed |
| Manage | Inventory, observe, block traffic, stop a process, or govern identity | One capability does not imply the others |
| Offline | No network during inference, first-run downloads excluded, or fully disconnected operations | Different test and governance boundaries |

Start with a precise question, for example: "Can central governance stop all
use of an agent application on an intermittently connected laptop that runs
inference locally?"

```text
Before answering, disambiguate the deployment, managed object, and requested
control. Use the repository's evidence as a starting point, then look for
current first-party documentation. Label unknowns instead of filling them.
```

## 2. Build a claim ledger - 10 minutes

Read the [brief](README.md) and [evidence register](docs/evidence.md).
For each material claim, record:

| Field | Example |
| --- | --- |
| Claim ID and exact wording | C-01: custom-agent blocking is not host shutdown |
| Evidence class | Direct documentation, architectural inference, or unverified assumption |
| Source URL and section | Lifecycle operations in the management page |
| Source/retrieval date | Original 2026-07-29 or targeted 2026-09-07 refresh |
| Product/version/status | Rolling service; note any preview feature |
| Applicability | Custom agent, not every Foundry agent type |
| What would invalidate it | New infrastructure-control support for that custom platform |

A search-result snippet is a discovery aid. Fetch the whole relevant section
before writing procedures, prerequisites, or a negative support claim.
Do not cite a page title as if it proved every sentence in a paragraph.

**Checkpoint:** distinguish "the support list does not name Foundry Local"
from "no application using local inference can ever be registered."

## 3. Trace two concrete scenarios - 12 minutes

### Scenario A: inference on a disconnected laptop

```text
local user -> local agent application -> Foundry Local inference
                     |
                     +-> local tools and state
```

The local inference runtime does not automatically create a centrally managed
agent asset. Initial model/component downloads are a separate network need.
If the application adds telemetry, cloud tools, or synchronization, its overall
data-flow claim must include those paths too.

Questions to answer: which files are local, which calls can leave the device,
what works after disconnecting, and who controls direct invocation?

### Scenario B: reachable on-premises agent with local inference

```text
client -> Foundry-associated API gateway -> reachable agent endpoint
                                               |
                                               +-> local inference/tools
                                               +-> optional telemetry export
```

Registration can put the gateway in the client request path. It does not move
inference into Azure, stop the host, or automatically protect an alternative
route to the origin. Gateway blocking is meaningful only for traffic that
actually traverses that control.

Registration and observability are also separate: basic inventory can exist
without detailed agent spans. Runs, error information, and tool/model traces
need their corresponding telemetry configuration. Do not call an empty metric
pane proof that the agent has never run.

**Checkpoint:** identify the owner, data, authentication, and failure behavior
on every arrow. A diagram without the direct-origin path can overstate control.

## 4. Try to disprove the answer - 8 minutes

```text
Critique this claim: "Because inference uses Foundry Local, no information can
leave the device and Foundry can never govern the application." Find current
counter-evidence. Separate model execution from application networking,
gateway enforcement, telemetry, and identity. Do not deploy anything.
```

Useful counterexamples are architectural, not rhetorical: an application can
perform inference locally while exporting traces or calling a cloud API.
Conversely, a visible asset is not evidence of an effective host-level kill switch.

Keep separate conclusions for identity governance, inference hosting, traffic
control, and observability. A missing column in one portal is not proof that
an identity capability cannot exist through another service.

Do not silently "refresh" the July APIM-tier matrix by changing its date.
Revisit the actual tier and gateway documentation before relying on it.

## 5. Write the decision record - 8 minutes

Use this short structure:

```text
Question and deployment scenario:
Required controls and data-residency constraints:
Decision:
Direct evidence (claim IDs and source URLs):
Architectural deductions:
Unverified assumptions / preview dependencies:
Costs and operational trade-offs:
Conditions that would change the decision:
Recheck owner and trigger:
```

A good conclusion might allow local inference but require a reachable application
and controlled ingress for centralized traffic blocking. It must also state
what happens offline and what bypass paths remain outside the gateway.

For an extension, compare a laptop and a managed on-premises cluster under the
same required-control list. Do not assume that "on premises" settles network
reachability, telemetry export policy, or host administration.

## Evidence quality and troubleshooting

| Problem | Better response |
| --- | --- |
| Sources disagree | Record both dates, versions, and scopes; do not average the claims |
| A link redirects to renamed docs | Record the final authoritative page and verify the product scope |
| A support claim has no quote | Mark it as inference or unverified |
| Only metadata is visible | Check permissions and telemetry before concluding feature absence |
| Documentation is silent | Say "not documented here," not "impossible" |

Keep the decision record and citations; no infrastructure cleanup is needed
for this reading/research track. Never publish internal topology or credentials
as proof of an architectural claim.

## Current sources and limits

The original brief is **2026-07-29**. A targeted refresh on **2026-09-07**
rechecked [Foundry Local](https://learn.microsoft.com/azure/ai-foundry/foundry-local/what-is-foundry-local),
[registration](https://learn.microsoft.com/azure/foundry/control-plane/register-custom-agent),
and [management](https://learn.microsoft.com/azure/foundry/control-plane/how-to-manage-agents).
These are rolling services; this guide does not assign them an invented
release version or certify the entire historical feature matrix.
