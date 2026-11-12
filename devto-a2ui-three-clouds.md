---
title: "One A2UI 1.0 Agent on Google Cloud, AWS and Azure: The Spec Ports, the Framework Hooks Move"
published: false
description: "The same A2UI 1.0 currency agent built three times: Google ADK and Gemini, Strands and Amazon Nova on AgentCore Runtime, Microsoft Agent Framework and Azure OpenAI on Container Apps. What the three builds share file for file, where they differ, and why the A2UI half carried across clouds unchanged."
tags: a2ui, agents, multicloud, ai
cover_image: https://raw.githubusercontent.com/xbill9/a2ui-three-clouds/main/devto-cover.24a2d00b.jpg
---

This article compares three builds of one generative UI agent, one per cloud. A currency agent answers with A2UI 1.0 cards and charts, rendered by a Next.js CopilotKit front end over AG-UI. On Google Cloud it runs on Google ADK and Gemini, on AWS on Strands Agents and Amazon Nova with AgentCore Runtime and ECS Express Mode, and on Azure on Microsoft Agent Framework and Azure OpenAI with Azure Container Apps.

https://github.com/xbill9/a2ui-three-clouds

**The A2UI specification half of the app ported across all three clouds without a single changed line.** The charts catalog, the three server-side macros, the React renderer components and the ten-prompt test suite are byte-identical in all three repositories. What changed is the agent framework's glue: the A2UI tool, the hook that ends the turn after the UI, the hook that catches A2UI written as reply text, and the hosting. Every build rendered 100 of 100 test replies clean on its own cloud's model.

---

#### What Was Built Three Times?

| | Google Cloud | AWS | Azure |
| :--- | :--- | :--- | :--- |
| Agent framework | Google ADK `LlmAgent` | Strands Agents `Agent` | Microsoft Agent Framework `Agent` |
| Model | `gemini-3.8-flash` | `us.amazon.nova-2-lite-v1:0` on Bedrock | `gpt-5.4-mini` on Azure OpenAI |
| AG-UI adapter | `ag_ui_adk` | `ag-ui-strands` | `agent-framework-ag-ui` |
| Agent hosting | laptop; Cloud Build config for Cloud Run | AgentCore Runtime, protocol AGUI | Container App, internal ingress |
| UI hosting | laptop | ECS Express Mode | Container App, external ingress |
| Credentials | Gemini API key or Application Default Credentials | ECS task role, SigV4 | managed identities, Entra ID |

The three repositories:

- Google Cloud: https://github.com/xbill9/currency-claude-agui-a2ui1
- AWS: https://github.com/xbill9/currency-strands-agui-a2ui1
- Azure: https://github.com/xbill9/currency-maf-agui-a2ui1

All three pin the same A2UI and UI versions, read from each machine's `versions.txt`:

| Component | All three builds |
| :--- | :--- |
| `a2ui-agent-sdk` / `a2ui-core` | 0.11.0 / 0.6.0 |
| `@a2ui/react` / `@a2ui/web_core` | 0.15.0 / 0.15.0 |
| `next` / `react` / `@copilotkit/react-core` | 16.1.1 / 19.2.7 / 1.56.4 |
| `fastmcp` | 4.1.8 |

---

#### What Do the Three Demos Share?

`tools/compare_ports.py` reads each file from the three repositories' git `HEAD`, counts its lines, and counts changed lines (added plus removed) between each pair of builds with `difflib`:

```shell
python3 tools/compare_ports.py
```

