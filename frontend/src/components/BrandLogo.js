import { Link } from "react-router-dom";

export default function BrandLogo({ imgSrc, imgWidth, imgHeight }) {
  return (
    <Link to="">
      <img src={imgSrc} width={imgWidth} height={imgHeight} alt="WatchB logo" />
    </Link>
  );
}
