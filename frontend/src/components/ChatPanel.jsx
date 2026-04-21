import { useState } from "react";
import { useDispatch, useSelector } from "react-redux";
import axios from "axios";
import { updateFields } from "../features/interactionSlice";
import { addMessage } from "../features/chatSlice";

function ChatPanel() {
  const [input, setInput] = useState("");
  const dispatch = useDispatch();
  const formState = useSelector((state) => state.interaction);
  const messages = useSelector((state) => state.chat.messages);

  const sendMessage = async () => {
    if (!input.trim()) return;

    const userInput = input;
    dispatch(addMessage({ role: "user", text: userInput }));
    setInput("");

    try {
      const res = await axios.post("http://127.0.0.1:8000/chat", {
        message: userInput,
        form_state: formState,
      });

      const updates = res.data.formUpdates || {};
      const assistantMessage = res.data.assistantMessage || "Done.";
      const toolsUsed = res.data.toolsUsed || [];

      if (Object.keys(updates).length) {
        dispatch(updateFields(updates));
      }

      dispatch(
        addMessage({
          role: "assistant",
          text: assistantMessage,
          tool: toolsUsed.join(", "),
        }),
      );
    } catch (err) {
      dispatch(
        addMessage({
          role: "assistant",
          text: `Error: ${err.message}`,
        }),
      );
    }
  };

  const handleKeyDown = (e) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  };

  return (
    <div style={{ display: "flex", flexDirection: "column", height: "100%" }}>
      {/* Header */}
      <h2 style={{ marginBottom: "10px", fontWeight: "600" }}>
        Chat Assistant
      </h2>

      {/* Messages Box */}
      <div
        style={{
          flex: 1,
          overflowY: "auto",
          padding: "12px",
          border: "1px solid #e5e7eb",
          borderRadius: "8px",
          background: "#fafafa",
          marginBottom: "12px",
        }}
      >
        {messages.length === 0 && (
          <div style={{ color: "#6b7280", fontSize: "14px" }}>
            Start typing to log or edit an interaction...
          </div>
        )}

        {messages.map((msg, i) => (
          <div
            key={i}
            style={{
              display: "flex",
              justifyContent: msg.role === "user" ? "flex-end" : "flex-start",
              marginBottom: "8px",
            }}
          >
            <div
              style={{
                maxWidth: "70%",
                background: msg.role === "user" ? "#2563eb" : "#ffffff",
                color: msg.role === "user" ? "white" : "#111827",
                padding: "10px",
                borderRadius: "10px",
                border: msg.role === "assistant" ? "1px solid #e5e7eb" : "none",
              }}
            >
              <div>{msg.text}</div>

              {msg.tool && (
                <div
                  style={{
                    fontSize: "11px",
                    marginTop: "4px",
                    color: "#6b7280",
                  }}
                >
                  [{msg.tool}]
                </div>
              )}
            </div>
          </div>
        ))}
      </div>

      {/* Input */}
      <div
        style={{
          display: "flex",
          gap: "8px",
          borderTop: "1px solid #e5e7eb",
          paddingTop: "10px",
        }}
      >
        <input
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder="Type message..."
          style={{
            flex: 1,
            padding: "10px",
            border: "1px solid #e5e7eb",
            borderRadius: "6px",
            outline: "none",
          }}
        />

        <button
          onClick={sendMessage}
          style={{
            padding: "10px 16px",
            background: "#2563eb",
            border: "none",
            color: "white",
            borderRadius: "6px",
            cursor: "pointer",
          }}
        >
          Send
        </button>
      </div>
    </div>
  );
}

export default ChatPanel;
