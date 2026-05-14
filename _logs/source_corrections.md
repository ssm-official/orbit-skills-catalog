# Source corrections

Repos from the §5 seed list that didn't resolve at their documented URL.
Each entry documents the original URL, what was found, and the replacement
(if any) that was substituted into the discovery feed.

## 2026-05-14 — initial seed verify pass

### `https://github.com/Shopify/dev-mcp`  →  **dropped, no clean replacement**
- Original lookup: 404.
- Closest hits: `Shopify/dev-mcp-gemini-cli` (Gemini CLI setup, 30★, 2026-04) and
  `Shopify/consumer-agent-mcp` (4★, 2025-12) — neither is the storefront/admin
  MCP server we're after.
- The Shopify community MCPs (`GeLi2001/shopify-mcp`, `amir-bengherbi/shopify-mcp-server`)
  remain in the seed list and will fill this slot if they pass audit.

### `https://github.com/duffelhq/duffel-api-node`  →  **renamed**
- Now `https://github.com/duffelhq/duffel-api-javascript` (MIT, 53★, active).
- Added to supplemental seeds as `personal.travel.flights-duffel-sdk`.
- Also discovered `duffelhq/duffel-api-python` (20★, last commit 2024-09) — added too,
  flagged as low-maintenance.

### `https://github.com/pipedrive/client-python`  →  **dropped, no replacement**
- 404. The `pipedrive` org has no public Python SDK at this time.
- The Pipedrive Node SDK (`pipedrive/client-nodejs`) remains in the seed list
  and will represent Pipedrive on Orbit if it passes audit.

### `https://github.com/arjunkmrm/sg-lta-mcp`  →  **dropped, no replacement**
- 404. Repo not findable via GitHub search by name or topic.
- Singapore LTA transit slot will be filled if a substitute surfaces during
  aggregator crawl; otherwise documented as a gap.

### `https://github.com/avabuildsdata/mcp-us-business-data`  →  **dropped, no replacement**
- 404. Owner org does not exist on GitHub.
- US business-data slot remains open; will check for SEC EDGAR / OpenCorporates
  client wrappers during aggregator crawl.