```text
commits: {'gcp': '294caee', 'aws': '802cb1c', 'azure': 'bbee6ae'}
| Role | GCP lines | AWS lines | Azure lines | AWS vs GCP changed | Azure vs GCP changed | AWS vs Azure changed | identical |
| Charts catalog (JSON) | 95 | 95 | 95 | 0 | 0 | 0 | all three |
| Macros | 181 | 181 | 181 | 0 | 0 | 0 | all three |
| Reply-text rescue | 118 | 122 | 122 | 162 | 164 | 164 |  |
| Agent + A2UI tool | 176 | 165 | 204 | 253 | 326 | 131 |  |
| MCP server | 75 | 78 | 78 | 19 | 19 | 0 | AWS = Azure |
| AG-UI entry point | 68 | 41 | 34 | 89 | 76 | 39 |  |
| Macro tests | 99 | 129 | 138 | 38 | 47 | 47 |  |
| Rescue tests | 83 | 71 | 56 | 110 | 117 | 87 |  |
| Render suite | 93 | 93 | 93 | 0 | 0 | 0 | all three |
| UI app/page.tsx | 151 | 151 | 151 | 2 | 2 | 2 |  |
| UI app/layout.tsx | 23 | 23 | 23 | 0 | 0 | 0 | all three |
| UI app/globals.css | 24 | 24 | 24 | 0 | 0 | 0 | all three |
| UI app/api/copilotkit/[[...slug]]/route.ts | 50 | 55 | 53 | 11 | 9 | 10 |  |
| UI components/A2UICustomCatalog.tsx | 186 | 186 | 186 | 0 | 0 | 0 | all three |
| UI components/A2uiMessages.tsx | 52 | 52 | 52 | 0 | 0 | 0 | all three |
| UI components/a2uiResult.ts | 45 | 45 | 45 | 0 | 0 | 0 | all three |
| UI components/CopilotProvider.tsx | 18 | 18 | 18 | 0 | 0 | 0 | all three |
| UI components/currency.tsx | 57 | 57 | 57 | 0 | 0 | 0 | all three |
| UI components/weather.tsx | 69 | 69 | 69 | 0 | 0 | 0 | all three |
| UI components/proverbs.tsx | 47 | 47 | 47 | 0 | 0 | 0 | all three |
| UI app/api/agentcore/route.ts | - | 99 | - | - | - | - |  |

12 of 21 roles byte-identical in all three repos
lines in byte-identical files: 890
gcp: 1710 lines over the listed roles; byte-identical share 890/1710 = 52%
aws: 1801 lines over the listed roles; byte-identical share 890/1801 = 49%
azure: 1726 lines over the listed roles; byte-identical share 890/1726 = 52%
```

The files that never changed are the ones the A2UI specification defines: the charts catalog, the macros that expand into catalog components, the renderer that draws them, and the test that checks a reply rendered. `page.tsx` differs in one line, the subtitle naming the framework and model.

---

#### Shared 1 — The Catalog Is a Contract

`custom_catalog.json` declares the currency charts catalog, `https://a2ui.org/catalog/currency-charts/v1/catalog.json`, with `LineChart` and `BarChart`. `A2UICustomCatalog.tsx` implements the same ids and props in React. The agent validates every payload against this catalog and the Basic 1.0 catalog before sending, and the browser renders only what the two catalogs list.

Both files are byte-identical in all three builds. The catalog describes components; it names no framework, model or cloud, so nothing in it had a reason to change.

---

#### Shared 2 — The Macros Port as Plain Python

`macros.py` is 181 lines in each build, byte-identical. `RateCard`, `RateHistoryChart` and `RateComparison` are `@macro` functions from `a2ui-agent-sdk`: the model writes one line, such as `root = RateCard("USD", "EUR", 250)`, and the server fetches the rate from the Frankfurter API and builds Basic catalog components.

| Macro | The model writes | The server builds |
| :--- | :--- | :--- |
| `RateCard` | `root = RateCard("USD", "EUR", 250)` | heading, rate line, divider, source line in a Card |
| `RateHistoryChart` | `root = RateHistoryChart("USD", "JPY", 90)` | heading, LineChart, low/high/latest line |
| `RateComparison` | `root = RateComparison("USD", ["EUR","GBP","JPY","CAD"])` | one rate per currency and a BarChart of the change |

A macro takes currency codes and an amount and returns components. It calls no model and no framework, which is why the same file runs under ADK, Strands and Agent Framework.

---

#### Shared 3 — One Pipeline Between the Model and the Browser

All three builds build the same A2UI objects from the same SDK calls. `tools/compare_functions.py` compares each top-level name in the three `agent.py` files. The rows for the A2UI pipeline:

```shell
python3 tools/compare_functions.py
```

