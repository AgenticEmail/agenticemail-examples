/**
 * Signup and verification agent: catches confirmation links and 2FA codes.
 *
 * Give an AgenticEmail inbox to a browser-automation agent. When a service
 * emails a verification code or magic link to the inbox, Claude extracts it as
 * structured JSON your automation can act on.
 */
import Anthropic from "@anthropic-ai/sdk";
import { AgenticEmail } from "agenticemail";
import { buildSystemPrompt } from "./prompt.js";

const MODEL = process.env.ANTHROPIC_MODEL ?? "claude-sonnet-5";
const POLL_MS = Number(process.env.POLL_SECONDS ?? "5") * 1000;
const INBOX_USERNAME = process.env.INBOX_USERNAME ?? "verification-agent";

const FORWARD_TO = process.env.FORWARD_TO ?? "";

const email = new AgenticEmail({ apiKey: process.env.AGENTICEMAIL_API_KEY! });
const claude = new Anthropic(); // reads ANTHROPIC_API_KEY

const inbox = await email.inboxes.create({ username: INBOX_USERNAME });
const inboxEmail = inbox.id;
const systemPrompt = buildSystemPrompt(inboxEmail);

type Extracted = {
	service: string | null;
	code: string | null;
	link: string | null;
};

async function extract(message: string): Promise<Extracted | null> {
	const resp = await claude.messages.create({
		model: MODEL,
		max_tokens: 2048,
		system: systemPrompt,
		messages: [{ role: "user", content: message }],
	});
	const raw = resp.content
		.filter((b) => b.type === "text")
		.map((b) => b.text)
		.join("");
	const start = raw.indexOf("{");
	const end = raw.lastIndexOf("}");
	if (start === -1 || end === -1) return null;
	try {
		return JSON.parse(raw.slice(start, end + 1)) as Extracted;
	} catch {
		return null;
	}
}

console.log(`Verification agent inbox: ${inboxEmail}`);
console.log("Sign up for a service with this address, then watch the code appear.");
const seen = new Set<string>();
for (const m of (await email.messages.list(inboxEmail)).data) seen.add(m.id);

while (true) {
	const { data } = await email.messages.list(inboxEmail);
	for (const msg of data) {
		if (seen.has(msg.id)) continue;
		seen.add(msg.id);
		if (msg.direction !== "inbound") continue;
		const body = `From: ${msg.from}\nSubject: ${msg.subject ?? ""}\n\n${msg.text ?? ""}`;
		const result = await extract(body);
		if (!result || !(result.code || result.link)) {
			console.log(`  ${msg.from}: no verification code or link found`);
			continue;
		}
		console.log(
			`  service=${result.service} code=${result.code} link=${result.link}`,
		);
		if (FORWARD_TO) {
			await email.messages.send(inboxEmail, {
				to: [FORWARD_TO],
				subject: `Verification from ${result.service}`,
				text: JSON.stringify(result, null, 2),
			});
		}
	}
	await new Promise((r) => setTimeout(r, POLL_MS));
}
