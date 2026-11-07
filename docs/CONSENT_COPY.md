# Consent copy (D-018)

**Status:** approved by the project owner on 2026-11-07 (revision 3.1).
**Provider status:** PhishTank is disabled and URLhaus is disabled. This copy is used only when a provider is enabled, and must be rechecked first: PhishTank's data handling was unclear on 2026-11-06, and the wording about outbound IP addresses depends on the hosting environment.

## Rules

- Consent is per scan and per provider. Nothing is remembered.
- No provider request is made before the user explicitly agrees.
- The preview is exactly the value sent (`Indicator.url_without_query`), never the shortened `display_value`.
- Never claim more was checked than was sent.
- A skipped or failed check is never presented as "safe".
- Text in `{braces}` is filled in by the bot and must be escaped for the output format.

## Prompt before a PhishTank lookup (URL input)

> **Check this link with PhishTank?**
>
> I've finished the local checks. I can also look this link up on PhishTank, a community list of reported phishing sites.
>
> This exact address would be sent:
> `{url_without_query}`
>
> - The part after the site name (the path) is included. If it holds a private code, tap Skip.
> - Anything after `?` or `#` is not sent, and neither is any username or password.
> - PhishTank's current privacy statement does not clearly say whether lookups are stored or for how long. An older PhishTank policy said it logged looked-up addresses and the requesting IP address. That policy is now archived and may no longer apply.
> - The request is sent by the system running ScamShield. Its outbound IP address depends on where the bot is hosted, and is normally not your device's IP address.
>
> [Send to PhishTank]  [Skip, local checks only]

Extra line, only when the link had a query string or fragment:

> Your link had extra parts after `?` or `#`. They are not sent, so any result covers the shorter address only.

## Results

- **Listed:** "PhishTank lists this address (without anything after `?` or `#`) as a reported phishing site. {verified | not yet verified by PhishTank}."
- **Not listed:** "PhishTank has no report for this address (checked without anything after `?` or `#`). That does not mean it is safe: new or unreported sites are not listed."
- **Error, timeout, or rate limit:** "PhishTank could not be checked right now. This is not a clean result."
- **Skipped:** "Local checks only. No outside service was asked. This is not a 'no threats found' result and does not mean the link is safe."

## Cases with no prompt

- **Domain-only input:** "ScamShield does not send a bare domain to PhishTank, because PhishTank's documented lookup takes a full web address. Send the full link, starting with `https://`, if you want that check." A domain is never turned into a made-up URL.
- **Private or internal address (`lookup_blocked_reason` is set):** "This looks like a private or internal address, so I did not send it to any outside service."
- **No provider enabled (the current state):** "Outside checks are not turned on yet, so this report uses local checks only. It is not a 'no threats found' result."

## URLhaus

No prompt is written. Its adapter stays disabled until its data handling is verified from official terms.
