import { Link } from "react-router-dom";
import Navbar from "react-bootstrap/Navbar";
import Container from "react-bootstrap/Container";
import Form from "react-bootstrap/Form";
import Button from "react-bootstrap/Button";

function BrandLogo({ imgSrc, imgWidth, imgHeight }) {
  return (
    <Link to="">
      <img src={imgSrc} width={imgWidth} height={imgHeight} alt="WatchB logo" />
    </Link>
  );
}
const LOGO_IMAGE_WIDTH = "151px";
const LOGO_IMAGE_HEIGHT = "29px";

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

function LoginButton() {
  return <Button>로그인</Button>;
}

function SignUpButton() {
  return <Button>회원가입</Button>;
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

export default function NavBar({ height }) {
  const userId = 1;
  const isAuthenticated = true;
  return (
    <Navbar sticky="top" bg="white" variant="dark" style={{ height }}>
      <Container fluid className="align-items-center">
        <BrandLogo imgWidth={LOGO_IMAGE_WIDTH} imgHeight={LOGO_IMAGE_HEIGHT} />
        <SearchForm />
        {isAuthenticated ? <ReviewLink /> : <LoginButton />}
        {isAuthenticated ? (
          <AvatarLink userId={userId} imgSize={AVATAR_SIZE} />
        ) : (
          <SignUpButton />
        )}
      </Container>
    </Navbar>
  );
}