```text
| Name | GCP | AWS | Azure | AWS == Azure | GCP == AWS |
| BASE_CATALOGS | x | x | x | yes | yes |
| INFERENCE_CATALOGS | x | x | x | yes | yes |
| ROLE_INSTRUCTION | x | x | x | yes |  |
| _message_adapter | x | x | x | yes | yes |
| a2ui_processor | x | x | x | yes | yes |
| compile_a2ui |  | x | x | yes |  |
| macro_expander | x | x | x | yes | yes |
| system_prompt |  | x | x | yes |  |
```

The catalogs, the macro expander and the request processor are the same lines of code in all three. The pipeline they make is the same everywhere:

1. The model writes A2UI Express and passes it to `send_a2ui_json_to_client`.
2. The tool compiles the Express block and validates it against the catalogs the model sees, which include the macros.
3. The macro expander runs the macros on the server.
4. The tool validates the expanded messages again against the catalogs the browser implements.
5. The tool result carries `validated_a2ui_json`, and the browser renders it with `@a2ui/react`.

---

#### Shared 4 — The Same Test, the Same Bar

`render_suite.py` is byte-identical in the three repositories. It sends ten prompts ten times each through the UI's CopilotKit endpoint. A UI prompt passes when A2UI rendered and no raw `<a2ui` text reached the chat; the weather question passes on a text refusal. One prompt asks the model to write A2UI as reply text and call no tool, to test each framework's catch for it.

| Build | Where | Model | Clean renders |
| :--- | :--- | :--- | :--- |
| Google Cloud | laptop | `gemini-3.8-flash` | 100 of 100 |
| Google Cloud | laptop | `gemini-2.5-flash` | 100 of 100 |
| AWS | laptop | `us.amazon.nova-2-lite-v1:0` | 100 of 100 |
| AWS | ECS Express Mode → AgentCore Runtime | `us.amazon.nova-2-lite-v1:0` | 100 of 100 |
| Azure | laptop | `gpt-5.4-mini` | 100 of 100 |
| Azure | Container Apps, first run | `gpt-5.4-mini` | 100 of 100 |
| Azure | Container Apps, second run | `gpt-5.4-mini` | 100 of 100 |

---

#### How Are They Different?

Everything that changed sits where the A2UI pipeline meets an agent framework or a cloud. Each section below names the job and how each build does it.

---

#### Difference 1 — The A2UI Tool

The A2UI SDK ships an ADK adapter, `a2ui-adk`. The Google Cloud build subclasses its `SendA2uiToClientToolset` and adds the macro expansion and second validation in `_parse_payload`.

Strands and Agent Framework have no adapter, so each build writes the tool as a plain function around `compile_a2ui`. That function is identical in the AWS and Azure builds; only the decorator changes:

```python
# AWS, Strands
@tool(name=TOOL_NAME, context=True)
def send_a2ui_json_to_client(a2ui_payload: str, tool_context: ToolContext) -> str:

# Azure, Agent Framework
@tool(name=TOOL_NAME)
def send_a2ui_json_to_client(
    a2ui_payload: Annotated[str, Field(description="The A2UI block to send to the client, ...")],
) -> str:
```

```python
def compile_a2ui(payload: str) -> list[dict]:
    ...
    validate_payload(a2ui_processor.active_catalogs, messages)
    typed = [_message_adapter.validate_python(m) for m in messages]
    expanded = macro_expander.transform_to_transport(typed)
    wire = [m.model_dump(by_alias=True, exclude_none=True) for m in expanded]
    validate_payload(BASE_CATALOGS, wire)
    return wire
```

The system prompt follows the same split. ADK's toolset appends the A2UI prompt on its own. The AWS and Azure builds assemble it in `system_prompt()`, identical in both: the role, then `generate_base_rules()`, `generate_catalog_instructions(include_schema=True)` and `generate_examples()` from the SDK.

---

#### Difference 2 — Ending the Turn After the UI

The card is the whole answer, so each build stops the model after a successful UI send. A rejected payload goes back to the model as a tool error in all three.

