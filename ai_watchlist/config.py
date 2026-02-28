"""
AI Company Watchlist Configuration
"""

COMPANIES = [
    {
        "ticker": "NVDA",
        "name": "NVIDIA",
        "github_orgs": ["NVIDIA", "nvidia"],
        "sec_cik": "1045810",
    },
    {
        "ticker": "MSFT",
        "name": "Microsoft",
        "github_orgs": ["microsoft"],
        "sec_cik": "0000789019",
    },
    {
        "ticker": "GOOGL",
        "name": "Alphabet",
        "github_orgs": ["google", "tensorflow", "google-research"],
        "sec_cik": "0001652044",
    },
    {
        "ticker": "AMZN",
        "name": "Amazon",
        "github_orgs": ["aws", "amazon-science"],
        "sec_cik": "0001018724",
    },
    {
        "ticker": "META",
        "name": "Meta Platforms",
        "github_orgs": ["facebookresearch", "facebookincubator"],
        "sec_cik": "0001326801",
    },
    {
        "ticker": "TSM",
        "name": "Taiwan Semiconductor",
        "github_orgs": [],
        "sec_cik": "0001046179",
    },
    {"ticker": "AVGO", "name": "Broadcom", "github_orgs": [], "sec_cik": "0001730168"},
    {
        "ticker": "AMD",
        "name": "AMD",
        "github_orgs": ["ROCmSoftwarePlatform", "AMDResearch"],
        "sec_cik": "0000002488",
    },
    {
        "ticker": "AAPL",
        "name": "Apple",
        "github_orgs": ["apple"],
        "sec_cik": "0000320193",
    },
    {
        "ticker": "ORCL",
        "name": "Oracle",
        "github_orgs": ["oracle"],
        "sec_cik": "0001341439",
    },
    {"ticker": "IBM", "name": "IBM", "github_orgs": ["IBM"], "sec_cik": "0000051143"},
    {
        "ticker": "PLTR",
        "name": "Palantir",
        "github_orgs": ["palantir"],
        "sec_cik": "0001321655",
    },
    {
        "ticker": "NOW",
        "name": "ServiceNow",
        "github_orgs": ["ServiceNow"],
        "sec_cik": "0001373715",
    },
    {
        "ticker": "SNOW",
        "name": "Snowflake",
        "github_orgs": ["snowflakedb"],
        "sec_cik": "0001640147",
    },
    {
        "ticker": "DDOG",
        "name": "Datadog",
        "github_orgs": ["DataDog"],
        "sec_cik": "0001567512",
    },
    {
        "ticker": "CRM",
        "name": "Salesforce",
        "github_orgs": ["forcedotcom", "salesforce"],
        "sec_cik": "0001108524",
    },
    {
        "ticker": "ADBE",
        "name": "Adobe",
        "github_orgs": ["adobe"],
        "sec_cik": "0000796343",
    },
    {
        "ticker": "INTU",
        "name": "Intuit",
        "github_orgs": ["Intuit"],
        "sec_cik": "0000896839",
    },
    {
        "ticker": "CRWD",
        "name": "CrowdStrike",
        "github_orgs": ["CrowdStrike"],
        "sec_cik": "0001535527",
    },
    {
        "ticker": "AI",
        "name": "C3.ai",
        "github_orgs": ["c3aidatalab"],
        "sec_cik": "0001829209",
    },
]

INDICATOR_WEIGHTS = {
    "sec_filings": 0.25,
    "job_postings": 0.15,
    "github_activity": 0.10,
    "exec_appearances": 0.15,
    "employee_sentiment": 0.10,
    "govt_contracts": 0.25,
}

AI_KEYWORDS = [
    "artificial intelligence",
    "machine learning",
    "deep learning",
    "neural network",
    "LLM",
    "large language model",
    "generative AI",
    "GPT",
    "transformer",
    "computer vision",
    "NLP",
    "natural language processing",
    "AI infrastructure",
    "GPU computing",
    "tensor",
    "inference",
    "training",
    "MLOps",
    "AI platform",
]

SIGNAL_THRESHOLDS = {
    "strong_buy": 2.0,
    "buy": 1.0,
    "neutral_upper": 1.0,
    "neutral_lower": -1.0,
    "sell": -1.0,
    "strong_sell": -2.0,
}

ROLLING_WEEKS = 4
