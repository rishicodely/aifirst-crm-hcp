import InteractionForm from "./components/InteractionForm";
import ChatPanel from "./components/ChatPanel";

function App() {
  return (
    <div
      style={{
        display: "flex",
        height: "100vh",
        backgroundColor: "#ffffff",
        color: "#111827",
        fontFamily: "Inter, sans-serif",
      }}
    >
      {/* LEFT PANEL */}
      <div
        style={{
          flex: 1,
          padding: "40px",
          borderRight: "1px solid #e5e7eb",
          display: "flex",
          flexDirection: "column",
          justifyContent: "flex-start",
          paddingTop: "40px",
        }}
      >
        <InteractionForm />
      </div>

      {/* RIGHT PANEL */}
      <div
        style={{
          flex: 1,
          padding: "40px",
          display: "flex",
          flexDirection: "column",
        }}
      >
        <ChatPanel />
      </div>
    </div>
  );
}

export default App;