| Build | Hook |
| :--- | :--- |
| Google Cloud | `skip_summarization`, set by the `a2ui-adk` toolset |
| AWS | `tool_context.agent.cancel(after_current_tools=True)` inside the tool, on success |
| Azure | `EndTurnAfterUi` function middleware raises `MiddlewareTermination` |

Azure also turns off `allow_multiple_tool_calls`. Two parallel UI sends in one model turn create the same surface twice, and the renderer rejects the second.

---

#### Difference 3 — Catching A2UI Written as Reply Text

A model sometimes writes the A2UI block into its reply. Each build turns that block into a call to the UI tool, at the place its framework exposes the model's output:

| Build | Hook |
| :--- | :--- |
| Google Cloud | `after_model_callback=rescue_a2ui_text` writes a function call |
| AWS | `RescuingBedrockModel` wraps the Bedrock ConverseStream and emits a `toolUse` |
| Azure | `A2uiRescueMiddleware` chat middleware rewrites the response stream to `tool_calls` |

This is the most rewritten file: 162 to 164 changed lines between any two builds of a file about 120 lines long. The suite's reply-text prompt rendered as a card in 10 of 10 runs in every suite run on every build. On Azure, the same request sent twice by hand from the browser rendered once; the other time the model answered in text that A2UI goes through the tool.

---

#### Difference 4 — The MCP Server

`get_exchange_rate` is the same FastMCP server in all three. On Google Cloud it runs as its own process over HTTP on port 8080, and the Cloud Build config deploys it as a second Cloud Run service. On AWS and Azure the agent starts it as a stdio child, so the agent ships as one unit. The 19 changed lines add the stdio branch:

```python
# stdio when the agent starts this server as a child process; HTTP otherwise.
if os.getenv("MCP_TRANSPORT") == "stdio":
    mcp.run(transport="stdio", show_banner=False)
else:
    ...
```

The AWS and Azure MCP servers are byte-identical.

---

#### Difference 5 — Hosting and Identity

| Job | Google Cloud | AWS | Azure |
| :--- | :--- | :--- | :--- |
| Agent endpoint | `/` on port 8008 (AG-UI), A2A on 10000 | `/invocations`, `/ping` on 8080 | `/invocations`, `/ping` on 8080 |
| UI to agent | `AGENT_URL`, same machine | SigV4 proxy in the Next.js server | `http://currency-maf-agent/invocations`, inside the environment |
| Agent to model | API key or Application Default Credentials | ECS task role and AgentCore runtime role | managed identity, *Cognitive Services OpenAI User* |
| Deploy | `cloudbuild.yaml` to Cloud Run | `agentcore deploy` and `infra/deploy_ui.sh` | `infra/deploy.sh` |

AWS has the one cloud-only file in the table: `app/api/agentcore/route.ts`, 99 lines that sign each AG-UI run with SigV4 and keep AWS credentials out of the browser. AgentCore's endpoint contract, `/invocations` and `/ping` on 8080, is also what the Azure build serves, so the two agents share an entry point shape. The copilotkit route differs by 9 to 11 lines between builds, all in where `AGENT_URL` points.

---

#### 🔎 Tip: Write the A2UI Tool Once for Frameworks Without an Adapter

`compile_a2ui` takes a string and returns validated wire messages. It touches no framework type, so it moved from Strands to Agent Framework byte for byte. Keep it apart from the decorator and from the end-of-turn logic, and the next framework port is a new decorator and a new hook.

---

#### 🔎 Tip: Keep the Catalog Id Matched on Both Sides

The charts catalog id and props must match between `custom_catalog.json` on the agent and `A2UICustomCatalog.tsx` in the browser. Copy both files together when porting. All three builds use `https://a2ui.org/catalog/currency-charts/v1/catalog.json`.

---

#### Compare and Contrast

