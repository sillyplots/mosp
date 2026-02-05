# Research Notes: X API Free Tier Workarounds

## Official API Status (Free Tier)
As of 2024/2025, the **Free Tier** access level is strictly limited:
-   **Write-Only**: You can post tweets (500/month).
-   **Read Limit**: Extremely limited or non-existent for retrieving other users' timelines.
-   **Endpoints**: `GET /2/users/:id/tweets` and search endpoints return `403 Forbidden`.

## "Creative" Workarounds Analyzed
I investigated several potential "creative" uses of the API:

1.  **Lookup by ID**: If we knew the Tweet IDs beforehand, we might fetch them?
    -   *Verdict*: No, the Free tier often blocks `GET /2/tweets` for reads as well, or limits it to your *own* tweets. Plus, we don't have the IDs.
2.  **OEmbed Endpoint**: (`publish.twitter.com/oembed`)
    -   *Verdict*: Can fetch single tweet HTML if you have the URL. Cannot iterate a timeline or find historical tweets.
3.  **RSS Feeds**:
    -   *Verdict*: Twitter retired official RSS feeds years ago. Third-party bridges (Nitter) are largely broken or blocked.
4.  **Frontend API (GraphQL)**:
    -   *Verdict*: This involves mimicking a browser (Guest Token + GraphQL queries). X has aggressively blocked this for logged-out users. Logged-in scraping is what `snscrape` used to do, but it breaks frequently.

## Conclusion
There is **no viable official API endpoint** on the Free tier to fetch the historical timeline of `@SDOTbridges`.

## Recommended Path
The **Chrome Console Script** (`etl/scrape_tweets.js`) remains the most robust solution because:
1.  It uses your legitimate, logged-in browser session.
2.  It mimics natural human scrolling.
3.  It bypasses API rate limits and tier restrictions.
