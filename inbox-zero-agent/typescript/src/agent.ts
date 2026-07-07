/**
 * Inbox Zero Agent: drafts replies while you sleep - you review and send.
 *
 * Give an AgenticEmail inbox to Claude. For every new email, Claude writes a
 * reply in your voice and saves it as a draft. Nothing is ever sent
 * automatically - you review each draft and send it yourself.
 */
import Anthropic from "@anthropic-ai/sdk";
import { AgenticEmail } from "agenticemail";
import { buildSystemPrompt } from "./prompt.js";

const MODEL = process.env.ANTHROPIC_MODEL ?? "claude-sonnet-5";
const POLL_MS = Number(process.env.POLL_SECONDS ?? "10") * 1000;
const INBOX_USERNAME = process.env.INBOX_USERNAME ?? "inbox-zero-agent";

const USER_NAME = process.env.USER_NAME ?? "Alex";

const email = new AgenticEmail({ apiKey: process.env.AGENTICEMAIL_API_KEY! });
const claude = new Anthropic(); // reads ANTHROPIC_API_KEY

const inbox = await email.inboxes.create({
	username: INBOX_USERNAME,
	...(process.env.INBOX_DOMAIN ? { domain: process.env.INBOX_DOMAIN } : {}),
});
const inboxEmail = inbox.id;
const systemPrompt = buildSystemPrompt(inboxEmail, USER_NAME);

async function draftReply(message: string): Promise<string> {
	const reply = await claude.messages.create({
		model: MODEL,
		max_tokens: 2048,
		system: systemPrompt,
		messages: [{ role: "user", content: message }],
	});
	return reply.content.filter((b) => b.type === "text").map((b) => b.text).join("");
}

console.log(`Inbox Zero Agent inbox: ${inboxEmail}`);
// Ignore mail that was already in the inbox when we started.
const seen = new Set<string>();
for (const m of (await email.messages.list(inboxEmail)).data) seen.add(m.id);
console.log("Waiting for email... (Ctrl+C to stop)");

while (true) {
	const { data } = await email.messages.list(inboxEmail);
	for (const msg of data) {
		if (seen.has(msg.id)) continue;
		seen.add(msg.id);
		if (msg.direction !== "inbound") continue;
		console.log(`New email from ${msg.from}: ${msg.subject ?? "(no subject)"}`);
		const prompt = `From: ${msg.from}\nSubject: ${msg.subject ?? ""}\n\n${msg.text ?? ""}`;
		await email.drafts.create(inboxEmail, {
			to: [msg.from],
			subject: `Re: ${msg.subject ?? ""}`,
			text: await draftReply(prompt),
		});
		console.log("  drafted (not sent).");
	}
	await new Promise((r) => setTimeout(r, POLL_MS));
}
