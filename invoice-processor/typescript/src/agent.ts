/**
 * Invoice processor: extracts, matches, and routes invoices from PDF attachments.
 *
 * Give an AgenticEmail inbox to Claude. When a vendor emails a PDF invoice,
 * Claude reads it with PDF vision, extracts the key fields, decides approved vs
 * needs-review, routes it to your AP team, and confirms receipt with the vendor.
 */
import Anthropic from "@anthropic-ai/sdk";
import { AgenticEmail } from "agenticemail";
import { buildSystemPrompt } from "./prompt.js";

const MODEL = process.env.ANTHROPIC_MODEL ?? "claude-sonnet-5";
const POLL_MS = Number(process.env.POLL_SECONDS ?? "10") * 1000;
const INBOX_USERNAME = process.env.INBOX_USERNAME ?? "invoice-processor";

const AP_EMAIL = process.env.AP_EMAIL ?? "ap@example.com";
const AUTO_APPROVE_LIMIT = Number(process.env.AUTO_APPROVE_LIMIT ?? "1000");

const email = new AgenticEmail({ apiKey: process.env.AGENTICEMAIL_API_KEY! });
const claude = new Anthropic(); // reads ANTHROPIC_API_KEY

const inbox = await email.inboxes.create({
	username: INBOX_USERNAME,
	...(process.env.INBOX_DOMAIN ? { domain: process.env.INBOX_DOMAIN } : {}),
});
const inboxEmail = inbox.id;
const systemPrompt = buildSystemPrompt(inboxEmail, AP_EMAIL, AUTO_APPROVE_LIMIT);

const EXTRACT_INSTRUCTION =
	'Extract this invoice. Reply with ONLY a JSON object: ' +
	'{"vendor":..., "invoice_number":..., "amount": <number>, ' +
	'"currency":..., "due_date":...}. No prose.';

interface Invoice {
	vendor?: string;
	invoice_number?: string;
	amount?: number;
	currency?: string;
	due_date?: string;
}

async function extractInvoice(pdfBytes: ArrayBuffer): Promise<Invoice | null> {
	const b64 = Buffer.from(pdfBytes).toString("base64");
	const reply = await claude.messages.create({
		model: MODEL,
		max_tokens: 2048,
		system: systemPrompt,
		messages: [
			{
				role: "user",
				content: [
					{
						type: "document",
						source: {
							type: "base64",
							media_type: "application/pdf",
							data: b64,
						},
					},
					{ type: "text", text: EXTRACT_INSTRUCTION },
				],
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
		return JSON.parse(raw.slice(start, end + 1)) as Invoice;
	} catch {
		console.log("  could not parse invoice JSON, skipping.");
		return null;
	}
}

async function processAttachment(
	msg: { id: string; from: string },
	attachment: { id: string },
): Promise<void> {
	const pdfBytes = await email.messages.getAttachment(inboxEmail, msg.id, attachment.id);
	const invoice = await extractInvoice(pdfBytes);
	if (invoice === null) return;

	const vendor = invoice.vendor ?? "unknown vendor";
	const invoiceNumber = invoice.invoice_number ?? "unknown";
	const amount = invoice.amount;
	const currency = invoice.currency ?? "";
	const dueDate = invoice.due_date ?? "unknown";

	const status =
		typeof amount === "number" && amount < AUTO_APPROVE_LIMIT ? "approved" : "needs-review";

	const summary =
		`Invoice ${invoiceNumber} from ${vendor}\n` +
		`Amount: ${amount} ${currency}\n` +
		`Due date: ${dueDate}\n` +
		`Status: ${status}\n` +
		`Received from: ${msg.from}`;
	await email.messages.send(inboxEmail, {
		to: [AP_EMAIL],
		subject: `[${status}] Invoice ${invoiceNumber} from ${vendor}`,
		text: summary,
	});
	await email.messages.reply(inboxEmail, msg.id, {
		text: `Thanks - we received invoice ${invoiceNumber} and it is being processed.`,
	});
	console.log(`  routed invoice ${invoiceNumber} to ${AP_EMAIL} (${status}).`);
}

console.log(`Invoice processor inbox: ${inboxEmail}`);
// Ignore mail that was already in the inbox when we started.
const seen = new Set<string>();
for (const m of (await email.messages.list(inboxEmail)).data) seen.add(m.id);
console.log("Waiting for invoices... (Ctrl+C to stop)");

while (true) {
	const { data } = await email.messages.list(inboxEmail);
	for (const msg of data) {
		if (seen.has(msg.id)) continue;
		seen.add(msg.id);
		if (msg.direction !== "inbound") continue;
		console.log(`New email from ${msg.from}: ${msg.subject ?? "(no subject)"}`);
		const pdfs = (msg.attachments ?? []).filter(
			(a) => a.contentType === "application/pdf",
		);
		if (pdfs.length === 0) {
			console.log("  no PDF attachment, skipping.");
			continue;
		}
		for (const attachment of pdfs) {
			await processAttachment(msg, attachment);
		}
	}
	await new Promise((r) => setTimeout(r, POLL_MS));
}
