import { useEffect, useState } from "react";
import DropdownButton from "react-bootstrap/DropdownButton";
import Dropdown from "react-bootstrap/Dropdown";
import { StarFill, StarHalf } from "react-bootstrap-icons";

// TODO: 호버 시 변하는 별점 형태로 바꾸기
export default function RatingStars() {
  const [starsOption, setStarsOption] = useState([]);
  useEffect(() => {
    const toStarsRating = (ratingIdx) => {
      let stars = Array(parseInt(ratingIdx / 2)).fill(<StarFill />);
      if (ratingIdx % 2 !== 0) {
        stars.push(<StarHalf />);
      }
      console.log(stars);
      return stars;
    };
    for (let idx = 1; idx <= 10; idx++) {
      setStarsOption((prevState) => [...prevState, toStarsRating(idx)]);
    }
    return () => setStarsOption([]);
  }, []);
  return (
    <DropdownButton title="평가하기">
      {starsOption.map((opt, idx) => (
        <Dropdown.Item eventKey={idx}>{opt}</Dropdown.Item>
      ))}
    </DropdownButton>
  );
}
