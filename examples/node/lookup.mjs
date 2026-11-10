// One lookup. Node.js 18+. Usage: RAPIDAPI_KEY=your_key node lookup.mjs cafemaltaaustin.com [US]
const HOST = "website-contacts-company-info.p.rapidapi.com";

export async function lookup(domain, { country, emails = "all" } = {}) {
  const url = new URL(`https://${HOST}/v1/contacts`);
  url.searchParams.set("domain", domain);
  url.searchParams.set("emails", emails);
  if (country) url.searchParams.set("country", country);
  const res = await fetch(url, {
    headers: { "x-rapidapi-host": HOST, "x-rapidapi-key": process.env.RAPIDAPI_KEY },
    signal: AbortSignal.timeout(60_000),
  });
  if (!res.ok) throw new Error(`HTTP ${res.status}: ${await res.text()}`);
  return res.json();
}

const [domain, country] = process.argv.slice(2);
if (!domain) {
  console.error("usage: node lookup.mjs <domain> [country]");
  process.exit(1);
}
const data = await lookup(domain, { country });
console.log(data.status, data.company.name ?? "");
for (const e of data.emails) console.log("email:", e.email, `[${e.type}]`);
for (const p of data.phones) console.log("phone:", p.international);
for (const [network, urls] of Object.entries(data.socials)) console.log(`${network}:`, urls.join(", "));
