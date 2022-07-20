import { Link } from "react-router-dom";

function Logo(params) {
  return <Link to="">watchb logo</Link>;
}

function SearchBox(params) {
  return <form>Search</form>;
}

function LoginButton(params) {
  return <button>Login</button>;
}

function SignUpButton(params) {
  return <button>Sign Up</button>;
}

function ReviewLink(params) {
  return <Link to="/review">Review</Link>;
}

function AvatarLink({ userId, imgLink }) {
  return (
    <Link to={`/users/${userId}`}>
      <img src={imgLink} alt="User avatar" />
    </Link>
  );
}

export default function NavBar() {
  return "Navigation Bar";
}
