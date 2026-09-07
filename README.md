# Foundry Control Plane vs. Foundry Local: can it manage local agents?

A sourced research brief answering one question:

> **Does the Microsoft Foundry Control Plane manage local agents, even when the agent is on Azure Foundry Local?**

Every claim here is traced to first-party Microsoft Learn documentation, quoted in
[`docs/evidence.md`](docs/evidence.md). Researched **29 July 2026**.

**Go deeper:** [WORKSHOP.md](WORKSHOP.md) is a 45-minute research lab with
claim classification, two concrete data-flow scenarios, a falsification exercise,
and a decision-record template. The model/application distinction and custom-agent
registration/management sources were rechecked **7 September 2026**; the entire
July feature/tier matrix has not been revalidated. See the evidence refresh note.

> [!WARNING]
> These are fast-moving products, several of them in preview. Negative claims ("X is not
> supported") are the first thing to go stale. Treat this as a **dated snapshot** and re-verify
> against the linked docs before making a design decision. See [Caveats](#caveats-and-how-to-re-verify).

---

## TL;DR

**Not natively — and the phrase "Azure Foundry Local" is ambiguous, so there are two answers.**

The Foundry Control Plane governs an agent by sitting in one or both of two paths:

1. **The control path** — an Azure API Management (APIM) endpoint it can route through and block.
2. **The telemetry path** — OpenTelemetry gen-AI spans landing in the project's Application Insights.

An out-of-the-box Foundry Local inference runtime does not by itself put an agent
application in either path. An application using it can separately add a gateway
and telemetry, which is why the qualified custom-agent answer below matters.

| Your reading of "Azure Foundry Local" | What it actually is | Managed by Foundry Control Plane? |
|---|---|---|
| **Foundry Local** (on-device runtime) | On-device **model inference** — ONNX Runtime, ~20 MB, SDK for C#/JS/Rust/Python. No Azure subscription required. | **No.** Not a supported agent platform, and there is no agent object to manage. |
| **Foundry Local on Azure Local** (Arc-enabled Kubernetes, preview) | On-premises **model inference** on Arc-enabled Kubernetes, managed as an Azure Arc extension. | **No — but for a different reason.** It *is* Azure-managed, just by **Azure Arc**, not the Foundry Control Plane. And it manages **models**, not agents. |

**The narrow "yes":** an agent *application you write* that happens to use Foundry Local for
inference can be registered as a **custom agent** — if you give it an endpoint that Azure can reach.
You then get an inventory row, runs/error-rate, traces, and block/unblock. You do **not** get
start/stop, cost, or token usage. And you pay for it by giving up offline operation.

---

## The distinction that drives everything: models vs. agents

Foundry Local is **not an agent-hosting platform**. It has a curated model catalog, model lifecycle,
and an OpenAI-compatible endpoint. It has no agent resource, no agent registry, no agent lifecycle.

This does *not* mean "agents on Foundry Local don't exist" — they obviously do. Pointing Microsoft
Agent Framework, Semantic Kernel, LangChain, or AutoGen at a local OpenAI-compatible endpoint is a
normal, documented pattern. What doesn't exist is an **agent-shaped resource for the control plane to
attach to**. From Foundry's perspective, that agent is an ordinary external application.

> [!IMPORTANT]
> **Do not confuse registering an HTTP endpoint with governing a complete agent.**
> The relevant target is your agent application's behavior and access boundary.
> A bare inference endpoint does not establish control over a separate
> application's tools, state, or direct local invocation paths.

---

## What the Control Plane actually supports

Foundry Control Plane auto-discovers agents on exactly these platforms:

1. Foundry agents (prompt-based, workflows, hosted agents)
2. Azure SRE Agent
3. Azure Logic Apps agent loops
4. **Custom agents** (manual registration — the only bring-your-own path)

There is no Foundry Local source type. The docs also explicitly exclude classic agents and Azure
OpenAI assistants. Notably, **Copilot Studio agents do not appear on this list either** — so the
absence of Foundry Local is not a special snub, the discovery surface is simply narrow.

---

## The custom-agent path, and exactly what it costs you

### Requirements

| Requirement | Detail |
|---|---|
| **AI Gateway** | Azure API Management, **v2 tiers only** (Basic v2 / Standard v2 / Premium v2), in the **same Entra tenant and same subscription** as the Foundry resource. |
| **Reachable endpoint** | "a public endpoint or an endpoint that's reachable from the network where you deploy the Foundry resource." |
| **Protocol** | HTTP (general) or A2A. |
| **Telemetry** | Optional for registration, required for the corresponding observability evidence. Detailed agent traces use OpenTelemetry gen-AI conventions and the project's Application Insights. |
| **Client change** | Registration mints a **new APIM URL**; clients "must use this URL." |

The docs scope this path to agents running "in Azure compute services or other cloud environments."
An intermittently-connected end-user device is not a described scenario.

### What you get vs. what you don't

| Capability | Foundry agents | Custom agents |
|---|---|---|
| Inventory row, Status | ✅ | ✅ |
| Runs, Error rate | ✅ | ✅ *(requires App Insights)* |
| Traces | ✅ | ✅ *(requires you to instrument)* |
| Project association | ✅ | ✅ |
| **Start / stop** | ✅ | ❌ **Block/unblock only** |
| Estimated cost, Token usage | ✅ | ❌ |
| Version, Published-as, Monitoring features | ✅ | ❌ |
| Entra Agent ID surfaced in Assets | ✅ | ❌ |

On lifecycle, the docs are unambiguous:

> "For custom agents, Foundry doesn't have access to the underlying infrastructure where the agent
> runs, so start and stop operations aren't available."

**On "Monitoring features" vs. "Runs/Error rate"** — these are different things, and it's worth being
precise. *Runs* and *error rate* are **computed from Application Insights telemetry**, so custom
agents get them. *Monitoring features* counts Foundry's **built-in evaluation/monitoring capabilities**
(continuous evaluation and friends), which are Foundry-platform only. No contradiction.

**On Entra Agent ID** — the accurate claim is narrow. The Assets pane **does not surface** an Entra
Agent ID for custom agents, and Foundry **does not auto-provision** one for them (Foundry Agent
Service provisions agent identities for *its own* agents). That is *not* the same as "a local agent
can never hold an Entra Agent ID." Identity is asserted **outbound by the agent**, so Azure never
needs to reach it — an org may well hold an Entra Agent ID, via Entra/Agent 365, for an agent the
Foundry Control Plane has never seen. **That is a separate governance plane.**

---

## Reachability: you can't push the gateway to the edge

A tempting fix is APIM's **self-hosted gateway** — a containerised gateway you run next to on-prem
backends. It does not work here:

| Tier | Self-hosted gateway | Valid as Foundry AI Gateway? |
|---|---|---|
| Developer | ✅ | ❌ (not v2) |
| Premium (classic) | ✅ | ❌ (not v2) |
| Basic v2 / Standard v2 / **Premium v2** | ❌ | ✅ |

**No v2 tier supports the self-hosted gateway, and Foundry's AI Gateway requires v2.** The two sets
are disjoint. (A2A backends aren't supported on self-hosted gateways either.)

> [!NOTE]
> **This is not the load-bearing blocker it first appears.** Even if a v2 tier *did* support the
> self-hosted gateway, it requires persistent outbound connectivity to Azure for configuration sync
> and telemetry. It was never going to deliver *offline* governance.

**So the correct conclusion is not "there is no way to reach a local agent."** It's the inverse of
what people assume: you can't move the gateway to the agent, so you must **bring the agent's endpoint
into Azure's reach**. Supported and semi-supported options:

- **VPN / ExpressRoute + VNet integration** — Standard v2 and Premium v2 support connecting to
  backends isolated in a virtual network. This is the legitimate enterprise path for a genuinely
  on-premises agent.
- **Azure Relay Hybrid Connections** — purpose-built reverse tunnel; a local listener holds an
  outbound connection and Azure exposes an endpoint. *Verify APIM auth and protocol fit.*
- **Entra application proxy / Private Access** — documented pattern, but service-to-service and A2A
  authentication need care.
- **Microsoft dev tunnels** — first-party, but explicitly dev/test. Not a production governance path.
- **A public endpoint or Azure-hosted facade** — works, and is the most common real answer.
- **Azure Application Gateway** — a red herring. It is an Azure-side L7 load balancer; it still needs
  a routable backend and solves nothing here.

**Every one of these requires the device to maintain persistent connectivity to Azure — which is
precisely what Foundry Local exists to avoid.**

---

## The trade-off, stated honestly

Routing a Foundry-Local-backed agent through the Control Plane doesn't "destroy" Foundry Local. It
creates a real and specific trade-off:

| What you give up | What you keep |
|---|---|
| Strictly offline operation | Model **weights** stay on the device |
| "No Azure subscription required" | Inference runs on **local hardware** (CPU/GPU/NPU) |
| A wholly on-device request path — clients now call the APIM URL, so **request/response traffic transits Azure** | No cloud **model-inference** cost per token |
| Telemetry locality — see below | Local data-at-rest characteristics |
| Recurring **APIM v2 cost** (verify current pricing) | |

> [!CAUTION]
> **Two independent Azure dependencies, not one.** Beyond the APIM hop, the telemetry hop is
> needed for the corresponding diagnostic metrics and detailed agent traces;
> registration and basic inventory do not require every telemetry feature.
> Custom instrumentation needs a configured export path to Azure Monitor.
> **Gen-AI OTel spans can carry prompt and completion content**
> depending on configuration (the sample in the docs sets `enable_content_recording=True`). So
> "data never leaves the device" can fail at the telemetry hop even if you were relaxed about the
> gateway hop.
>
> Also note the OpenTelemetry gen-AI semantic conventions are still **experimental** — attribute
> names have churned, and registration depends on `gen_ai.operation.name` / `gen_ai.agent.id`.

### What "Blocked" really means

Block/unblock is a **gateway-level control**, not host-level enforcement. A blocked agent keeps
running and keeps serving anyone who can still reach its original endpoint.

This is **not a Foundry Local quirk — it is true of every custom agent.** The real variable is whether
you can network-isolate the backend so it only accepts traffic from the gateway:

- **In Azure:** achievable — private endpoints, NSGs, IP allowlists, mTLS. Block becomes meaningful.
- **On an end-user device:** generally not achievable, and certainly not centrally enforceable. The
  machine's owner can always call `localhost` directly, while the Control Plane reports "Blocked."

Know which of those two worlds you're in before you rely on it.

---

## Decision guide

| If you need... | Do this |
|---|---|
| Offline / on-device inference, data never leaves the device | Use **Foundry Local**. Accept that Foundry Control Plane governance is **out of scope**; build your own local logging and controls. |
| Central governance of an agent, plus local inference | Host the **agent** where Azure can reach it; reconsider whether Foundry Local is the right model backend. |
| On-premises inference at enterprise scale, Azure-managed | Use **Foundry Local on Azure Local** (Arc). Manage **models** via Arc/Kubernetes. An agent on that cluster can *also* be registered as a custom agent — and because ingress is controllable, block/unblock is actually enforceable there. |
| Identity governance for a local agent | Look at **Entra Agent ID / Agent 365**, not the Foundry Control Plane. Different plane, different question. |
| Cost/token metering for local inference | Instrument it yourself. Foundry isn't in the inference path, so it has no metering signal. |

---

## Scope of this answer

This brief answers **"does the Foundry Control Plane manage it?"** It does **not** claim that
"Microsoft cannot govern local agents." Those are different questions:

- **Entra Agent ID / Agent 365** — identity plane. Works outbound; doesn't need Azure to reach the agent.
- **Defender / Purview** — depend on data or inference flowing through governed Microsoft surfaces. A
  fully local agent doing local inference generates little such signal, which is consistent with the
  conclusion here.
- **Azure Arc** — genuinely *does* manage local **model deployments** on Azure Local. So "Azure can't
  manage anything local" is false; "the Foundry Control Plane can't manage local **agents**" is true.

---

## Caveats and how to re-verify

- **Dated snapshot: 29 July 2026.** Re-verify before relying on any negative claim.
- **Preview volatility.** The Control Plane docs carry the standard "items marked (preview)" notice.
  Foundry Local on Azure Local is explicitly **preview, access by request**. Preview surfaces change.
- **Doc-set split / naming churn.** Content lives under both `/azure/foundry/` and
  `/azure/ai-foundry/`, and the branding moves between "Azure AI Foundry" and "Microsoft Foundry."
  Foundry RBAC roles were also recently renamed. Different vintages sit side by side.
- **Portal-only.** Control Plane features are described as available "through the Foundry portal only."
  If you need automation, verify whether an ARM/REST/CLI surface has since shipped.
- **Verify pricing** for APIM v2 rather than trusting any number quoted from memory.

Full quotes and links: [`docs/evidence.md`](docs/evidence.md).

---

## Method

Researched with GitHub Copilot CLI against first-party Microsoft Learn docs, then adversarially
reviewed by two independent models (GPT-5.6 Sol and Claude Opus 5, both at high reasoning effort).
Both returned "publish with fixes." Their corrections are incorporated — most substantially:
disambiguating the two readings of "Azure Foundry Local," correcting a non sequitur about gateway
reachability, narrowing the Entra Agent ID claim, and replacing rhetorical overclaims with a
specific trade-off analysis.

## Contributing

Corrections welcome — especially if a product update has invalidated something. Please open an issue
with a link to the relevant doc.

## License

[MIT](LICENSE)
