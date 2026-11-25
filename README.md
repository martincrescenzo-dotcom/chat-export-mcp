# chat-export-mcp

Zero-dependency **MCP server** that lets Claude Desktop, Cursor, or any MCP client read your **local chat exports**: WhatsApp `.txt`, Telegram Desktop `result.json`, DiscordChatExporter `.json`. One Python file, standard library only, offline. Nothing is uploaded.

Ask your agent things like "summarize what Bob said about the deposit in this WhatsApp export", "find every message mentioning 'invoice'", or "who sent the most messages and when did the chat start".

Need the chat as a PDF (for a lawyer, HR, insurer or court file)? [ChatExhibit](https://martincrescenzo-dotcom.github.io/chatexhibit/) makes one in your browser from the same export: free chat-style PDF, or a numbered, hashed Exhibit edition for EUR 9 one-time.

## Tools
- `read_chat_export(path, query?, sender?, offset?, limit?)`: numbered messages (date, sender, text), keyword/sender filter, paging, plus the SHA-256 of the file.
- `chat_export_stats(path)`: messages per sender, first/last date, SHA-256.
- `export_chat_html(path, output?)`: writes a printable HTML transcript (numbered messages, SHA-256) next to the export; open it and Print > Save as PDF. For an evidence-ready PDF with cover sheet and page numbers, use [ChatExhibit](https://martincrescenzo-dotcom.github.io/chatexhibit/) (€9).

## Install
One-click: download [chat-export-mcp.mcpb](https://github.com/martincrescenzo-dotcom/chat-export-mcp/releases/latest/download/chat-export-mcp.mcpb) and open it in Claude Desktop. Or with [uv](https://docs.astral.sh/uv/) (no clone):
```json
{"mcpServers": {"chat-export": {"command": "uvx", "args": ["--from", "git+https://github.com/martincrescenzo-dotcom/chat-export-mcp", "chat-export-mcp"]}}}
```
Or manually:
```bash
curl -O https://raw.githubusercontent.com/martincrescenzo-dotcom/chat-export-mcp/main/chat_export_mcp.py
```
Claude Desktop (`claude_desktop_config.json`) or Cursor (`.cursor/mcp.json`):
```json
{"mcpServers": {"chat-export": {"command": "python3", "args": ["/full/path/to/chat_export_mcp.py"]}}}
```

## Need a PDF for a lawyer, HR, or court?
[ChatExhibit](https://martincrescenzo-dotcom.github.io/chatexhibit/) turns the same exports into a PDF in your browser. Free: chat-style PDF. **Exhibit edition (EUR 9 one-time):** numbered transcript with exhibit label, SHA-256 of the export, date/keyword/sender excerpts with visible gaps, no branding. Agents can find purchase details in its [llms.txt](https://martincrescenzo-dotcom.github.io/chatexhibit/llms.txt). Not legal advice.

See also: [whatsapp-chat-to-pdf](https://github.com/martincrescenzo-dotcom/whatsapp-chat-to-pdf) · [telegram-chat-to-pdf](https://github.com/martincrescenzo-dotcom/telegram-chat-to-pdf) · [discord-chat-to-pdf](https://github.com/martincrescenzo-dotcom/discord-chat-to-pdf)

MCP Registry name: `mcp-name: io.github.martincrescenzo-dotcom/chat-export-mcp`

MIT License.
