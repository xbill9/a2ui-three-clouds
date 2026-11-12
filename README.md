# A2UI 1.0 on three clouds

A comparison of one A2UI 1.0 currency agent built on Google Cloud, AWS and Azure, and the dev.to article that reports it: `devto-a2ui-three-clouds.md`.

| Build | Repository |
| :--- | :--- |
| Google Cloud: Google ADK, Gemini | https://github.com/xbill9/currency-claude-agui-a2ui1 |
| AWS: Strands Agents, Amazon Nova, AgentCore Runtime, ECS Express Mode | https://github.com/xbill9/currency-strands-agui-a2ui1 |
| Azure: Microsoft Agent Framework, Azure OpenAI, Container Apps | https://github.com/xbill9/currency-maf-agui-a2ui1 |

## Reproduce the comparison

Clone the three repositories into your home directory, then:

```shell
python3 tools/compare_ports.py      # file-by-file line counts and changed lines, from each repo's git HEAD
python3 tools/compare_functions.py  # top-level names in the three agent.py files
```

`evidence/` holds both outputs and the render suite results and version lists copied from each build's own evidence.
