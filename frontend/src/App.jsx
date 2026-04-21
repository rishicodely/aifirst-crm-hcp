import InteractionForm from "./components/InteractionForm";
import ChatPanel from "./components/ChatPanel";

function App() {
  return (
    <div
      style={{
        display: "flex",
        height: "100vh",
        backgroundColor: "#0f172a",
        color: "white",
        fontFamily: "Inter, sans-serif",
      }}
    >
      <div
        style={{
          flex: 1,
          padding: "32px",
          borderRight: "1px solid #1e293b",
          display: "flex",
          flexDirection: "column",
          justifyContent: "center",
        }}
      >
        <InteractionForm />
      </div>

      <div
        style={{
          flex: 1,
          padding: "32px",
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
