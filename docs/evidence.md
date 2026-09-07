# Evidence

Direct quotations from first-party Microsoft Learn documentation, retrieved **29 July 2026**.
Each claim in the [README](../README.md) traces to an item here.

## September refresh: scoped, not a new full audit

On **7 September 2026**, the current Microsoft Learn pages for
[Foundry Local](https://learn.microsoft.com/azure/ai-foundry/foundry-local/what-is-foundry-local),
[custom-agent registration](https://learn.microsoft.com/azure/foundry/control-plane/register-custom-agent),
and [agent management](https://learn.microsoft.com/azure/foundry/control-plane/how-to-manage-agents)
were fetched again.

They continue to distinguish local inference from registration of a reachable
agent application, and custom-agent block/unblock from infrastructure start/stop.
Registration describes telemetry as optional when that capability is not needed;
metrics and detailed traces require the appropriate observability configuration.
The README now states that distinction instead of implying telemetry is always
a prerequisite for basic inventory.

The July APIM-tier, Azure Local, and identity comparisons below remain a dated
snapshot. This refresh does not certify every negative claim in them.

---

## 1. Foundry Control Plane — supported agent platforms

**Source:** [Manage agents at scale in Microsoft Foundry Control Plane](https://learn.microsoft.com/en-us/azure/foundry/control-plane/how-to-manage-agents)

> Foundry Control Plane automatically discovers agents in the following platforms:
>
> - Foundry agents, including prompt-based agents, workflows, and hosted agents
> - Azure SRE Agent
> - Azure Logic Apps agent loops
> - Custom agents

> Classic agents and Azure OpenAI assistants aren't supported.

**Observations**
- No Foundry Local source type appears in this list.
- Copilot Studio is likewise absent.

---

## 2. Lifecycle operations by platform

**Source:** [Manage agents at scale](https://learn.microsoft.com/en-us/azure/foundry/control-plane/how-to-manage-agents)

| Platform | Agent type | Supported actions |
|---|---|---|
| Foundry | Prompt/Workflow (unpublished) | None |
| Foundry | Hosted | Start/stop |
| Foundry | Prompt/Workflow/Hosted (published) | Start/stop |
| Azure SRE Agent | n/a | Start/stop |
| Azure Logic Apps | n/a | Start/stop |
| **Custom** | n/a | **Block/unblock** |

> For custom agents, Foundry doesn't have access to the underlying infrastructure where the agent
> runs, so start and stop operations aren't available. However, Foundry can block incoming requests
> to the agent. Blocking prevents clients from using the agent.

> Agents in the **Blocked** state run in their associated infrastructure but can't take incoming
> requests.

**Observation.** The docs say a blocked agent "can't take incoming requests." Mechanically this is
scoped to requests *through the gateway* — the origin endpoint is unaffected. Enforcement therefore
depends on network-isolating the backend, which Foundry does not control for custom agents.

---

## 3. Assets pane — field availability by platform

**Source:** [Manage agents at scale](https://learn.microsoft.com/en-us/azure/foundry/control-plane/how-to-manage-agents)

| Column | Agent platform |
|---|---|
| Name | All |
| Source | All |
| Project | Foundry, Custom |
| Status | All |
| Version | Foundry |
| Published as | Foundry |
| Error rate | All |
| Estimated cost | Foundry |
| Token usage | Foundry |
| Runs | All |
| Monitoring features | Foundry |
| Entra ID | Foundry |

Definitions given in the docs:

> **Monitoring features** — The number of monitoring features that are enabled in the agent.
> *(links to "The three stages of AI application lifecycle evaluation")*

> **Entra ID** — The Microsoft Entra Agent ID application and object ID associated with the agent. An
> agent identity is a special service principal in Microsoft Entra ID.

**Observations**
- *Runs* and *error rate* are marked **All**, and are computed from Application Insights telemetry —
  so custom agents do get them.
- *Monitoring features* is Foundry-only and refers to Foundry's built-in evaluation/monitoring
  capabilities. This does not conflict with the previous point.
- This table describes **what the Assets pane displays**. Absence of a column is not proof that an
  underlying capability cannot exist by another route — see §8 on Entra Agent ID.

---

## 4. Custom agent registration — prerequisites

**Source:** [Register and manage custom agents](https://learn.microsoft.com/en-us/azure/foundry/control-plane/register-custom-agent)

> An AI gateway configured in your Foundry resource. Foundry uses Azure API Management to register
> agents as APIs.

> An agent that you deploy and expose through a reachable endpoint. The endpoint can be either a
> public endpoint or an endpoint that's reachable from the network where you deploy the Foundry
> resource.

> Registering custom agents that run in Azure compute services or other cloud environments can help
> you gain visibility into their operations and control their behavior.

> The agent communicates by using one of the supported protocols: HTTP (general) or A2A (more specific).

> Your agent emits data by using the OpenTelemetry semantic conventions for generative AI solutions
> (or you don't need this capability).

> After you register an agent, Foundry Control Plane generates a new URL. *Clients and users must use
> this URL to communicate with the agent*.

> This capability is available only in the Foundry (new) portal.

**Telemetry requirement:**

> Traces include spans with attribute `gen_ai.operation.name="create_agent"` and
> `gen_ai.agent.id="<agent-id>"` (or `gen_ai.agent.name="<agent-id>"`).

**Content recording** — the documented sample enables prompt/completion capture:

```python
tracer = AzureAIOpenTelemetryTracer(
    connection_string=application_insights_connection_string,
    enable_content_recording=True,
)
```

---

## 5. AI Gateway — APIM v2 tier requirement

**Source:** [Configure AI Gateway in your Foundry resources](https://learn.microsoft.com/en-us/azure/foundry/configuration/enable-ai-api-management-gateway-portal)

> The API Management instance is in the **same Microsoft Entra tenant** and the same **subscription**
> as the Foundry resource.

> The API Management instance must be created in one of the **v2 tiers**.

> **Create new**: Creates a Basic v2 SKU instance.

---

## 6. APIM self-hosted gateway — tier availability

**Source:** [Feature-based comparison of the Azure API Management tiers](https://learn.microsoft.com/en-us/azure/api-management/api-management-features)

| Tier | Self-hosted gateway |
|---|---|
| Consumption | ❌ |
| Developer | ✅ (single node) |
| Basic | ❌ |
| **Basic v2** | ❌ |
| Standard | ❌ |
| **Standard v2** | ❌ |
| Premium | ✅ |
| **Premium v2** | ❌ |

**Source:** [API gateway in Azure API Management](https://learn.microsoft.com/en-us/azure/api-management/api-management-gateways-overview)

> **Self-hosted gateway** - In select service tiers, the self-hosted gateway is an optional,
> containerized version of the default managed gateway... It's useful for hybrid and multicloud
> scenarios where there's a requirement to run the gateways off of Azure in the same environments
> where API backends are hosted.

> Each self-hosted gateway is associated with a **Gateway** resource in a cloud-based API Management
> instance from which it receives configuration updates and communicates status.

A2A backend support: Classic ✅ | V2 ✅ | **Self-hosted ❌**

**Deduction.** Foundry's AI Gateway requires a v2 tier (§5); no v2 tier supports the self-hosted
gateway. The sets are disjoint, so the self-hosted gateway cannot serve as a Foundry AI Gateway.

**Limit of that deduction.** This proves only that you cannot push *the gateway* to the edge. It does
**not** prove the endpoint is unreachable. Relevant counter-evidence from the same tier matrix —
"Connect to backends isolated in virtual network": Standard v2 ✅, Premium v2 ✅. So a VNet-routable
on-premises backend (via VPN/ExpressRoute) is reachable.

---

## 7. Foundry Local — on-device model runtime

**Source:** [What is Foundry Local?](https://learn.microsoft.com/en-us/azure/ai-foundry/foundry-local/what-is-foundry-local)

> Foundry Local is an **end-to-end local AI solution for shipping applications that run entirely on
> the user's device**.

> User data never leaves the device, responses start immediately with zero network latency, and your
> app works offline. There are no per-token costs and no backend infrastructure to maintain.

> **Is an Azure subscription required?** No. Foundry Local runs entirely on local hardware. No Azure
> subscription is required.

> **Can Foundry Local run on a server?** Foundry Local is optimized for hardware-constrained devices
> where a single user accesses the model at a time. While you can technically install and run it on
> server hardware, it isn't designed as a server inference stack.

> **Optional local server** — An OpenAI-compatible web server for serving models to multiple
> processes, integrating with tools like LangChain, or experimenting through REST calls.

**Observation.** Every construct is a **model** construct: model catalog, model management, model
lifecycle, inference. There is no agent resource, registry, or lifecycle.

---

## 8. Agent identity — provisioned by Foundry Agent Service

**Source:** [Agent identity concepts in Microsoft Foundry](https://learn.microsoft.com/en-us/azure/foundry/agents/concepts/agent-identity)

> An *agent identity* is a specialized identity type in Microsoft Entra ID that's designed
> specifically for AI agents.

> **Microsoft Foundry automatically provisions and manages agent identities throughout the agent
> lifecycle.**

> When an agent invokes a tool, a multi-step OAuth 2.0 token exchange occurs automatically between
> Agent Service, Microsoft Entra ID, and the downstream resource.

**Observation.** Provisioning is tied to **Foundry Agent Service**, which does not run custom agents.
This supports the narrow claim ("not auto-provisioned, not surfaced in Assets") but **not** the broad
claim that a local agent can never hold an Entra Agent ID. Identity is asserted outbound by the agent,
so Azure reachability is not a precondition. Entra Agent ID / Agent 365 is a separate governance plane
and was not exhaustively researched here.

---

## 9. Foundry Local on Azure Local — a distinct product

**Source:** [What is Foundry Local on Azure Local?](https://learn.microsoft.com/en-us/azure/azure-sovereign-clouds/private/foundry-local/what-is-foundry-local-on-azure-local)

> Foundry Local on Azure Local brings AI inference to your Azure Local environment. Deploy and run AI
> models on an Arc-enabled Kubernetes cluster with Kubernetes-native operations.

> Foundry Local on Azure Local runs on an Arc-enabled Kubernetes cluster and is deployed as an Azure
> Arc extension. It uses an **operator-based control plane for model lifecycle management**.

> - The **Kubernetes inference operator** watches cluster state and reconciles model resources.
> - A **Model** resource defines model metadata...
> - A **ModelDeployment** resource defines runtime intent...

> Foundry Local is available in preview... Deployment is currently available by request during preview.

> Operate in disconnected environments where internet connectivity isn't available.

**Observations**
- This is Azure-managed local inference — but the management plane is **Azure Arc**, not the Foundry
  Control Plane.
- The managed objects are `Model` and `ModelDeployment`. Still models, not agents.
- Because cluster ingress is controllable, an *agent* on this cluster registered as a custom agent
  could have genuinely enforceable block/unblock — unlike an agent on a developer laptop.

---

## 10. Preview / GA status

**Source:** [What is Microsoft Foundry Control Plane?](https://learn.microsoft.com/en-us/azure/foundry/control-plane/overview)

> Items marked (preview) in this article are currently in public preview. This preview is provided
> without a service-level agreement, and we don't recommend it for production workloads.

> These features are currently available through the Foundry portal only.

**Honest limitation.** The docs carry the standard preview boilerplate but do not mark individual
Control Plane panes as preview in the retrieved text. This brief therefore does **not** assert a
definitive GA/preview status for the Control Plane or custom agent registration. Foundry Local on
Azure Local *is* explicitly preview and access-by-request (§9). Verify current status before relying
on any claim here.

---

## Corrections applied after adversarial review

Two independent models (GPT-5.6 Sol, Claude Opus 5) reviewed a draft of this analysis. Both returned
"publish with fixes." Substantive corrections made:

| Draft claim | Problem | Corrected to |
|---|---|---|
| Unqualified "No" | Ignored the working custom-agent path | "Not natively," with the narrow yes spelled out |
| "An agent on Foundry Local isn't a thing that exists" | Overstated; agents using local OpenAI-compatible endpoints are a normal pattern | No agent-shaped *resource* exists for the control plane to attach to |
| "No supported way to proxy to an unreachable endpoint" | **Non sequitur** — self-hosted gateway is one mechanism, not all of them | You can't push the gateway to the edge; you must bring the endpoint into Azure's reach. Options enumerated. |
| "Custom agents do NOT get an Entra Agent ID" | Over-read a UI-column table; Entra provisions identity, not Foundry | Not auto-provisioned by Foundry, not surfaced in Assets |
| "Governance theater" | Editorial verdict presented as a finding | Threat model stated; reader draws the conclusion |
| "Destroys Foundry Local's entire value proposition" | Absolute claim inviting counterexamples | Explicit table of what breaks vs. what survives |
| Block bypass framed as a local-agent issue | Applies to *all* custom agents | Real variable is backend network isolation |
| "Monitoring features = Foundry only" alongside "custom agents get runs/traces" | Apparent self-contradiction | Distinguished App Insights-derived metrics from Foundry evaluation features |
| Ambiguity of "Azure Foundry Local" unaddressed | Risked answering the wrong question | Both readings answered separately |
