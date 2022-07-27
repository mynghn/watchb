import { Routes, Route } from "react-router-dom";
import { useEffect } from "react";

import NavBar from "./components/NavBar";
import Home from "./pages/Home";
import Profile from "./pages/account/Profile";
import BottomBar from "./components/BottomBar";
import { useDispatch, useSelector } from "react-redux";
import { refreshJWT, retrieveUser } from "./api";
import { login, setUser } from "./store";

const NAV_BAR_HEIGHT = "62px";
const BOTTOM_BAR_HEIGHT = "62px";
const BOTTOM_BAR_FONTSIZE = "19px";

function WatchB() {
  const { isAuthenticated, username } = useSelector((state) => state.auth);
  const dispatch = useDispatch();

  const silentLogin = () => {
    refreshJWT()
      .then(retrieveUser)
      .then(({ data: { id: userId, username } }) => {
        dispatch(setUser({ userId, username }));
        dispatch(login());
      });
  };
  useEffect(silentLogin, []);
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
          <Route path="users/:username" element={<Profile />}></Route>
        </Routes>
      </div>
      <BottomBar height={BOTTOM_BAR_HEIGHT} fontsize={BOTTOM_BAR_FONTSIZE} />
    </div>
  );
}

export default WatchB;
