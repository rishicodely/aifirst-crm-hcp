import { useSelector } from "react-redux";
import axios from "axios";

function InteractionForm() {
  const data = useSelector((state) => state.interaction);

  const fieldStyle = { marginBottom: "12px" };

  return (
    <div>
      <h2 style={{ marginBottom: "20px" }}>
        Interaction Summary (AI Controlled)
      </h2>

      <div style={fieldStyle}>
        <strong>HCP:</strong> {data.hcp_name || "—"}
      </div>

      <div style={fieldStyle}>
        <strong>Type:</strong> {data.interaction_type || "—"}
      </div>

      <div style={fieldStyle}>
        <strong>Date:</strong> {data.date || "—"}
      </div>

      <div style={fieldStyle}>
        <strong>Time:</strong> {data.time || "—"}
      </div>

      <div style={fieldStyle}>
        <strong>Sentiment:</strong> {data.sentiment || "—"}
      </div>

      <div style={fieldStyle}>
        <strong>Topics:</strong>{" "}
        {data.topics?.length ? data.topics.join(", ") : "—"}
      </div>

      <div style={fieldStyle}>
        <strong>Materials:</strong>{" "}
        {data.materials_shared?.length ? data.materials_shared.join(", ") : "—"}
      </div>

      <div style={fieldStyle}>
        <strong>Attendees:</strong>{" "}
        {data.attendees?.length ? data.attendees.join(", ") : "—"}
      </div>

      <button
        style={{
          marginTop: "20px",
          padding: "10px",
          background: "#2563eb",
          border: "none",
          color: "white",
          borderRadius: "6px",
          cursor: "pointer",
        }}
        onClick={async () => {
          await axios.post("http://127.0.0.1:8000/save", data);
          alert("Saved!");
        }}
      >
        Save Interaction
      </button>
    </div>
  );
}

export default InteractionForm;
