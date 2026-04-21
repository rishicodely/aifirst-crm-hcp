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

    let updates = {};
    try {
      const res = await axios.post("http://127.0.0.1:8000/chat", {
        message: userInput,
        form_state: formState,
      });
      updates = res.data.formUpdates || {};
    } catch (err) {
      dispatch(
        addMessage({
          role: "assistant",
          text: `Error: ${err.message}`,
        }),
      );
      return;
    }

    const cleanUpdates = Object.fromEntries(
      Object.entries(updates).filter(([, v]) => v !== null && v !== undefined),
    );

    if (Object.keys(cleanUpdates).length) {
      dispatch(updateFields(cleanUpdates));
    }

    let message = "";

    if (cleanUpdates.hcp_name) message += `HCP set to ${cleanUpdates.hcp_name}. `;
    if (cleanUpdates.interaction_type) message += `Interaction type set. `;
    if (cleanUpdates.date) message += `Date updated. `;
    if (cleanUpdates.time) message += `Time updated. `;
    if (cleanUpdates.sentiment) message += `Sentiment → ${cleanUpdates.sentiment}. `;
    if (cleanUpdates.topics?.length) message += `Topics added. `;
    if (cleanUpdates.materials_shared?.length) message += `Materials recorded. `;
    if (cleanUpdates.attendees?.length) message += `Attendees recorded. `;

    if (!message) message = "Updated successfully.";

    dispatch(
      addMessage({
        role: "assistant",
        text: message,
      }),
    );
  };

  const handleKeyDown = (e) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  };

  return (
    <div style={{ display: "flex", flexDirection: "column", height: "100%" }}>
      <h2 style={{ marginBottom: "10px" }}>Chat</h2>

      {/* Messages */}
      <div
        style={{
          flex: 1,
          overflowY: "auto",
          paddingBottom: "10px",
        }}
      >
        {messages.map((msg, i) => (
          <div
            key={i}
            style={{
              background: msg.role === "user" ? "#2563eb" : "#1e293b",
              padding: "8px",
              margin: "6px 0",
              borderRadius: "8px",
            }}
          >
            <b>{msg.role}:</b> {msg.text}
          </div>
        ))}
      </div>

      {/* Input */}
      <div style={{ display: "flex", gap: "8px" }}>
        <input
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder="Type message..."
          style={{
            flex: 1,
            padding: "10px",
            background: "#1e293b",
            border: "none",
            color: "white",
            borderRadius: "6px",
          }}
        />
        <button
          onClick={sendMessage}
          style={{
            padding: "10px",
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
