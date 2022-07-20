import { Routes, Route } from "react-router-dom";
import Home from "./pages/Home";
import Profile from "./pages/account/Profile";

function App() {
  return (
    <div className="App">
      <Routes>
        <Route path="/" element={<Home />}></Route>
        <Route path="users/:userId" element={<Profile />}></Route>
      </Routes>
    </div>
  );
}

export default App;
