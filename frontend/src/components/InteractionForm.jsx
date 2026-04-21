import { useSelector, useDispatch } from "react-redux";
import axios from "axios";
import { resetForm } from "../features/interactionSlice";

function InteractionForm() {
  const data = useSelector((state) => state.interaction);
  const dispatch = useDispatch();

  const inputStyle = {
    width: "100%",
    padding: "8px",
    border: "1px solid #e5e7eb",
    borderRadius: "6px",
    marginBottom: "12px",
    background: "#f9fafb",
  };

  return (
    <div>
      <h2 style={{ marginBottom: "20px", color: "#111827" }}>
        Log Interaction (AI Controlled)
      </h2>

      {/* HCP */}
      <input
        style={inputStyle}
        placeholder="Search or select HCP"
        value={data.hcp_name || ""}
        disabled
      />

      {/* Type */}
      <select style={inputStyle} value={data.interaction_type || ""} disabled>
        <option value="">Select interaction type</option>
        <option value="meeting">Meeting</option>
        <option value="call">Call</option>
        <option value="email">Email</option>
      </select>

      {/* Date */}
      <input type="date" style={inputStyle} value={data.date || ""} disabled />

      {/* Time */}
      <input type="time" style={inputStyle} value={data.time || ""} disabled />

      {/* Sentiment */}
      <input
        style={inputStyle}
        placeholder="Sentiment"
        value={data.sentiment || ""}
        disabled
      />

      {/* Topics */}
      <textarea
        style={inputStyle}
        placeholder="Topics discussed"
        value={data.topics?.join(", ") || ""}
        disabled
      />

      {/* Materials */}
      <textarea
        style={inputStyle}
        placeholder="Materials shared"
        value={data.materials_shared?.join(", ") || ""}
        disabled
      />

      {/* Attendees */}
      <textarea
        style={inputStyle}
        placeholder="Attendees"
        value={data.attendees?.join(", ") || ""}
        disabled
      />

      <button
        style={{
          marginTop: "10px",
          padding: "10px",
          background: "#2563eb",
          border: "none",
          color: "white",
          borderRadius: "6px",
          cursor: "pointer",
          width: "100%",
        }}
        onClick={async () => {
          await axios.post("http://127.0.0.1:8000/save", data);
          alert("Saved!");
          dispatch(resetForm());
        }}
      >
        Save Interaction
      </button>
    </div>
  );
}

export default InteractionForm;
