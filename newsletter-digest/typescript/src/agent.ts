/**
 * Newsletter digest: one daily summary of everything that hit your inbox.
 *
 * Point an AgenticEmail inbox at your newsletters and updates. Once a day this
 * reads every message that arrived, groups it by theme, and emails you a single
 * scannable digest.
 */
import Anthropic from "@anthropic-ai/sdk";
import { AgenticEmail } from "agenticemail";
import { buildSystemPrompt } from "./prompt.js";

const MODEL = process.env.ANTHROPIC_MODEL ?? "claude-sonnet-5";
const INBOX_USERNAME = process.env.INBOX_USERNAME ?? "newsletter-digest";

const USER_EMAIL = process.env.USER_EMAIL ?? "you@example.com";

const email = new AgenticEmail({ apiKey: process.env.AGENTICEMAIL_API_KEY! });
const claude = new Anthropic(); // reads ANTHROPIC_API_KEY

const inbox = await email.inboxes.create({ username: INBOX_USERNAME });
const inboxEmail = inbox.id;
const systemPrompt = buildSystemPrompt(inboxEmail, USER_EMAIL);

console.log(`Newsletter digest inbox: ${inboxEmail}`);

const { data } = await email.messages.list(inboxEmail);
const inbound = data.filter((m) => m.direction === "inbound");

if (inbound.length === 0) {
	console.log(
		"Nothing to digest yet - subscribe this inbox to a few newsletters and run again.",
	);
	process.exit(0);
}

let items = "";
for (const msg of inbound) {
	const text = (msg.text ?? "").slice(0, 1500);
	items += `From: ${msg.from}\nSubject: ${msg.subject ?? ""}\n${text}\n\n---\n\n`;
}

const today = new Date().toISOString().slice(0, 10);
const reply = await claude.messages.create({
	model: MODEL,
	max_tokens: 2048,
	system: systemPrompt,
	messages: [{ role: "user", content: items }],
});
const digest = reply.content.filter((b) => b.type === "text").map((b) => b.text).join("");

await email.messages.send(inboxEmail, {
	to: [USER_EMAIL],
	subject: `Your daily digest - ${today}`,
	text: digest,
});
console.log(`Digest sent to ${USER_EMAIL}.`);
