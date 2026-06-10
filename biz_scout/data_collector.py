import logging
import asyncio
import os
import time

import microcore as mc

from biz_scout.bootstrap.perplexity_connection import perplexity
from .company import safe_file_name

PAGES_PER_SUBJECT = os.getenv("PAGES_PER_SUBJECT", 2)
MAX_CONCURRENT_TASKS = os.getenv("MAX_CONCURRENT_TASKS", 5)

SUBJECTS = {
    "news": "Latest news and developments (recent news, press releases, product launches, executive changes)",
    "legal_identity": "General info, Legal identity and registration (legal name, entity type, registration numbers, jurisdiction, incorporation date)",
    "structure": "Corporate structure and ownership (parent company, subsidiaries, shareholders, beneficial owners, group hierarchy)",
    "leadership": "Leadership and governance (board members, executives, key decision-makers, organizational governance)",
    "financials": "Financial performance (revenue, profit, margins, growth trends, financial statements)",
    "funding": "Funding and capital (investment rounds, investors, valuation, debt, IPO status)",
    "products": "Products and services (offerings, product lines, pricing models, flagship products)",
    "business_model": "Business model and revenue streams (how the company makes money, monetization, unit economics)",
    "market": "Market position and competitors (market share, main rivals, competitive positioning)",
    "customers": "Customers and target segments (client base, key accounts, demographics, geographic markets)",
    "workforce": "Employees and workforce (headcount, hiring trends, culture, locations, key talent)",
    "operations": "Operations and supply chain (facilities, manufacturing, logistics, suppliers, distribution)",
    "technology": "Technology and intellectual property (patents, trademarks, proprietary tech, R&D)",
    "partnerships": "Partnerships and alliances (strategic partners, joint ventures, integrations, vendors)",
    "mergers": "Mergers, acquisitions and divestitures (M&A history, deals, exits)",
    "legal_matters": "Legal and regulatory matters (lawsuits, litigation, compliance, regulatory standing, sanctions)",
    "risk": "Financial health and risk indicators (credit rating, solvency, bankruptcy risk, liabilities)",
    "industry": "Industry and sector context (industry classification, sector trends affecting the company)",
    "history": "History and milestones (founding story, pivots, major events, timeline)",
    "reputation": "Reputation and public perception (brand sentiment, media coverage, reviews, controversies, scandals)",
    "strategy": "Strategy and future outlook (stated goals, expansion plans, recent announcements, forecasts)",
    "online": "Digital and online presence (website, social media, traffic, online footprint)",
    "qa": "Frequently asked questions and synthesized answers about the company generated from all collected evidence",
    "rare": "Facts the company rarely highlights publicly, surprising facts and little-known information",
    "negative": "Negative news and criticism",
    "perception": "Public perception and internet discussions",
}


def collect_company_info_perplexity(company_name: str) -> list[tuple[str, str]]:
    logging.info("Collecting information for company: %s", company_name)
    started_at = time.monotonic()
    results = asyncio.run(
        mc.utils.run_parallel(
            [
                collect_facts_group_perplexity(company_name, subj_key)
                for subj_key in SUBJECTS.keys()
            ],
            max_concurrent_tasks=MAX_CONCURRENT_TASKS,
        )
    )
    # collect instead facts in one line
    facts: list[tuple[str, str]] = [fact for group in results for fact in group]
    logging.info(
        "Collected %d facts for company %s in %.1fs",
        len(facts),
        company_name,
        time.monotonic() - started_at,
    )
    return facts


async def collect_facts_group_perplexity(
    company_name: str, subj_key: str
) -> list[tuple[str, str]]:
    subject = SUBJECTS[subj_key]
    prompt = mc.tpl(
        "data_collector_perplexity.jinja2", company_name=company_name, subject=subject
    ).as_user
    facts = []
    history = [prompt]
    for i in range(PAGES_PER_SUBJECT):
        logging.info(
            "Collecting facts for subject: %s... Iteration %d\n%s",
            subject,
            i + 1,
            mc.ui.green(prompt),
        )
        response = await perplexity(history)
        logging.info(
            "Received response for subject %s, iteration %d: %s",
            subject,
            i + 1,
            mc.ui.cyan(response),
        )
        file = mc.storage.write(
            f"raw_kb/{safe_file_name(company_name)}/{subj_key}_step{i+1}.txt",
            str(response),
        )
        logging.info("Saved raw response to %s", file)
        history.append(response.as_assistant)
        history.append(mc.UserMsg("Collect more facts from other sources"))
        if "FATAL_ERROR" in response:
            logging.error(
                "Perplexity returned an error for subject %s: %s",
                subject,
                mc.ui.red(response),
            )
            break
        for record in response.split("\n---"):
            try:
                record = record.strip()
                fact, url = record.rsplit("\n", 1)
                url = url.replace("Source URL:", "").strip()
                facts.append((fact, url))
            except Exception as e:
                logging.error(f"Failed to parse record: {record}: {e}")
    return facts
