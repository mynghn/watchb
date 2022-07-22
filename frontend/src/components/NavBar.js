import { Link } from "react-router-dom";
import Navbar from "react-bootstrap/Navbar";
import Container from "react-bootstrap/Container";
import Form from "react-bootstrap/Form";

import BrandLogo from "./BrandLogo";
import LoginModal from "./LoginModal";
import SignUpModal from "./SignUpModal";

function SearchForm() {
  return (
    <Form>
      <Form.Control
        type="search"
        placeholder="영화, 인물, 컬렉션, 유저를 검색해보세요."
      />
    </Form>
  );
}

function ReviewLink() {
  return <Link to="/review">평가하기</Link>;
}

function AvatarLink({ userId, imgSrc, imgSize }) {
  return (
    <Link to={`users/${userId}`}>
      <img src={imgSrc} alt="User avatar" width={imgSize} height={imgSize} />
    </Link>
  );
}
const AVATAR_SIZE = "28px";

const LOGO_IMAGE_WIDTH = "151px";
const LOGO_IMAGE_HEIGHT = "29px";

export default function NavBar({ height }) {
  const userId = 1;
  const isAuthenticated = true;
  return (
    <Navbar sticky="top" bg="white" variant="dark" style={{ height }}>
      <Container fluid className="align-items-center">
        <BrandLogo imgWidth={LOGO_IMAGE_WIDTH} imgHeight={LOGO_IMAGE_HEIGHT} />
        <SearchForm />
        {isAuthenticated ? <ReviewLink /> : <LoginModal />}
        {isAuthenticated ? (
          <AvatarLink userId={userId} imgSize={AVATAR_SIZE} />
        ) : (
          <SignUpModal />
        )}
      </Container>
    </Navbar>
  );
}
