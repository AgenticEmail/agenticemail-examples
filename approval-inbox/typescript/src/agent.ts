/**
 * Approval Inbox: turns your inbox into an approval queue.
 *
 * Give an AgenticEmail inbox to Claude. Systems email it approval requests,
 * Claude summarises each one, and the approver replies "approve" or "reject".
 */
import Anthropic from "@anthropic-ai/sdk";
import { AgenticEmail } from "agenticemail";
import { buildSystemPrompt } from "./prompt.js";

const MODEL = process.env.ANTHROPIC_MODEL ?? "claude-sonnet-5";
const POLL_MS = Number(process.env.POLL_SECONDS ?? "10") * 1000;
const INBOX_USERNAME = process.env.INBOX_USERNAME ?? "approval-inbox";

const APPROVER_NAME = process.env.APPROVER_NAME ?? "Alex";

const email = new AgenticEmail({ apiKey: process.env.AGENTICEMAIL_API_KEY! });
const claude = new Anthropic(); // reads ANTHROPIC_API_KEY

const inbox = await email.inboxes.create({ username: INBOX_USERNAME });
const inboxEmail = inbox.id;
const systemPrompt = buildSystemPrompt(inboxEmail, APPROVER_NAME);

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

console.log(`Approval inbox: ${inboxEmail}`);
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
