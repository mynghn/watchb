import { Routes, Route } from "react-router-dom";
import NavBar from "./components/NavBar";
import Home from "./pages/Home";
import Profile from "./pages/account/Profile";
import BottomBar from "./components/BottomBar";

function App() {
  return (
    <div className="App">
      <div className="NavBar">
        <NavBar />
      </div>
      <div className="Body">
        <Routes>
          <Route path="" element={<Home />}></Route>
          <Route path="users/:userId" element={<Profile />}></Route>
        </Routes>
      </div>
      <div className="BottomBar">
        <BottomBar />
      </div>
    </div>
  );
}

export default App;
