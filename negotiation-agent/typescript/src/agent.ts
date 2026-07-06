/**
 * Negotiation agent: works a deal over email, holding your line.
 *
 * Give an AgenticEmail inbox to Claude. When the other side emails, Claude
 * anchors, concedes slowly, and confirms once your target is hit - in-thread.
 */
import Anthropic from "@anthropic-ai/sdk";
import { AgenticEmail } from "agenticemail";
import { buildSystemPrompt } from "./prompt.js";

const MODEL = process.env.ANTHROPIC_MODEL ?? "claude-sonnet-5";
const POLL_MS = Number(process.env.POLL_SECONDS ?? "10") * 1000;
const INBOX_USERNAME = process.env.INBOX_USERNAME ?? "negotiation-agent";

const USER_NAME = process.env.USER_NAME ?? "Sam";
const TARGET_TERMS = process.env.TARGET_TERMS ?? "$18,000 out the door";
const WALK_AWAY = process.env.WALK_AWAY ?? "$20,000";

const email = new AgenticEmail({ apiKey: process.env.AGENTICEMAIL_API_KEY! });
const claude = new Anthropic(); // reads ANTHROPIC_API_KEY

const inbox = await email.inboxes.create({ username: INBOX_USERNAME });
const inboxEmail = inbox.id;
const systemPrompt = buildSystemPrompt(inboxEmail, USER_NAME, TARGET_TERMS, WALK_AWAY);

async function answer(message: string): Promise<string> {
	const reply = await claude.messages.create({
		model: MODEL,
		max_tokens: 1024,
		system: systemPrompt,
		messages: [{ role: "user", content: message }],
	});
	const block = reply.content[0];
	return block.type === "text" ? block.text : "";
}

console.log(`Negotiation agent inbox: ${inboxEmail}`);
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
		await email.messages.reply(inboxEmail, msg.id, { text: await answer(prompt) });
		console.log("  replied.");
	}
	await new Promise((r) => setTimeout(r, POLL_MS));
}
