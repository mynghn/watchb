import Navbar from "react-bootstrap/Navbar";
import Container from "react-bootstrap/Container";

export default function BottomBar({ height, fontsize }) {
  const totalRatings = 665645731;
  return (
    <Navbar fixed="bottom" bg="dark" variant="dark" style={{ height }}>
      <Container className="justify-content-center align-items-center">
        <Navbar.Brand sytle={{ color: "#d1d1d2", fontsize: fontsize }}>
          {"지금까지 "}
          <em style={{ color: "#ff0558", "font-style": "normal" }}>
            {`★ ${totalRatings.toLocaleString()} 개의 평가가 `}
          </em>
          {"쌓였어요."}
        </Navbar.Brand>
      </Container>
    </Navbar>
  );
}
