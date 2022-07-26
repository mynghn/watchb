import { Routes, Route } from "react-router-dom";
import NavBar from "./components/NavBar";
import Home from "./pages/Home";
import Profile from "./pages/account/Profile";
import BottomBar from "./components/BottomBar";
import { useSelector } from "react-redux";

const NAV_BAR_HEIGHT = "62px";
const BOTTOM_BAR_HEIGHT = "62px";
const BOTTOM_BAR_FONTSIZE = "19px";

function App() {
  const { isAuthenticated, username } = useSelector((state) => state.auth);
  return (
    <div className="App">
      <NavBar
        height={NAV_BAR_HEIGHT}
        isAuthenticated={isAuthenticated}
        username={username}
      />
      <div className="Body bg-light">
        <Routes>
          <Route path="" element={<Home />}></Route>
          <Route path="users/:userId" element={<Profile />}></Route>
        </Routes>
      </div>
      <BottomBar height={BOTTOM_BAR_HEIGHT} fontsize={BOTTOM_BAR_FONTSIZE} />
    </div>
  );
}

export default App;
