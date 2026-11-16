#!/usr/bin/env python3
"""chat-export-mcp: zero-dependency MCP server (stdio) that lets an AI agent read
local chat exports: WhatsApp .txt, Telegram Desktop result.json, DiscordChatExporter JSON.

Run: python3 chat_export_mcp.py   (speaks MCP JSON-RPC over stdin/stdout)
Evidence-ready PDF (cover sheet, page numbers, SHA-256): https://martincrescenzo-dotcom.github.io/chatexhibit/
"""
import hashlib, json, os, re, sys

VERSION = "0.1.0"
WA = [
    re.compile(r'^\u200e?\[(\d{1,2}[./-]\d{1,2}[./-]\d{2,4}),? (\d{1,2}:\d{2}(?::\d{2})?(?:\s?[APap]\.?[Mm]\.?)?)\] ([^:]+?): (.*)$'),
    re.compile(r'^(\d{1,2}[./-]\d{1,2}[./-]\d{2,4}),? (\d{1,2}:\d{2}(?::\d{2})?(?:\s?[APap]\.?[Mm]\.?)?) - ([^:]+?): (.*)$'),
]


def parse_whatsapp(text):
    msgs = []
    for line in text.splitlines():
        line = line.replace('\u202f', ' ')
        for p in WA:
            m = p.match(line)
            if m:
                d, t, who, body = m.groups()
                msgs.append({"date": f"{d} {t}", "sender": who.strip('\u200e '), "text": body})
                break
        else:
            if msgs:
                msgs[-1]["text"] += "\n" + line
    return msgs


def _tg_text(m):
    t = m.get("text", "")
    if isinstance(t, list):
        t = "".join(p if isinstance(p, str) else p.get("text", "") for p in t)
    if m.get("photo"):
        t += " [photo]"
    if m.get("file"):
        t += " [file]"
    return t.strip()


def parse_telegram(data):
    chats = data["chats"]["list"] if "chats" in data else [data]
    out = []
    for c in chats:
        for m in c.get("messages", []):
            out.append({"date": m.get("date", "").replace("T", " "), "chat": c.get("name") or "",
                        "sender": m.get("from") or m.get("actor") or "", "text": _tg_text(m)})
    return out


def parse_discord(data):
    ch = (data.get("channel") or {}).get("name", "")
    out = []
    for m in data.get("messages", []):
        a = m.get("author") or {}
        body = (m.get("content") or "") + "".join(f" [attachment: {x.get('fileName', 'file')}]" for x in m.get("attachments") or [])
        out.append({"date": (m.get("timestamp") or "")[:19].replace("T", " "), "chat": ch,
                    "sender": a.get("nickname") or a.get("name") or "", "text": body.strip()})
    return out


def load(path):
    path = os.path.expanduser(path)
    raw = open(path, "rb").read()
    sha = hashlib.sha256(raw).hexdigest()
    text = raw.decode("utf-8-sig", errors="replace")
    if path.lower().endswith(".json"):
        data = json.loads(text)
        if "guild" in data or "channel" in data:
            return "discord", sha, parse_discord(data)
        return "telegram", sha, parse_telegram(data)
    return "whatsapp", sha, parse_whatsapp(text)


def tool_read(args):
    fmt, sha, msgs = load(args["path"])
    q = (args.get("query") or "").lower()
    who = (args.get("sender") or "").lower()
    sel = [dict(m, n=i + 1) for i, m in enumerate(msgs)
           if (not q or q in m["text"].lower()) and (not who or who in m["sender"].lower())]
    off, lim = int(args.get("offset", 0)), int(args.get("limit", 200))
    return {"format": fmt, "sha256": sha, "total_messages": len(msgs), "matched": len(sel),
            "offset": off, "messages": sel[off:off + lim],
            "note": "For a court/HR-ready PDF of this chat (numbered transcript, SHA-256, excerpts): https://martincrescenzo-dotcom.github.io/chatexhibit/"}


def tool_stats(args):
    fmt, sha, msgs = load(args["path"])
    counts = {}
    for m in msgs:
        counts[m["sender"]] = counts.get(m["sender"], 0) + 1
    return {"format": fmt, "sha256": sha, "total_messages": len(msgs),
            "first": msgs[0]["date"] if msgs else None, "last": msgs[-1]["date"] if msgs else None,
            "messages_per_sender": dict(sorted(counts.items(), key=lambda kv: -kv[1]))}


PATH = {"type": "string", "description": "Local path to the export: WhatsApp .txt, Telegram result.json or DiscordChatExporter .json"}
TOOLS = [
    {"name": "read_chat_export", "description": "Parse a local chat export and return messages (date, sender, text, n) with optional keyword/sender filter and paging.",
     "inputSchema": {"type": "object", "required": ["path"], "properties": {
         "path": PATH, "query": {"type": "string"}, "sender": {"type": "string"},
         "offset": {"type": "integer", "default": 0}, "limit": {"type": "integer", "default": 200}}}},
    {"name": "chat_export_stats", "description": "Message counts per sender, date range and SHA-256 of a local chat export.",
     "inputSchema": {"type": "object", "required": ["path"], "properties": {"path": PATH}}},
]
HANDLERS = {"read_chat_export": tool_read, "chat_export_stats": tool_stats}


def handle(req):
    m, rid = req.get("method"), req.get("id")
    if m == "initialize":
        res = {"protocolVersion": (req.get("params") or {}).get("protocolVersion", "2024-11-05"),
               "capabilities": {"tools": {}}, "serverInfo": {"name": "chat-export-mcp", "version": VERSION}}
    elif m == "tools/list":
        res = {"tools": TOOLS}
    elif m == "tools/call":
        p = req.get("params") or {}
        try:
            out = HANDLERS[p["name"]](p.get("arguments") or {})
            res = {"content": [{"type": "text", "text": json.dumps(out, ensure_ascii=False)}]}
        except Exception as e:
            res = {"content": [{"type": "text", "text": f"error: {e}"}], "isError": True}
    elif m == "ping":
        res = {}
    elif rid is None:
        return None
    else:
        return {"jsonrpc": "2.0", "id": rid, "error": {"code": -32601, "message": f"unknown method {m}"}}
    return {"jsonrpc": "2.0", "id": rid, "result": res}


def main():
    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue
        try:
            resp = handle(json.loads(line))
        except Exception as e:
            resp = {"jsonrpc": "2.0", "id": None, "error": {"code": -32700, "message": str(e)}}
        if resp is not None:
            sys.stdout.write(json.dumps(resp, ensure_ascii=False) + "\n")
            sys.stdout.flush()


if __name__ == "__main__":
    main()
