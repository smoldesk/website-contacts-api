# Using the API in n8n, Make or Zapier

All three tools have a generic HTTP request step. Use these settings.

| Setting | Value |
|---|---|
| Method | `GET` |
| URL | `https://website-contacts-company-info.p.rapidapi.com/v1/contacts` |
| Query parameter `domain` | the website from your previous step, e.g. `{{ $json.website }}` |
| Query parameter `country` | optional, e.g. `US` (recommended for .com sites) |
| Header `x-rapidapi-host` | `website-contacts-company-info.p.rapidapi.com` |
| Header `x-rapidapi-key` | your RapidAPI key |
| Timeout | 60 seconds |
| Response format | JSON |

Then map the fields you need, for example `emails[0].email`, `phones[0].international`, `socials.facebook[0]`, `status`.

## n8n

1. Add an **HTTP Request** node after the node that has your websites (Google Sheets, CSV, Airtable…).
2. Method `GET`, URL as above.
3. Turn on **Send Query Parameters**: name `domain`, value `{{ $json.website }}` (use your own column name).
4. Turn on **Send Headers**: add `x-rapidapi-host` and `x-rapidapi-key`.
5. Under **Options**, set **Timeout** to `60000` and **Batching** to 1 item every 1000 ms on the free plan.
6. Add an **If** node on `{{ $json.status }}` equals `contacts_found` before writing results back.

## Make (Integromat)

1. Add **HTTP > Make a request**.
2. URL and method as above. Add the two headers. Under **Query String** add `domain` (mapped from your sheet) and `country`.
3. Tick **Parse response**. Set **Timeout** to 60.
4. Map `emails[].email`, `phones[].international` and `socials` into your next module (Google Sheets > Update a row, for example).

## Zapier

1. Add an action **Webhooks by Zapier > GET**.
2. URL as above. In **Query String Params** add `domain` (mapped from the trigger) and `country`.
3. In **Headers** add `x-rapidapi-host` and `x-rapidapi-key`.
4. Zapier flattens the JSON, so fields appear as `Emails Email`, `Phones International`, `Socials Facebook`, and so on.

## Good to know

- A lookup that finds nothing does not use your Lookups quota, but it still counts as a request.
- Filter on `status`. Only `contacts_found` rows have data. See the status table in the [README](../README.md#status-values).
- Respect your plan's rate limit. On the free plan, send one request per second.