| | Google Cloud | AWS | Azure |
| :--- | :--- | :--- | :--- |
| Catalog, macros, renderer, render suite | shared | shared | shared |
| A2UI tool | `a2ui-adk` toolset subclass | `compile_a2ui` + `@tool` | `compile_a2ui` + `@tool` |
| End the turn after the UI | `skip_summarization` (`a2ui-adk`) | `agent.cancel(...)` | `MiddlewareTermination` |
| Reply-text A2UI | `after_model_callback` | ConverseStream wrapper | chat middleware |
| MCP server | HTTP, separate service | stdio child | stdio child |
| Cloud-specific glue in the UI | none | SigV4 proxy, 99 lines | none |
| Keys in the deployment | API key or ADC | none, IAM roles | none, managed identities |
| Clean renders, 10 prompts × 10 runs | 100 of 100 on each of two models | 100 of 100 locally and deployed | 100 of 100 locally and in two deployed runs |

---

#### So, Which One?

Pick the cloud where the rest of the system lives. The A2UI half moves with you: the catalog, the macros, the React renderer and the test suite are the same files on all three, and each build passed the same suite on its own cloud's model.

Google ADK has the shortest path, since the A2UI SDK ships an ADK adapter. AWS adds the most cloud glue, a SigV4 proxy in the UI server, and gets an agent runtime that takes an AG-UI app as is. Azure needs no proxy: the two Container Apps talk inside one environment and managed identities replace every key.

Budget the porting time for the two framework hooks, ending the turn after the UI and catching reply-text A2UI, and for the hosting.

---

#### Summary

The goal of this article was to compare one A2UI 1.0 agent built on Google Cloud, AWS and Azure: what the three builds share and where they differ. The key to the solution was keeping the A2UI specification half whole, with the catalog, the macros and the renderer written once, and moving only the framework hooks, the model client and the hosting. The results were:

- 🟢 12 of 21 compared files are byte-identical in all three repositories, 890 lines, about half of each build
- 🟢 The charts catalog, the three macros, the React A2UI components and the render suite did not change a line
- 🟢 `compile_a2ui` and `system_prompt` moved from Strands to Agent Framework byte for byte
- 🟢 Every build rendered 100 of 100 suite replies clean on its own cloud's model, and the deployed AWS and Azure apps matched their laptop runs
- ⚠️ Each framework needs its own hook to end the turn after the UI and its own catch for reply-text A2UI; the reply-text handler is the most rewritten file
- ⚠️ A2UI requested as reply text rendered 1 of 2 when sent by hand on Azure; the other reply was text
- ❌ Only ADK has an A2UI SDK adapter; Strands and Agent Framework need the tool written by hand

Scope: three builds measured separately, each on its own model and day. Google Cloud on a laptop with `gemini-3.8-flash` and `gemini-2.5-flash` on 2026-11-11; AWS in us-east-1 with `us.amazon.nova-2-lite-v1:0` at temperature 0.2 on 2026-11-11; Azure in eastus2 with `gpt-5.4-mini` on 2026-11-12. Ten runs per prompt for each run listed. The models differ between builds, so the render results show that each build works, and compare no models. File comparisons read git `HEAD` at the commits printed above.

The strategy for porting a generative UI agent across Google Cloud, AWS and Azure was validated with an incremental step by step approach.

---

#### References

- This comparison, its scripts and evidence: https://github.com/xbill9/a2ui-three-clouds
- Google Cloud build (ADK, Gemini): https://github.com/xbill9/currency-claude-agui-a2ui1
- AWS build (Strands, Nova, AgentCore, ECS Express Mode): https://github.com/xbill9/currency-strands-agui-a2ui1
- Azure build (Agent Framework, Azure OpenAI, Container Apps): https://github.com/xbill9/currency-maf-agui-a2ui1
- What Changes With the A2UI 1.0 Release: https://dev.to/gde/what-changes-with-the-a2ui-10-release-31eo
- A2UI 1.0 on AWS: https://dev.to/aws-builders/a2ui-10-on-aws-a-strands-currency-agent-with-amazon-nova-agentcore-runtime-and-ecs-express-mode-2pgl
- A2UI v1.0 specification: https://a2ui.org/specification/v1.0-a2ui/
- AG-UI: https://docs.ag-ui.com
- CopilotKit: https://github.com/CopilotKit/CopilotKit
- Google Agent Development Kit: https://github.com/google/adk-python
- Strands Agents: https://strandsagents.com
- Microsoft Agent Framework: https://github.com/microsoft/agent-framework
- Frankfurter API: https://www.frankfurter.dev
