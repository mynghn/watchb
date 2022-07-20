import { useParams } from "react-router-dom";

export default function Profile() {
  const { userId } = useParams();
  return <div>User {userId}'s Profile</div>;
}
