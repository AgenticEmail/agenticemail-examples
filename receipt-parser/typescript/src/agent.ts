/**
 * Receipt & expense parser: turns forwarded receipt photos and PDFs into clean expense rows.
 *
 * Give an AgenticEmail inbox to Claude. When someone forwards or photographs a
 * receipt and sends it here, Claude reads the image or PDF with its vision,
 * extracts the merchant, date, total, tax, and payment method, categorises the
 * expense, flags anything unusual, routes a clean row to your expense system,
 * and confirms with the sender - all from an inbox it owns.
 */
import Anthropic from "@anthropic-ai/sdk";
import { AgenticEmail } from "agenticemail";
import { buildSystemPrompt } from "./prompt.js";

const MODEL = process.env.ANTHROPIC_MODEL ?? "claude-sonnet-5";
const POLL_MS = Number(process.env.POLL_SECONDS ?? "10") * 1000;
const INBOX_USERNAME = process.env.INBOX_USERNAME ?? "receipt-parser";

const EXPENSE_EMAIL = process.env.EXPENSE_EMAIL ?? "expenses@example.com";
const FLAG_LIMIT = Number(process.env.FLAG_LIMIT ?? "500");

const email = new AgenticEmail({ apiKey: process.env.AGENTICEMAIL_API_KEY! });
const claude = new Anthropic(); // reads ANTHROPIC_API_KEY

const inbox = await email.inboxes.create({ username: INBOX_USERNAME });
const inboxEmail = inbox.id;
const systemPrompt = buildSystemPrompt(inboxEmail, EXPENSE_EMAIL, FLAG_LIMIT);

const EXTRACT_INSTRUCTION =
	'Extract this receipt. Reply with ONLY a JSON object: ' +
	'{"merchant":..., "date":..., "total": <number>, "currency":..., ' +
	'"category":..., "tax":..., "payment_method":...}. No prose.';

interface Receipt {
	merchant?: string;
	date?: string;
	total?: number;
	currency?: string;
	category?: string;
	tax?: string | number;
	payment_method?: string;
}

function receiptBlock(
	contentType: string,
	dataB64: string,
): Anthropic.ContentBlockParam | null {
	if (contentType.startsWith("image/")) {
		return {
			type: "image",
			source: {
				type: "base64",
				media_type: contentType as "image/jpeg",
				data: dataB64,
			},
		};
	}
	if (contentType === "application/pdf") {
		return {
			type: "document",
			source: {
				type: "base64",
				media_type: "application/pdf",
				data: dataB64,
			},
		};
	}
	return null;
}

async function extractReceipt(
	contentType: string,
	rawBytes: ArrayBuffer,
): Promise<Receipt | null> {
	const block = receiptBlock(contentType, Buffer.from(rawBytes).toString("base64"));
	if (block === null) return null;
	const reply = await claude.messages.create({
		model: MODEL,
		max_tokens: 2048,
		system: systemPrompt,
		messages: [
			{
				role: "user",
				content: [block, { type: "text", text: EXTRACT_INSTRUCTION }],
			},
		],
	});
	const raw = reply.content.filter((b) => b.type === "text").map((b) => b.text).join("");
	const start = raw.indexOf("{");
	const end = raw.lastIndexOf("}");
	if (start === -1 || end === -1) {
		console.log("  could not find JSON in Claude's reply, skipping.");
		return null;
	}
	try {
		return JSON.parse(raw.slice(start, end + 1)) as Receipt;
	} catch {
		console.log("  could not parse receipt JSON, skipping.");
		return null;
	}
}

async function processAttachment(
	msg: { id: string; from: string },
	attachment: { id: string; contentType: string },
): Promise<void> {
	const rawBytes = await email.messages.getAttachment(inboxEmail, msg.id, attachment.id);
	const receipt = await extractReceipt(attachment.contentType, rawBytes);
	if (receipt === null) return;

	const merchant = receipt.merchant ?? "unknown merchant";
	const date = receipt.date ?? "unknown";
	const total = receipt.total;
	const currency = receipt.currency ?? "";
	const category = receipt.category ?? "other";
	const tax = receipt.tax ?? "n/a";
	const paymentMethod = receipt.payment_method ?? "unknown";

	const flagged = typeof total === "number" && total > FLAG_LIMIT;
	const status = flagged ? "FLAG" : "ok";

	const row =
		`Merchant: ${merchant}\n` +
		`Date: ${date}\n` +
		`Category: ${category}\n` +
		`Total: ${total} ${currency}\n` +
		`Tax: ${tax}\n` +
		`Payment method: ${paymentMethod}\n` +
		`Status: ${status}\n` +
		`Received from: ${msg.from}`;
	await email.messages.send(inboxEmail, {
		to: [EXPENSE_EMAIL],
		subject: `Expense: ${merchant} ${total} ${currency}` + (flagged ? " [FLAG]" : ""),
		text: row,
	});
	await email.messages.reply(inboxEmail, msg.id, {
		text: `Recorded ${merchant} for ${total} ${currency}.`,
	});
	console.log(`  routed expense for ${merchant} to ${EXPENSE_EMAIL} (${status}).`);
}

console.log(`Receipt parser inbox: ${inboxEmail}`);
// Ignore mail that was already in the inbox when we started.
const seen = new Set<string>();
for (const m of (await email.messages.list(inboxEmail)).data) seen.add(m.id);
console.log("Waiting for receipts... (Ctrl+C to stop)");

while (true) {
	const { data } = await email.messages.list(inboxEmail);
	for (const msg of data) {
		if (seen.has(msg.id)) continue;
		seen.add(msg.id);
		if (msg.direction !== "inbound") continue;
		console.log(`New email from ${msg.from}: ${msg.subject ?? "(no subject)"}`);
		const receipts = (msg.attachments ?? []).filter(
			(a) => a.contentType.startsWith("image/") || a.contentType === "application/pdf",
		);
		if (receipts.length === 0) {
			console.log("  no image or PDF attachment, skipping.");
			continue;
		}
		for (const attachment of receipts) {
			await processAttachment(msg, attachment);
		}
	}
	await new Promise((r) => setTimeout(r, POLL_MS));
}
