import { useParams, useNavigate } from "react-router-dom";
import { useDispatch } from "react-redux";
import Button from "react-bootstrap/Button";

import { axios, deleteRefreshTokenCookie } from "../../api";
import { logout as reduxLogout } from "../../store";

export default function Profile() {
  const { username } = useParams();
  const navigate = useNavigate();
  const dispatch = useDispatch();

  const logout = () => {
    deleteRefreshTokenCookie();
    delete axios.defaults.headers.common["Authorization"];
    dispatch(reduxLogout());
  };

  return (
    <div>
      User {username}'s Profile{" "}
      <Button
        onClick={() => {
          logout();
          navigate("/");
        }}
      >
        로그아웃
      </Button>
    </div>
  );
}
