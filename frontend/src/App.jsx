import "./App.css";

function App() {
  return (
    <div className="App">
      <div>Welcome to Brickly! {'->'} {import.meta.env.VITE_BACKEND_URL}</div>
    </div>
  );
}

export default App;
