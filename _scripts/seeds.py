"""Seed list — every starter repo from §5 of the master prompt.

Each entry: (source_url, kind, proposed_slot, track_hint, notes)
- kind: mcp_server | sdk_wrapper | tool_folder | aggregator
- proposed_slot: best-fit taxonomy leaf (subject to revision after verify)
- track_hint: personal | merchant | both

Aggregator entries are awesome-lists we crawl to extract more candidates;
they themselves do not become catalog rows.

DO NOT add entries you have not verified exist. Run cli_verify.py to confirm.
"""

SEEDS = [
    # --- §5.1 MCP foundations / aggregators ---
    ("https://github.com/modelcontextprotocol/servers", "mcp_server", "_aggregator.mcp_reference", "both", "Anthropic reference MCP servers; crawl subdirs"),
    ("https://github.com/modelcontextprotocol/python-sdk", "tool_folder", "_meta.mcp_python_sdk", "both", "For wrappers we write ourselves"),
    ("https://github.com/modelcontextprotocol/typescript-sdk", "tool_folder", "_meta.mcp_ts_sdk", "both", "For wrappers we write ourselves"),
    ("https://github.com/punkpeye/awesome-mcp-servers", "aggregator", "_aggregator", "both", "Large community list"),
    ("https://github.com/wong2/awesome-mcp-servers", "aggregator", "_aggregator", "both", "Second curator"),
    ("https://github.com/appcypher/awesome-mcp-servers", "aggregator", "_aggregator", "both", "Third curator"),
    ("https://github.com/TensorBlock/awesome-mcp-servers", "aggregator", "_aggregator", "both", "Categorized directory"),
    ("https://github.com/tolkonepiu/best-of-mcp-servers", "aggregator", "_aggregator", "both", "Ranked list"),
    ("https://github.com/anthropics/skills", "tool_folder", "_aggregator.anthropic_skills", "both", "Anthropic reference Claude Skills"),

    # --- §5.2 vendor-published official MCP servers ---
    ("https://github.com/stripe/agent-toolkit", "mcp_server", "merchant.finance.stripe-agent", "merchant", "Stripe agent toolkit, includes MCP"),
    ("https://github.com/github/github-mcp-server", "mcp_server", "merchant.devops.github-mcp", "merchant", "Official GitHub MCP"),
    ("https://github.com/cloudflare/mcp-server-cloudflare", "mcp_server", "merchant.devops.cloudflare-mcp", "merchant", "Official Cloudflare MCP"),
    ("https://github.com/getsentry/sentry-mcp", "mcp_server", "merchant.devops.sentry-mcp", "merchant", "Official Sentry MCP"),
    ("https://github.com/Shopify/dev-mcp", "mcp_server", "merchant.ecommerce.shopify-dev-mcp", "merchant", "Official Shopify dev tooling MCP"),
    ("https://github.com/elevenlabs/elevenlabs-mcp", "mcp_server", "both.creative.elevenlabs-tts", "both", "Official ElevenLabs MCP"),

    # --- §5.3 personal-track seeds ---
    # travel
    ("https://github.com/ravinahp/flights-mcp", "mcp_server", "personal.travel.flights-duffel", "personal", "Duffel flight search MCP"),
    ("https://github.com/duffelhq/duffel-api-node", "sdk_wrapper", "personal.travel.flights-duffel-sdk", "personal", "Duffel Node SDK"),
    ("https://github.com/hrishabhn/flight-mcp", "mcp_server", "personal.travel.flights-skyscanner", "personal", "Skyscanner flight MCP"),
    ("https://github.com/esakrissa/hotels_mcp_server", "mcp_server", "personal.travel.hotels-booking", "personal", "Booking.com hotels MCP"),
    ("https://github.com/skarlekar/mcp_travelassistant", "mcp_server", "personal.travel.travelassistant-suite", "personal", "Travel suite MCP"),
    ("https://github.com/gs-ysingh/travel-mcp-server", "mcp_server", "personal.travel.travel-misc", "personal", "Travel MCP"),
    ("https://github.com/Cyreslab-AI/flightradar24-mcp-server", "mcp_server", "personal.travel.flight-status-fr24", "personal", "FlightRadar24 MCP — check ToS"),
    ("https://github.com/sunsetcoder/flightradar24-mcp-server", "mcp_server", "personal.travel.flight-status-fr24-alt", "personal", "FlightRadar24 MCP alt — check ToS"),
    ("https://github.com/r-huijts/ns-mcp-server", "mcp_server", "personal.travel.rail-nl", "personal", "NL Dutch Railways MCP"),
    ("https://github.com/Fabsbags/sbb-mcp", "mcp_server", "personal.travel.rail-ch", "personal", "Swiss SBB rail MCP"),
    ("https://github.com/Joooook/12306-mcp", "mcp_server", "personal.travel.rail-cn", "personal", "China rail MCP"),
    ("https://github.com/arjunkmrm/sg-lta-mcp", "mcp_server", "personal.travel.transit-sg", "personal", "Singapore LTA MCP"),
    ("https://github.com/kennyckk/mcp_hkbus", "mcp_server", "personal.travel.transit-hk", "personal", "Hong Kong bus MCP"),
    ("https://github.com/pab1it0/tripadvisor-mcp", "mcp_server", "personal.travel.reviews-tripadvisor", "personal", "TripAdvisor reviews MCP"),
    ("https://github.com/birariro/agoda-review-mcp", "mcp_server", "personal.travel.reviews-agoda", "personal", "Agoda reviews MCP"),
    ("https://github.com/googlemaps/google-maps-services-js", "sdk_wrapper", "both.maps.google-maps", "both", "Official Google Maps JS client"),
    ("https://github.com/googlemaps/google-maps-services-python", "sdk_wrapper", "both.maps.google-maps-py", "both", "Official Google Maps Python client"),
    ("https://github.com/mapbox/mapbox-sdk-js", "sdk_wrapper", "both.maps.mapbox", "both", "Official Mapbox JS SDK"),
    # weather
    # (open-meteo, OpenWeatherMap, weather.gov via clients found in discovery phase)

    # shopping
    ("https://github.com/easypost/easypost-node", "sdk_wrapper", "both.shipping.easypost", "both", "EasyPost Node SDK"),
    ("https://github.com/easypost/easypost-python", "sdk_wrapper", "both.shipping.easypost-py", "both", "EasyPost Python SDK"),

    # finance/markets
    ("https://github.com/ccxt/ccxt", "sdk_wrapper", "personal.finance.crypto-ccxt", "personal", "Unified crypto exchange API"),
    ("https://github.com/alchemyplatform/alchemy-mcp-server", "mcp_server", "personal.finance.crypto-alchemy", "personal", "Alchemy on-chain MCP"),
    ("https://github.com/ferdousbhai/investor-agent", "mcp_server", "personal.finance.investor-agent", "personal", "Investor agent MCP"),
    ("https://github.com/plaid/plaid-python", "sdk_wrapper", "both.finance.plaid", "both", "Plaid official Python SDK"),
    ("https://github.com/plaid/plaid-node", "sdk_wrapper", "both.finance.plaid-node", "both", "Plaid official Node SDK"),

    # productivity / mail / notes
    ("https://github.com/googleapis/google-api-nodejs-client", "sdk_wrapper", "both.productivity.google-apis-js", "both", "Official Google APIs Node client"),
    ("https://github.com/googleapis/google-api-python-client", "sdk_wrapper", "both.productivity.google-apis-py", "both", "Official Google APIs Python client"),
    ("https://github.com/makenotion/notion-sdk-js", "sdk_wrapper", "both.productivity.notion", "both", "Official Notion JS SDK"),
    ("https://github.com/linear/linear", "sdk_wrapper", "both.productivity.linear", "both", "Linear SDK monorepo"),

    # search / fetch / web
    ("https://github.com/microsoft/playwright-mcp", "mcp_server", "merchant.devops.playwright-mcp", "merchant", "Microsoft Playwright MCP"),
    ("https://github.com/browserbase/mcp-server-browserbase", "mcp_server", "merchant.devops.browserbase-mcp", "merchant", "Browserbase MCP"),

    # creative / AI media
    ("https://github.com/replicate/replicate-python", "sdk_wrapper", "both.creative.replicate-py", "both", "Replicate Python SDK"),
    ("https://github.com/replicate/replicate-javascript", "sdk_wrapper", "both.creative.replicate-js", "both", "Replicate JS SDK"),
    ("https://github.com/huggingface/huggingface_hub", "sdk_wrapper", "both.creative.huggingface", "both", "Hugging Face hub client"),
    ("https://github.com/openai/openai-python", "sdk_wrapper", "both.creative.openai-py", "both", "OpenAI Python SDK"),
    ("https://github.com/openai/openai-node", "sdk_wrapper", "both.creative.openai-node", "both", "OpenAI Node SDK"),
    ("https://github.com/anthropics/anthropic-sdk-python", "sdk_wrapper", "both.creative.anthropic-py", "both", "Anthropic Python SDK"),
    ("https://github.com/anthropics/anthropic-sdk-typescript", "sdk_wrapper", "both.creative.anthropic-ts", "both", "Anthropic TS SDK"),
    ("https://github.com/danielgatis/rembg", "tool_folder", "both.creative.rembg", "both", "Background removal (self-host)"),

    # --- §5.4 merchant-track seeds ---
    # CRM
    ("https://github.com/HubSpot/hubspot-api-nodejs", "sdk_wrapper", "merchant.crm.hubspot-node", "merchant", "Official HubSpot Node SDK"),
    ("https://github.com/HubSpot/hubspot-api-python", "sdk_wrapper", "merchant.crm.hubspot-py", "merchant", "Official HubSpot Python SDK"),
    ("https://github.com/jsforce/jsforce", "sdk_wrapper", "merchant.crm.salesforce-jsforce", "merchant", "Salesforce community SDK"),
    ("https://github.com/pipedrive/client-nodejs", "sdk_wrapper", "merchant.crm.pipedrive-node", "merchant", "Pipedrive Node SDK"),
    ("https://github.com/pipedrive/client-python", "sdk_wrapper", "merchant.crm.pipedrive-py", "merchant", "Pipedrive Python SDK"),
    ("https://github.com/Meerkats-Ai/findymail-mcp-server", "mcp_server", "merchant.crm.findymail", "merchant", "Findymail email finder MCP"),

    # marketing / email infra
    ("https://github.com/mailchimp/mailchimp-marketing-node", "sdk_wrapper", "merchant.marketing.mailchimp-node", "merchant", "Mailchimp Node SDK"),
    ("https://github.com/mailchimp/mailchimp-marketing-python", "sdk_wrapper", "merchant.marketing.mailchimp-py", "merchant", "Mailchimp Python SDK"),
    ("https://github.com/resend/resend-node", "sdk_wrapper", "both.marketing.resend-node", "both", "Resend Node SDK"),
    ("https://github.com/resend/resend-python", "sdk_wrapper", "both.marketing.resend-py", "both", "Resend Python SDK"),
    ("https://github.com/sendgrid/sendgrid-nodejs", "sdk_wrapper", "merchant.marketing.sendgrid-node", "merchant", "Twilio SendGrid Node SDK"),
    ("https://github.com/sendgrid/sendgrid-python", "sdk_wrapper", "merchant.marketing.sendgrid-py", "merchant", "Twilio SendGrid Python SDK"),
    ("https://github.com/twilio/twilio-node", "sdk_wrapper", "both.comms.twilio-node", "both", "Twilio Node SDK"),
    ("https://github.com/twilio/twilio-python", "sdk_wrapper", "both.comms.twilio-py", "both", "Twilio Python SDK"),

    # customer support
    ("https://github.com/zendesk/zendesk_api_client_rb", "sdk_wrapper", "merchant.support.zendesk-rb", "merchant", "Zendesk Ruby SDK — note Ruby"),
    ("https://github.com/intercom/python-intercom", "sdk_wrapper", "merchant.support.intercom-py", "merchant", "Intercom Python (verify maintenance)"),

    # commerce / payments
    ("https://github.com/stripe/stripe-python", "sdk_wrapper", "merchant.finance.stripe-py", "merchant", "Official Stripe Python SDK"),
    ("https://github.com/stripe/stripe-node", "sdk_wrapper", "merchant.finance.stripe-node", "merchant", "Official Stripe Node SDK"),
    ("https://github.com/square/square-nodejs-sdk", "sdk_wrapper", "merchant.finance.square-node", "merchant", "Square Node SDK"),
    ("https://github.com/square/square-python-sdk", "sdk_wrapper", "merchant.finance.square-py", "merchant", "Square Python SDK"),

    # shopify community MCPs
    ("https://github.com/GeLi2001/shopify-mcp", "mcp_server", "merchant.ecommerce.shopify-mcp", "merchant", "Community Shopify MCP — vet carefully"),
    ("https://github.com/amir-bengherbi/shopify-mcp-server", "mcp_server", "merchant.ecommerce.shopify-mcp-alt", "merchant", "Alt community Shopify MCP"),

    # devops / sources
    ("https://github.com/octokit/octokit.js", "sdk_wrapper", "merchant.devops.octokit-js", "merchant", "Octokit (GitHub) JS"),
    ("https://github.com/PyGithub/PyGithub", "sdk_wrapper", "merchant.devops.pygithub", "merchant", "PyGithub"),

    # research / public data
    ("https://github.com/avabuildsdata/mcp-us-business-data", "mcp_server", "merchant.research.us-business", "merchant", "17 US state SoS DBs MCP"),

    # PM
    ("https://github.com/YajieQi123/mcp-server-monday-qi", "mcp_server", "merchant.ops.monday-com", "merchant", "Monday.com MCP"),

    # inventory
    ("https://github.com/ReplenishRadar/MCP", "mcp_server", "merchant.ecommerce.replenish-radar", "merchant", "Multi-channel inventory MCP"),

    # meta — pipedream
    ("https://github.com/PipedreamHQ/pipedream", "tool_folder", "_meta.pipedream", "both", "8000+ prebuilt actions; meta-source"),
]
