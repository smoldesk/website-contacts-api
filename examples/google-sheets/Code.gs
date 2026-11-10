/**
 * Website Contacts API for Google Sheets.
 *
 * Setup (once):
 *   1. In your sheet: Extensions > Apps Script. Paste this whole file, replacing what is there.
 *   2. Put your RapidAPI key below and click Save.
 *   3. Back in the sheet, type in a cell:  =CONTACTS(A2)      or  =CONTACTS(A2, "US")
 *
 * The formula fills 7 cells to the right:
 *   status | emails | phones | facebook | instagram | linkedin | contact form
 * Add this header row above your results if you like:
 *   =CONTACTS_HEADER()
 *
 * Results are cached for 6 hours, so re-opening or re-sorting the sheet does not call the API again.
 * When you are done, copy the result columns and use Paste special > Values only, so they never refresh.
 */
const RAPIDAPI_KEY = "PASTE_YOUR_RAPIDAPI_KEY_HERE";
const HOST = "website-contacts-company-info.p.rapidapi.com";

/**
 * Public contacts of a website.
 * @param {string} domain Domain or URL, e.g. "example.com".
 * @param {string} [country] Optional 2-letter country code for phone numbers, e.g. "US".
 * @return Status, emails, phones, facebook, instagram, linkedin, contact form.
 * @customfunction
 */
function CONTACTS(domain, country) {
  domain = String(domain || "").trim();
  if (!domain) return [[""]];
  const key = "wc:" + domain.toLowerCase() + ":" + (country || "");
  const cache = CacheService.getScriptCache();
  const hit = cache.get(key);
  if (hit) return JSON.parse(hit);

  let url = "https://" + HOST + "/v1/contacts?domain=" + encodeURIComponent(domain);
  if (country) url += "&country=" + encodeURIComponent(country);
  const res = UrlFetchApp.fetch(url, {
    headers: { "x-rapidapi-host": HOST, "x-rapidapi-key": RAPIDAPI_KEY },
    muteHttpExceptions: true,
  });
  const code = res.getResponseCode();
  if (code === 429) return [["rate limited, try again in a minute"]];
  if (code !== 200 && code !== 400) return [["error " + code]];

  const d = JSON.parse(res.getContentText());
  const s = d.socials || {};
  const first = list => (list && list[0]) || "";
  const row = [[
    d.status || "",
    (d.emails || []).map(e => e.email).join(", "),
    (d.phones || []).map(p => p.international).join(", "),
    first(s.facebook),
    first(s.instagram),
    first(s.linkedin),
    d.contactFormUrl || "",
  ]];
  cache.put(key, JSON.stringify(row), 21600);
  return row;
}

/** Header row for CONTACTS(). @customfunction */
function CONTACTS_HEADER() {
  return [["status", "emails", "phones", "facebook", "instagram", "linkedin", "contact form"]];
}
