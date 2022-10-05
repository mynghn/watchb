import { useLocation, useNavigate } from "react-router-dom";
import Card from "react-bootstrap/Card";
import ListGroup from "react-bootstrap/ListGroup";

import UserSettingsModal from "../../components/UserSettingsModal";
import { useSelector } from "react-redux";

export default function Profile() {
  const navigate = useNavigate();
  const { username, profile, avatar, background } = useSelector(
    ({ auth: { user } }) => user
  );
  const { pathname } = useLocation();

  return (
    <Card style={{ width: "638px" }}>
      <UserSettingsModal />
      <Card.Img variant="top" src={background || "asf"} />
      <Card.Body>
        <Card.Img src={avatar || "asf"} />
        <Card.Title>{username}</Card.Title>
        <Card.Text>{profile || "프로필이 없습니다."}</Card.Text>
      </Card.Body>
      <ListGroup className="list-group-flush">
        <ListGroup.Item>취향분석</ListGroup.Item>
      </ListGroup>
      <Card
        onClick={() => {
          navigate(`${pathname}/contents/movies`);
        }}
      >
        <Card.Img></Card.Img>
        <Card.Body>
          <Card.Title>영화</Card.Title>
          <Card.Subtitle>★447</Card.Subtitle>
          <Card.Text>보고싶어요 287</Card.Text>
        </Card.Body>
      </Card>
    </Card>
  );
}
