/**
 * Dinner reservation agent: emails a restaurant and books your table over email.
 *
 * Give an AgenticEmail inbox to Claude. It sends the opening reservation
 * request, then handles every reply - accepting an in-window time, confirming
 * the booking, and reporting back to you - all in-thread.
 */
import Anthropic from "@anthropic-ai/sdk";
import { AgenticEmail } from "agenticemail";
import { buildSystemPrompt } from "./prompt.js";

const MODEL = process.env.ANTHROPIC_MODEL ?? "claude-sonnet-5";
const POLL_MS = Number(process.env.POLL_SECONDS ?? "10") * 1000;
const INBOX_USERNAME = process.env.INBOX_USERNAME ?? "dinner-reservation";

const USER_NAME = process.env.USER_NAME ?? "Sam";
const PARTY_SIZE = process.env.PARTY_SIZE ?? "2";
const DATE_WINDOW = process.env.DATE_WINDOW ?? "Friday 7-8pm";
const AREA = process.env.AREA ?? "downtown";
const PREFERENCES = process.env.PREFERENCES ?? "Italian, quiet";
const RESTAURANT_EMAIL = process.env.RESTAURANT_EMAIL ?? "restaurant@example.com";

const email = new AgenticEmail({ apiKey: process.env.AGENTICEMAIL_API_KEY! });
const claude = new Anthropic(); // reads ANTHROPIC_API_KEY

const inbox = await email.inboxes.create({
	username: INBOX_USERNAME,
	...(process.env.INBOX_DOMAIN ? { domain: process.env.INBOX_DOMAIN } : {}),
});
const inboxEmail = inbox.id;
const systemPrompt = buildSystemPrompt(
	inboxEmail,
	USER_NAME,
	PARTY_SIZE,
	DATE_WINDOW,
	AREA,
	PREFERENCES,
);

async function answer(message: string): Promise<string> {
	const reply = await claude.messages.create({
		model: MODEL,
		max_tokens: 2048,
		system: systemPrompt,
		messages: [{ role: "user", content: message }],
	});
	return reply.content.filter((b) => b.type === "text").map((b) => b.text).join("");
}

console.log(`Dinner reservation agent inbox: ${inboxEmail}`);
// Send the opening reservation request before we start listening for replies.
const opener = await answer(
	"Write the opening reservation request email to the restaurant.",
);
await email.messages.send(inboxEmail, {
	to: [RESTAURANT_EMAIL],
	subject: "Table request",
	text: opener,
});
console.log(`Sent request to ${RESTAURANT_EMAIL}.`);
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
