/**
 * GTM agent: runs outbound over email, classifies replies, hands off warm leads.
 *
 * Give an AgenticEmail inbox to Claude. It sends a first-touch cold email, then
 * classifies every reply and responds - warm leads get a call and a CC to you.
 */
import Anthropic from "@anthropic-ai/sdk";
import { AgenticEmail } from "agenticemail";
import { buildSystemPrompt } from "./prompt.js";

const MODEL = process.env.ANTHROPIC_MODEL ?? "claude-sonnet-5";
const POLL_MS = Number(process.env.POLL_SECONDS ?? "10") * 1000;
const INBOX_USERNAME = process.env.INBOX_USERNAME ?? "gtm-agent";

const USER_NAME = process.env.USER_NAME ?? "Sam";
const PROSPECT_EMAIL = process.env.PROSPECT_EMAIL ?? "prospect@example.com";

const email = new AgenticEmail({ apiKey: process.env.AGENTICEMAIL_API_KEY! });
const claude = new Anthropic(); // reads ANTHROPIC_API_KEY

const inbox = await email.inboxes.create({ username: INBOX_USERNAME });
const inboxEmail = inbox.id;
const systemPrompt = buildSystemPrompt(inboxEmail, USER_NAME);

async function answer(message: string): Promise<string> {
	const reply = await claude.messages.create({
		model: MODEL,
		max_tokens: 2048,
		system: systemPrompt,
		messages: [{ role: "user", content: message }],
	});
	return reply.content.filter((b) => b.type === "text").map((b) => b.text).join("");
}

console.log(`GTM agent inbox: ${inboxEmail}`);
// Send the first-touch cold email before we start listening for replies.
const opener = await answer(
	`Write a first-touch cold email to the prospect at ${PROSPECT_EMAIL}. They are a growth lead at an early-stage SaaS company.`,
);
await email.messages.send(inboxEmail, {
	to: [PROSPECT_EMAIL],
	subject: "Quick question",
	text: opener,
});
console.log(`Sent opener to ${PROSPECT_EMAIL}.`);
// Ignore mail that was already in the inbox when we started.
const seen = new Set<string>();
for (const m of (await email.messages.list(inboxEmail)).data) seen.add(m.id);
console.log("Waiting for replies... (Ctrl+C to stop)");

while (true) {
	const { data } = await email.messages.list(inboxEmail);
	for (const msg of data) {
		if (seen.has(msg.id)) continue;
		seen.add(msg.id);
		if (msg.direction !== "inbound") continue;
		console.log(`New email from ${msg.from}: ${msg.subject ?? "(no subject)"}`);
		const prompt = `From: ${msg.from}\nSubject: ${msg.subject ?? ""}\n\n${msg.text ?? ""}`;
		await email.messages.reply(inboxEmail, msg.id, { text: await answer(prompt) });
		console.log("  replied.");
	}
	await new Promise((r) => setTimeout(r, POLL_MS));
}
